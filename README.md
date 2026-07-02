# Telegram Job Application Bot

Send a Telegram command with a job role and an email address, and this
sends out a job application email with the right resume attached.

## How it fits together

```
Telegram User -> Telegram Bot -> Django REST API -> SMTP Server -> Recipient Email
```

The Telegram bot and the Django API are two separate processes. The
bot listens for messages on Telegram and, when it sees a valid
`/apply` command, makes an HTTP request to the Django API. The API
checks the request, picks the right resume and email template, sends
the email over SMTP, and logs the result. They talk to each other
only over HTTP, using a shared API key for authentication.

## Project layout

```
job_application_bot/
├── manage.py
├── jobapp/              Django project settings, root URLs, wsgi/asgi
├── api/                 The REST API: model, serializer, view, auth, admin
├── services/            Shared logic: email sending, templates, resume mapping
├── bot/                 The standalone Telegram bot script
├── resumes/             Resume PDFs go here (not in the database)
├── logs/                application.log gets written here at runtime
├── .env.example
├── requirements.txt
└── Procfile
```

## 1. Setup

```bash
python -m venv venv
source venv/bin/activate          # venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env
# now edit .env with your real values, see below
```

### Environment variables

| Variable | What it's for |
|---|---|
| `DJANGO_SECRET_KEY` | Django's internal secret, generate a random string |
| `DJANGO_DEBUG` | `True` locally, `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames, add your production domain here |
| `SECRET_API_KEY` | The shared key the bot sends as `X-API-KEY`. Must match on both sides |
| `SMTP_HOST` / `SMTP_PORT` | Your email provider's SMTP server, e.g. `smtp.gmail.com` / `587` |
| `SMTP_EMAIL` / `SMTP_PASSWORD` | The sending account. For Gmail, use an App Password, not your normal password |
| `SMTP_USE_TLS` | `True` for Gmail on port 587 |
| `TELEGRAM_BOT_TOKEN` | From [@BotFather](https://t.me/BotFather) on Telegram |
| `WHATSAPP_PORT` | Optional port for the WhatsApp webhook listener, default `8001` |
| `DJANGO_API_URL` | Where the bot sends requests, e.g. `http://127.0.0.1:8000/api/apply/` locally |

#### Getting a Gmail App Password

1. Turn on 2-Step Verification on the Gmail account.
2. Go to Google Account > Security > App Passwords.
3. Generate one for "Mail" and use that 16-character value as `SMTP_PASSWORD`.

#### Getting a Telegram bot token

1. Message [@BotFather](https://t.me/BotFather) on Telegram.
2. Send `/newbot` and follow the prompts.
3. Copy the token it gives you into `TELEGRAM_BOT_TOKEN`.

### Add your resumes

Drop these four files into `resumes/`:

```
resumes/frontend.pdf
resumes/backend.pdf
resumes/angular.pdf
resumes/fullstack.pdf
```

If you want different roles or filenames, edit `RESUME_MAP` in
`services/resume_mapper.py`, everything else (validation, the API,
the bot) reads from that one dictionary.

### Set up the database

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, lets you view ApplicationHistory in /admin/
```

## 2. Running it locally

You need two terminals open at the same time, since the bot and the
API are separate processes.

**Terminal 1, the Django API:**
```bash
python manage.py runserver
```

**Terminal 2, the Telegram bot:**
```bash
python bot/telegram_bot.py
```

**Terminal 3, the WhatsApp webhook bot:**
```bash
python bot/whatsapp_bot.py
```

Now message your bot on Telegram or WhatsApp:

```
/apply frontend hr@company.com
```

or

```
apply frontend hr@company.com
```

You should get a confirmation message back, and an email should land
in the recipient's inbox with the frontend resume attached.

## 3. The API

### `POST /api/apply/`

Every request needs this header:
```
X-API-KEY: <your SECRET_API_KEY value>
```

Request body:
```json
{
  "email": "hr@company.com",
  "role": "frontend"
}
```

Valid roles: `frontend`, `backend`, `angular`, `fullstack`

Success response (200):
```json
{
  "success": true,
  "message": "Application sent"
}
```

Error responses:

| Status | Reason |
|---|---|
| 400 | Invalid email format or unrecognized role |
| 401 | Missing or incorrect `X-API-KEY` header |
| 404 | Role is valid but its resume file isn't in `resumes/` |
| 502 | The email couldn't be sent (SMTP connection or auth failure) |

Every attempt, successful or not, gets saved to the `ApplicationHistory`
table and written to `logs/application.log`.

## 4. Deployment

The Django API and the Telegram bot need to run as two separate
services in production, since the bot uses long-polling and needs to
stay running continuously, while the API just needs to be reachable
over HTTP.

### Render

1. Push this project to a GitHub repo.
2. In Render, create a **Web Service** from that repo:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn jobapp.wsgi --log-file -`
   - Add all the environment variables from `.env.example` in the
     Render dashboard, except set `DJANGO_API_URL` to this service's
     own Render URL plus `/api/apply/` (you'll get the URL after the
     first deploy).
3. Create a second service from the same repo, this time a
   **Background Worker**:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python bot/telegram_bot.py`
   - Add the same environment variables, `DJANGO_API_URL` here should
     point at the Web Service's URL from step 2.
4. Make sure `DJANGO_ALLOWED_HOSTS` includes the Render web service's
   domain.

### Railway

1. Push this project to a GitHub repo.
2. In Railway, create a new project from that repo. Railway will
   detect Python and the `Procfile` automatically.
3. Add a service for `web` (the Django API) and a separate service
   for `worker` (the bot), Railway lets you pick which Procfile
   process each service runs.
4. Add the environment variables from `.env.example` to both
   services. For the worker, set `DJANGO_API_URL` to the public URL
   Railway assigns the web service.
5. Update `DJANGO_ALLOWED_HOSTS` to include the Railway-assigned
   domain.

### A note on SQLite in production

SQLite works fine for getting this running, but most hosting
platforms use ephemeral or read-only filesystems for deployed code,
which means the SQLite file (and your logs) may not persist across
deploys or restarts. If you need application history to actually
stick around long-term, swap in Postgres (Render and Railway both
offer it as an add-on) by changing the `DATABASES` setting in
`jobapp/settings.py`.

## 5. What's been tested

This project was run end-to-end before being handed over: Django's
system check, migrations, and a full request cycle through
`/api/apply/` covering a successful send with the resume actually
attached, a missing API key, a wrong API key, an invalid role, an
invalid email, and a missing resume file. All of them returned the
expected status codes and were recorded correctly in
`ApplicationHistory` and `logs/application.log`.
