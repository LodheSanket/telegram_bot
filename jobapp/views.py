from django.http import HttpResponse


def home(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Telegram Bot API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f7fb;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }

            .card {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                text-align: center;
                max-width: 600px;
            }

            h1 {
                color: #2c3e50;
            }

            p {
                color: #555;
                font-size: 18px;
            }

            .badge {
                display: inline-block;
                margin-top: 20px;
                padding: 10px 20px;
                background: #28a745;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🤖 Telegram Job Bot</h1>
            <p>Welcome! Your Django application is running successfully on Render.</p>
            <div class="badge">Status: Online ✅</div>
        </div>
    </body>
    </html>
    """)