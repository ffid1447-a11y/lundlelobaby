#!/usr/bin/env python3
"""Professional Email Sender WebUI
Sends emails securely through Gmail SMTP with a modern responsive interface"""

import smtplib
import re
from email.message import EmailMessage
from flask import Flask, request, jsonify
from functools import wraps

# -------- CONFIG --------
SENDER_EMAIL = "rkhakkieva@gmail.com"     # your Gmail address
APP_PASSWORD = "acee hcmb cvqk iwum"      # your Gmail App Password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
MIN_MESSAGE_LENGTH = 5
MAX_MESSAGE_LENGTH = 5000
MAX_SUBJECT_LENGTH = 200
# ------------------------

app = Flask(__name__)
app.secret_key = 'email-sender-secret-key-2024'
app.config['SESSION_TYPE'] = 'filesystem'


def api_response(success, message=None, error=None, data=None, status_code=200):
    """Standardized API response format"""
    response = {
        'success': success,
        'message': message,
        'error': error,
        'data': data
    }
    return jsonify(response), status_code


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_input(from_email, to_email, subject, message):
    """Validate all email inputs"""
    errors = []

    if not from_email or not validate_email(from_email):
        errors.append('Invalid sender email format')

    if not to_email or not validate_email(to_email):
        errors.append('Invalid recipient email format')

    if not subject or len(subject) == 0:
        errors.append('Subject cannot be empty')

    if len(subject) > MAX_SUBJECT_LENGTH:
        errors.append(f'Subject exceeds {MAX_SUBJECT_LENGTH} characters')

    if not message or len(message) < MIN_MESSAGE_LENGTH:
        errors.append(f'Message must be at least {MIN_MESSAGE_LENGTH} characters')

    if len(message) > MAX_MESSAGE_LENGTH:
        errors.append(f'Message exceeds {MAX_MESSAGE_LENGTH} characters')

    return errors


class EmailSender:
    """Handles email sending securely via Gmail SMTP"""

    def send_email(self, to_email, from_email, subject, message):
        """
        Send email through Gmail SMTP
        
        Args:
            to_email: Recipient email address
            from_email: Sender email address (display name)
            subject: Email subject
            message: Email body content
            
        Returns:
            dict: Response with success status and message/error
        """
        try:
            msg = EmailMessage()
            msg["From"] = f"{from_email} <{SENDER_EMAIL}>"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.set_content(message)

            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as smtp:
                smtp.login(SENDER_EMAIL, APP_PASSWORD)
                smtp.send_message(msg)

            return {
                'success': True,
                'message': 'Email sent successfully!',
                'error': None
            }
        except smtplib.SMTPAuthenticationError:
            return {
                'success': False,
                'message': None,
                'error': 'Authentication failed. Check Gmail credentials.'
            }
        except smtplib.SMTPException as e:
            return {
                'success': False,
                'message': None,
                'error': f'SMTP error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'message': None,
                'error': f'Error sending email: {str(e)}'
            }


email_sender = EmailSender()


