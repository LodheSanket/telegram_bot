
import logging
import os
import re

import httpx
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
DJANGO_API_URL = os.environ.get("DJANGO_API_URL")
SECRET_API_KEY = os.environ.get("SECRET_API_KEY")


EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

ROLE_DISPLAY_NAMES = {
    "frontend": "Frontend Developer",
    "backend": "Backend Developer",
    "angular": "Angular Developer",
    "fullstack": "Full Stack Developer",
}


pending_emails: dict[int, str] = {}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def is_valid_email(text: str) -> bool:
    """Checks whether a string looks like a valid email address."""
    return bool(EMAIL_REGEX.match(text.strip()))


def build_role_keyboard() -> InlineKeyboardMarkup:
    """
    Builds the inline keyboard shown after a valid email is received.
    Each button's callback_data is the role key, so the callback
    handler knows which role was picked without any extra parsing.
    """
    buttons = [
        InlineKeyboardButton(display_name, callback_data=role_key)
        for role_key, display_name in ROLE_DISPLAY_NAMES.items()
    ]
    # One button per row keeps this readable on narrow phone screens.
    keyboard_rows = [[button] for button in buttons]
    return InlineKeyboardMarkup(keyboard_rows)


async def submit_application(email: str, role: str) -> tuple[bool, str]:
    """
    Sends the application to the Django API and returns a tuple of
    (success, message). Keeping this separate from the Telegram
    handlers means the HTTP logic can be tested or reused on its own.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            logger.info(f"Bot SECRET_API_KEY: {repr(SECRET_API_KEY)}")
            logger.info(f"Bot DJANGO_API_URL: {repr(DJANGO_API_URL)}")
            print(f"Bot SECRET_API_KEY: {repr(SECRET_API_KEY)}")
            print(f"Bot DJANGO_API_URL: {repr(DJANGO_API_URL)}")
            response = await client.post(
                DJANGO_API_URL,
                json={"email": email, "role": role},
                headers={"X-API-KEY": SECRET_API_KEY},
            )
    except httpx.RequestError as exc:
        logger.error(f"Could not reach Django API: {exc}")
        return False, "Couldn't reach the application server. Please try again in a bit."

    if response.status_code == 200:
        return True, (
            "Application sent successfully\n"
            f"Email: {email}\n"
            f"Role: {ROLE_DISPLAY_NAMES[role]}"
        )

    print("Status:", response.status_code)
    print("Response:", response.text)
    print("Headers:", response.headers)
    if response.status_code == 401:
        return False, (
            "The bot couldn't authenticate with the API. Check that SECRET_API_KEY "
            "matches on both sides."
        )

    # Try to pull a useful message out of the API's JSON error
    # response, fall back to raw text if it isn't JSON.
    try:
        error_detail = response.json().get("message", response.text)
    except ValueError:
        error_detail = response.text
    return False, f"Application failed: {error_detail}"


async def handle_email_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles any plain text message. If it looks like an email, store
    it for this chat and show the role buttons. Otherwise, explain
    what the bot expects.
    """
    text = update.message.text or ""

    if not is_valid_email(text):
        await update.message.reply_text(
            "Please send a valid HR email address to start an application.\n"
            "Example: hr@company.com"
        )
        return

    email = text.strip()
    chat_id = update.effective_chat.id
    pending_emails[chat_id] = email

    await update.message.reply_text(
        f"Got it: {email}\nWhich role is this for?",
        reply_markup=build_role_keyboard(),
    )


async def handle_role_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handles a tap on one of the role buttons. Looks up the email
    stored for this chat, then sends the application.
    """
    query = update.callback_query
    chat_id = update.effective_chat.id
    role = query.data

    # Acknowledge the tap right away so Telegram doesn't show a
    # loading spinner on the button while we wait for the API call.
    await query.answer()

    email = pending_emails.get(chat_id)
    if not email:
        await query.edit_message_text(
            "I don't have an email on file for this chat anymore. "
            "Please send the email address again."
        )
        return

    await query.edit_message_text(f"Sending your application for {ROLE_DISPLAY_NAMES[role]}...")

    success, message = await submit_application(email, role)
    await query.message.reply_text(message)

    # Clear the pending email whether it succeeded or failed, so a
    # stale email can't accidentally get reused for a different role.
    pending_emails.pop(chat_id, None)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles /start, explaining how to use the bot."""
    await update.message.reply_text(
        "Hi! To apply, just send me an HR email address.\n"
        "Example: hr@company.com\n\n"
        "I'll show you role options to choose from after that."
    )


def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set. Check your .env file.")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start_command))
    # Any non-command text message is treated as a potential email.
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email_message)
    )
    # Button taps come through as callback queries, not messages.
    application.add_handler(CallbackQueryHandler(handle_role_selection))

    logger.info("Bot is starting...")
    application.run_polling()


if __name__ == "__main__":
    main()