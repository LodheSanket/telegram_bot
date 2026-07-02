"""
Standalone WhatsApp bot webhook listener.

This script listens for incoming WhatsApp messages from a provider like
Twilio and forwards valid application commands to the Django API over HTTP.
Run it with:
    python bot/whatsapp_bot.py

It expects environment variables in .env, including:
    DJANGO_API_URL  - the same API URL the Telegram bot uses
    SECRET_API_KEY  - shared API key for /api/apply/
    WHATSAPP_PORT   - optional HTTP port (default: 8001)

The incoming message should look like:
    apply frontend hr@company.com
or:
    frontend hr@company.com

The script replies with a text response that Twilio will forward back to
WhatsApp.
"""

import html
import logging
import os
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

import httpx
from dotenv import load_dotenv


ROLE_DISPLAY_NAMES = {
    "frontend": "Frontend Developer",
    "backend": "Backend Developer",
    "angular": "Angular Developer",
    "fullstack": "Full Stack Developer",
}
load_dotenv()

DJANGO_API_URL = os.environ.get("DJANGO_API_URL", "http://127.0.0.1:8000/api/apply/")
SECRET_API_KEY = os.environ.get("SECRET_API_KEY")
WHATSAPP_HOST = os.environ.get("WHATSAPP_HOST", "0.0.0.0")
WHATSAPP_PORT = int(os.environ.get("WHATSAPP_PORT", "8001"))

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
AVAILABLE_ROLES = ", ".join(ROLE_DISPLAY_NAMES.keys())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def build_help_text() -> str:
    return (
        "Usage: apply <role> <email>\n"
        "Example: apply frontend hr@company.com\n\n"
        f"Available roles: {AVAILABLE_ROLES}"
    )


def parse_command(text: str) -> tuple[str | None, str | None, str | None]:
    text = text.strip()

    if text.startswith("/apply "):
        text = text[len("/apply "):].strip()
    elif text.lower().startswith("apply "):
        text = text[len("apply "):].strip()

    if not text:
        return None, None, build_help_text()

    parts = text.split()
    if len(parts) != 2:
        return None, None, build_help_text()

    role, email = parts[0].lower(), parts[1].strip()

    if role not in ROLE_DISPLAY_NAMES:
        return None, None, (
            f"'{role}' isn't a recognized role.\n"
            f"Available roles: {AVAILABLE_ROLES}"
        )

    if not EMAIL_REGEX.match(email):
        return None, None, f"'{email}' doesn't look like a valid email address."

    return role, email, None


def send_application(role: str, email: str) -> str:
    if not SECRET_API_KEY:
        return "The bot is not configured properly. SECRET_API_KEY is missing."

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                DJANGO_API_URL,
                json={"email": email, "role": role},
                headers={"X-API-KEY": SECRET_API_KEY},
            )

        if response.status_code == 200:
            return (
                "Application sent successfully.\n"
                f"Email: {email}\n"
                f"Role: {ROLE_DISPLAY_NAMES[role]}"
            )
        if response.status_code == 401:
            return (
                "The bot couldn't authenticate with the API. "
                "Check that SECRET_API_KEY matches on both sides."
            )

        try:
            error_detail = response.json().get("message", response.text)
        except ValueError:
            error_detail = response.text
        return f"Application failed: {error_detail}"

    except httpx.RequestError as exc:
        logger.error(f"Could not reach Django API: {exc}")
        return "Couldn't reach the application server. Please try again in a bit."


def build_twiml_response(message: str) -> bytes:
    escaped = html.escape(message)
    xml = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>" "<Response><Message>{escaped}</Message></Response>"
    return xml.encode("utf-8")


class WhatsAppWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/whatsapp":
            self.send_error(404)
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        body_bytes = self.rfile.read(content_length)
        data = parse_qs(body_bytes.decode("utf-8"))

        message_body = data.get("Body", [""])[0].strip()
        logger.info(f"WhatsApp message received: {message_body}")

        role, email, error_message = parse_command(message_body)
        if error_message is not None:
            reply_text = error_message
        else:
            reply_text = send_application(role, email)

        reply_bytes = build_twiml_response(reply_text)
        self.send_response(200)
        self.send_header("Content-Type", "application/xml")
        self.send_header("Content-Length", str(len(reply_bytes)))
        self.end_headers()
        self.wfile.write(reply_bytes)

    def log_message(self, format: str, *args) -> None:
        logger.info("HTTP %s - %s", self.address_string(), format % args)


def main() -> None:
    if not SECRET_API_KEY:
        raise RuntimeError("SECRET_API_KEY is not set. Check your .env file.")

    server_address = (WHATSAPP_HOST, WHATSAPP_PORT)
    httpd = HTTPServer(server_address, WhatsAppWebhookHandler)
    logger.info("WhatsApp webhook listener starting on http://%s:%s/whatsapp", WHATSAPP_HOST, WHATSAPP_PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("WhatsApp webhook listener stopped by user")
        httpd.server_close()


if __name__ == "__main__":
    main()