@app.route('/')
def index():
    """Main Email Sender Page UI"""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ANONYMOUS EMAIL SENDER</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary: #4f46e5;
            --primary-dark: #4338ca;
            --secondary: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --dark: #1f2937;
            --light: #f9fafb;
            --gray: #6b7280;
            --gray-light: #e5e7eb;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }

        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .container {
            width: 100%;
            max-width: 800px;
        }

        .card {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        .card-header {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            padding: 30px;
            text-align: center;
            position: relative;
        }

        .card-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--secondary);
        }

        .card-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .card-subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .card-body {
            padding: 40px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--dark);
            font-size: 0.95rem;
        }

        .form-control {
            width: 100%;
            padding: 15px 20px;
            border: 2px solid var(--gray-light);
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s;
            background: white;
        }

        .form-control:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
        }

        .form-control.message {
            min-height: 150px;
            resize: vertical;
        }

        .btn {
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        .btn-primary {
            background: var(--primary);
            color: white;
            width: 100%;
        }

        .btn-primary:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(79, 70, 229, 0.3);
        }

        .btn-primary:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .status-message {
            padding: 15px 20px;
            border-radius: 12px;
            margin: 20px 0;
            display: none;
            animation: slideIn 0.3s ease;
        }

        @keyframes slideIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .status-success {
            background: #d1fae5;
            color: #065f46;
            border: 1px solid #a7f3d0;
        }

        .status-error {
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .feature {
            text-align: center;
            padding: 20px;
            background: #f8fafc;
            border-radius: 12px;
            transition: transform 0.3s;
        }

        .feature:hover {
            transform: translateY(-5px);
        }

        .feature-icon {
            font-size: 2.5rem;
            color: var(--primary);
            margin-bottom: 15px;
        }

        .feature-title {
            font-weight: 600;
            margin-bottom: 10px;
            color: var(--dark);
        }

        .feature-desc {
            color: var(--gray);
            font-size: 0.9rem;
        }

        .history-section {
            margin-top: 40px;
            border-top: 1px solid var(--gray-light);
            padding-top: 30px;
        }

        .history-title {
            font-size: 1.3rem;
            margin-bottom: 20px;
            color: var(--dark);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .history-item {
            padding: 15px;
            border: 1px solid var(--gray-light);
            border-radius: 10px;
            margin-bottom: 10px;
            background: #fafafa;
        }

        .history-subject {
            font-weight: 600;
            margin-bottom: 5px;
        }

        .history-details {
            font-size: 0.9rem;
            color: var(--gray);
            display: flex;
            justify-content: space-between;
        }

        .footer {
            text-align: center;
            margin-top: 30px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9rem;
        }

        .char-count {
            text-align: right;
            font-size: 0.8rem;
            color: var(--gray);
            margin-top: 5px;
        }

        .tabs {
            display: flex;
            margin-bottom: 30px;
            border-bottom: 1px solid var(--gray-light);
        }

        .tab {
            padding: 15px 25px;
            cursor: pointer;
            font-weight: 600;
            color: var(--gray);
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }

        .tab.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        @media (max-width: 768px) {
            body {
                padding: 10px;
            }

            .card-body {
                padding: 25px;
            }

            .card-title {
                font-size: 1.5rem;
            }

            .features {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h1 class="card-title"><i class="fas fa-paper-plane"></i> ANONYMOUS EMAIL SENDER</h1>
                <p class="card-subtitle">FOR FREE</p>
            </div>

            <div class="card-body">
                <div class="tabs">
                    <div class="tab active" data-tab="compose">Compose Email</div>
                    <div class="tab" data-tab="history">Sent History</div>
                    <div class="tab" data-tab="about">About</div>
                </div>

                <div class="tab-content active" id="compose-tab">
                    <form id="email-form">
                        <div class="form-group">
                            <label class="form-label" for="from-email">
                                <i class="fas fa-envelope"></i> From Email
                            </label>
                            <input type="email" class="form-control" id="from-email"
                                    placeholder="your-email@example.com" required
                                   value="example@gmail.com">
                        </div>

                        <div class="form-group">
                            <label class="form-label" for="to-email">
                                <i class="fas fa-user"></i> To Email
                            </label>
                            <input type="email" class="form-control" id="to-email"
                                    placeholder="recipient@example.com" required
                                   value="example@gmail.com">
                        </div>

                        <div class="form-group">
                            <label class="form-label" for="subject">
                                <i class="fas fa-tag"></i> Subject
                            </label>
                            <input type="text" class="form-control" id="subject"
                                    placeholder="Email subject" required value="King">
                        </div>

                        <div class="form-group">
                            <label class="form-label" for="message">
                                <i class="fas fa-edit"></i> Message
                            </label>
                            <textarea class="form-control message" id="message"
                                       placeholder="Type your message here..." required>minimum 20 character message</textarea>
                            <div class="char-count"><span id="char-count">0</span> characters</div>
                        </div>

                        <div id="status-message"></div>

                        <button type="submit" class="btn btn-primary" id="send-btn">
                            <i class="fas fa-paper-plane"></i> Send Email
                        </button>
                    </form>

                    <div class="features">
                        <div class="feature">
                            <div class="feature-icon">
                                <i class="fas fa-shield-alt"></i>
                            </div>
                            <div class="feature-title">Secure</div>
                            <div class="feature-desc">Emails sent through encrypted API</div>
                        </div>

                        <div class="feature">
                            <div class="feature-icon">
                                <i class="fas fa-bolt"></i>
                            </div>
                            <div class="feature-title">Fast</div>
                            <div class="feature-desc">Quick delivery with minimal latency</div>
                        </div>

                        <div class="feature">
                            <div class="feature-icon">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <div class="feature-title">Reliable</div>
                            <div class="feature-desc">High delivery success rate</div>
                        </div>
                    </div>
                </div>

                <div class="tab-content" id="history-tab">
                    <div class="history-section">
                        <h3 class="history-title">
                            <i class="fas fa-history"></i> Sent Emails
                        </h3>
                        <div id="history-list">
                            <p style="text-align: center; color: var(--gray);">No sent emails yet</p>
                        </div>
                    </div>
                </div>

                <div class="tab-content" id="about-tab">
                    <div class="form-group">
                        <h3><i class="fas fa-info-circle"></i> About Secure Email Sender</h3>
                        <p style="margin-top: 15px; line-height: 1.6;">
                            This application allows you to send emails securely through Gmail SMTP.
                            It provides a user-friendly interface for composing and sending messages with
                            professional delivery capabilities.
                        </p>

                        <h4 style="margin-top: 20px;">Features:</h4>
                        <ul style="margin-left: 20px; margin-top: 10px; line-height: 1.8;">
                            <li>Secure email transmission</li>
                            <li>Simple and intuitive interface</li>
                            <li>Message history tracking</li>
                            <li>Responsive design for all devices</li>
                            <li>Professional email templates</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>Powered by frappeash.t.me • Secure Email Delivery System</p>
        </div>
    </div>

    <script>
        // DOM Elements
        const emailForm = document.getElementById('email-form');
        const fromEmail = document.getElementById('from-email');
        const toEmail = document.getElementById('to-email');
        const subject = document.getElementById('subject');
        const message = document.getElementById('message');
        const sendBtn = document.getElementById('send-btn');
        const statusMessage = document.getElementById('status-message');
        const charCount = document.getElementById('char-count');
        const historyList = document.getElementById('history-list');
        const tabs = document.querySelectorAll('.tab');
        const tabContents = document.querySelectorAll('.tab-content');

        // Character counter
        message.addEventListener('input', function() {
            charCount.textContent = this.value.length;
        });

        // Initialize character count
        charCount.textContent = message.value.length;

        // Tab functionality
        tabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const tabId = this.getAttribute('data-tab');

                // Update active tab
                tabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');

                // Show active tab content
                tabContents.forEach(content => {
                    content.classList.remove('active');
                    if (content.id === `${tabId}-tab`) {
                        content.classList.add('active');
                    }
                });

                // Load history if history tab is selected
                if (tabId === 'history') {
                    loadHistory();
                }
            });
        });

        // Load sent email history
        function loadHistory() {
            const history = JSON.parse(localStorage.getItem('emailHistory') || '[]');

            if (history.length === 0) {
                historyList.innerHTML = '<p style="text-align: center; color: var(--gray);">No sent emails yet</p>';
                return;
            }

            let html = '';
            history.forEach((item, index) => {
                html += `
                    <div class="history-item">
                        <div class="history-subject">${item.subject}</div>
                        <div class="history-details">
                            <span>To: ${item.to}</span>
                            <span>${item.date}</span>
                        </div>
                    </div>
                `;
            });

            historyList.innerHTML = html;
        }

        // Save email to history
        function saveToHistory(emailData) {
            const history = JSON.parse(localStorage.getItem('emailHistory') || '[]');

            history.unshift({
                to: emailData.to,
                from: emailData.from,
                subject: emailData.subject,
                date: new Date().toLocaleString(),
                message: emailData.message.substring(0, 50) + '...'
            });

            // Keep only last 10 items
            if (history.length > 10) {
                history.pop();
            }

            localStorage.setItem('emailHistory', JSON.stringify(history));
        }

        // Form submission
        emailForm.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Disable send button and show loading
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<div class="loading"></div> Sending...';

            // Clear previous status
            statusMessage.style.display = 'none';
            statusMessage.className = 'status-message';

            // Prepare data
            const emailData = {
                from: fromEmail.value,
                to: toEmail.value,
                subject: subject.value,
                message: message.value
            };

            try {
                const response = await fetch('/send-email', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(emailData)
                });

                const result = await response.json();

                if (result.success) {
                    statusMessage.className = 'status-message status-success';
                    statusMessage.innerHTML = `
                        <i class="fas fa-check-circle"></i> ${result.message}
                    `;

                    // Save to history
                    saveToHistory(emailData);
                } else {
                    statusMessage.className = 'status-message status-error';
                    statusMessage.innerHTML = `
                        <i class="fas fa-exclamation-circle"></i> ${result.error}
                    `;
                }
            } catch (error) {
                statusMessage.className = 'status-message status-error';
                statusMessage.innerHTML = `
                    <i class="fas fa-exclamation-circle"></i> Network error: ${error.message}
                `;
            } finally {
                statusMessage.style.display = 'block';
                sendBtn.disabled = false;
                sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Email';
            }
        });
    </script>
</body>
</html>'''


@app.route('/send-email', methods=['POST'])
def send_email():
    """
    Send email through Gmail SMTP
    
    Expected JSON payload:
    {
        "from": "sender_name",
        "to": "recipient@example.com",
        "subject": "Email subject",
        "message": "Email body"
    }
    """
    try:
        data = request.get_json()

        if not data:
            return api_response(False, error='Invalid JSON payload', status_code=400)

        from_email = data.get('from', '').strip()
        to_email = data.get('to', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        validation_errors = validate_input(from_email, to_email, subject, message)
        if validation_errors:
            error_msg = '; '.join(validation_errors)
            return api_response(False, error=error_msg, status_code=400)

        result = email_sender.send_email(to_email, from_email, subject, message)

        if result['success']:
            return api_response(True, message=result['message'], status_code=200)
        else:
            return api_response(False, error=result['error'], status_code=500)

    except Exception as e:
        return api_response(False, error=f'Server error: {str(e)}', status_code=500)


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return api_response(True, message='API is running', status_code=200)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return api_response(False, error='Endpoint not found', status_code=404)


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return api_response(False, error='Internal server error', status_code=500)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)