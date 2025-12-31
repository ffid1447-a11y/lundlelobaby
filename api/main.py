#!/usr/bin/env python3
"""Professional Email Sender WebUI
Sends emails securely through Gmail SMTP with a modern responsive interface
BRAND LOCKED: encore | frappeash.t.me
"""

import smtplib
import re
from email.message import EmailMessage
from flask import Flask, request, jsonify

# ================= BRAND LOCK =================
BRAND_NAME = "encore"
WATERMARK = "frappeash.t.me"
BRAND_LOCK = f"{BRAND_NAME} | {WATERMARK}"
# ==============================================

# -------- CONFIG --------
SENDER_EMAIL = "rkhakkieva@gmail.com"
APP_PASSWORD = "acee hcmb cvqk iwum"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
MIN_MESSAGE_LENGTH = 5
MAX_MESSAGE_LENGTH = 5000
MAX_SUBJECT_LENGTH = 200
# ------------------------

app = Flask(__name__)
app.secret_key = 'email-sender-secret-key-2024'

# ---------- API RESPONSE ----------
def api_response(success, message=None, error=None, data=None, status_code=200):
    return jsonify({
        'success': success,
        'message': message,
        'error': error,
        'data': data
    }), status_code


def validate_email(email):
    return re.match(r'^[^@]+@[^@]+\.[^@]+$', email)


def validate_input(from_email, to_email, subject, message):
    errors = []
    if not validate_email(from_email):
        errors.append('Invalid sender email')
    if not validate_email(to_email):
        errors.append('Invalid recipient email')
    if not subject:
        errors.append('Subject cannot be empty')
    if len(message) < MIN_MESSAGE_LENGTH:
        errors.append(f'Message must be at least {MIN_MESSAGE_LENGTH} characters')
    return errors


# ---------- EMAIL ----------
class EmailSender:
    def send_email(self, to_email, from_email, subject, message):
        try:
            msg = EmailMessage()
            msg["From"] = f"{from_email} <{SENDER_EMAIL}>"
            msg["To"] = to_email
            msg["Subject"] = subject

            # 🔒 HARD EMAIL WATERMARK (UNREMOVABLE)
            msg.set_content(f"""{message}

-------------------------
Sent via ENCORE
{WATERMARK}
-------------------------
""")

            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.login(SENDER_EMAIL, APP_PASSWORD)
                smtp.send_message(msg)

            return True, None
        except Exception as e:
            return False, str(e)


mailer = EmailSender()

# ---------- UI ----------
@app.route('/')
def index():
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>ENCORE Anonymous Email Sender</title>
<style>
body {{
    background: linear-gradient(135deg,#667eea,#764ba2);
    font-family: Arial;
}}
.box {{
    max-width:800px;
    margin:40px auto;
    background:#fff;
    padding:30px;
    border-radius:20px;
}}
input,textarea,button {{
    width:100%;
    margin-top:10px;
    padding:12px;
}}
button {{
    background:#4f46e5;
    color:white;
    border:none;
    font-size:16px;
}}
.footer {{
    text-align:center;
    margin-top:25px;
    font-size:13px;
    color:#ddd;
}}
.watermark {{
    position:fixed;
    bottom:12px;
    right:18px;
    font-size:12px;
    color:rgba(255,255,255,0.6);
    pointer-events:none;
}}
</style>
</head>
<body>

<div class="box" id="brand-lock">
<h2>ENCORE ANONYMOUS EMAIL SENDER</h2>

<input id="from" placeholder="From Email">
<input id="to" placeholder="To Email">
<input id="subject" placeholder="Subject">
<textarea id="message" placeholder="Minimum 5 characters"></textarea>
<button onclick="sendMail()">Send Email</button>

<p id="status"></p>
</div>

<div class="footer">
Powered by <b>encore</b> • Secure Email Delivery System<br>
{WATERMARK}
</div>

<div class="watermark">{WATERMARK}</div>

<script>
// 🔒 FRONTEND BRAND LOCK
setInterval(() => {{
    if (!document.body.innerText.includes("encore") ||
        !document.body.innerText.includes("{WATERMARK}")) {{
        document.body.innerHTML =
            "<h1 style='text-align:center;color:red;margin-top:20%'>Branding tampered</h1>";
    }}
}}, 1500);

async function sendMail() {{
    const res = await fetch('/send-email', {{
        method:'POST',
        headers:{{'Content-Type':'application/json'}},
        body: JSON.stringify({{
            from:from.value,
            to:to.value,
            subject:subject.value,
            message:message.value
        }})
    }});
    const data = await res.json();
    status.innerText = data.success ? data.message : data.error;
}}
</script>

</body>
</html>"""


# ---------- API ----------
@app.route('/send-email', methods=['POST'])
def send_email():
    if BRAND_NAME not in BRAND_LOCK:
        return api_response(False, error="Brand lock violated", status_code=403)

    data = request.get_json()
    if not data:
        return api_response(False, error="Invalid payload", status_code=400)

    errors = validate_input(
        data.get('from',''),
        data.get('to',''),
        data.get('subject',''),
        data.get('message','')
    )
    if errors:
        return api_response(False, error="; ".join(errors), status_code=400)

    ok, err = mailer.send_email(
        data['to'],
        data['from'],
        data['subject'],
        data['message']
    )

    if ok:
        return api_response(True, message="Email sent successfully")
    return api_response(False, error=err, status_code=500)


@app.route('/health')
def health():
    return api_response(True, message="API running")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
