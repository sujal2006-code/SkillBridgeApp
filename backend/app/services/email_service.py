import os
import smtplib
import ssl
import json
import urllib.request
import urllib.error
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, Tuple


class EmailService:
    @staticmethod
    def get_provider_status() -> Dict[str, Any]:
        """Inspect environment and return detected email providers (without exposing secrets)."""
        resend_key = os.environ.get("RESEND_API_KEY") or os.environ.get("EMAIL_API_KEY")
        sendgrid_key = os.environ.get("SENDGRID_API_KEY")
        brevo_key = os.environ.get("BREVO_API_KEY")
        
        smtp_host = os.environ.get("SMTP_HOST") or os.environ.get("MAIL_SERVER")
        smtp_user = os.environ.get("SMTP_USER") or os.environ.get("MAIL_USERNAME") or os.environ.get("GMAIL_USER")
        smtp_password = os.environ.get("SMTP_PASSWORD") or os.environ.get("MAIL_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD")
        
        email_from = (
            os.environ.get("EMAIL_FROM")
            or os.environ.get("MAIL_FROM")
            or (f"SkillBridge <{smtp_user}>" if smtp_user else "SkillBridge Verification <onboarding@resend.dev>")
        )

        providers = []
        if resend_key:
            providers.append("Resend API")
        if brevo_key:
            providers.append("Brevo API")
        if sendgrid_key:
            providers.append("SendGrid API")
        if smtp_host and smtp_user and smtp_password:
            providers.append(f"SMTP ({smtp_host})")

        return {
            "has_live_provider": len(providers) > 0,
            "configured_providers": providers,
            "sender_email": email_from,
            "smtp_configured": bool(smtp_host and smtp_user and smtp_password),
            "resend_configured": bool(resend_key),
            "brevo_configured": bool(brevo_key),
            "sendgrid_configured": bool(sendgrid_key),
        }

    @classmethod
    def send_otp_email(cls, to_email: str, otp_code: str, purpose: str = "register") -> Tuple[bool, str]:
        """
        Send a real 6-digit OTP verification email to the user's Gmail/email address.
        Returns: (success: bool, detail_message: str)
        """
        status = cls.get_provider_status()
        
        action_title = "Account Verification" if purpose == "register" else "Password Reset"
        action_desc = (
            "Thank you for joining SkillBridge. Use the verification code below to complete your account registration and unlock your Digital Skill Passport."
            if purpose == "register"
            else "We received a request to reset your SkillBridge account password. Use the verification code below to set a new password."
        )

        subject = f"SkillBridge — {otp_code} is your {action_title} Code"

        # High-contrast branded HTML email template
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>{subject}</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f7f9fb; margin: 0; padding: 24px; color: #191c1e;">
          <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 540px; background-color: #ffffff; border-radius: 16px; overflow: hidden; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
            <!-- Header -->
            <tr>
              <td style="background-color: #00687a; padding: 28px 32px; text-align: center;">
                <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;">SkillBridge</h1>
                <p style="color: #e0f2f1; margin: 6px 0 0 0; font-size: 13px;">Verifiable Digital Skill Passport & Opportunities</p>
              </td>
            </tr>
            <!-- Content -->
            <tr>
              <td style="padding: 32px 32px 24px 32px;">
                <h2 style="font-size: 18px; font-weight: 600; margin: 0 0 12px 0; color: #1e293b;">{action_title}</h2>
                <p style="font-size: 14px; line-height: 1.6; color: #475569; margin: 0 0 24px 0;">{action_desc}</p>
                
                <!-- OTP Code Box -->
                <div style="background-color: #f0f7f9; border: 1px solid #cce5ea; border-radius: 12px; padding: 20px; text-align: center; margin: 0 0 24px 0;">
                  <div style="font-size: 12px; text-transform: uppercase; font-weight: 700; color: #00687a; letter-spacing: 1px; margin-bottom: 6px;">Your 6-Digit Verification Code</div>
                  <div style="font-size: 36px; font-weight: 800; letter-spacing: 8px; color: #004e5c; font-family: monospace;">{otp_code}</div>
                  <div style="font-size: 12px; color: #64748b; margin-top: 8px;">Valid for <strong>10 minutes</strong>. Single-use only.</div>
                </div>

                <p style="font-size: 13px; line-height: 1.5; color: #64748b; margin: 0;">
                  If you did not request this verification code, please ignore this email. Your account remains secure.
                </p>
              </td>
            </tr>
            <!-- Footer -->
            <tr>
              <td style="background-color: #f8fafc; padding: 20px 32px; border-top: 1px solid #f1f5f9; text-align: center; font-size: 12px; color: #94a3b8;">
                SkillBridge Inc. • Verifiable Credential Protocol<br>
                This is an automated security transmission. Do not reply to this email.
              </td>
            </tr>
          </table>
        </body>
        </html>
        """

        plain_text = f"SkillBridge {action_title}\n\n{action_desc}\n\nYour 6-Digit Verification Code is: {otp_code}\n\nThis code expires in 10 minutes.\nIf you did not request this, please ignore this email."

        errors = []

        # 1. Try Resend API (HTTP REST)
        resend_key = os.environ.get("RESEND_API_KEY") or os.environ.get("EMAIL_API_KEY")
        if resend_key:
            try:
                from_email = os.environ.get("EMAIL_FROM") or "SkillBridge Verification <onboarding@resend.dev>"
                cls._send_via_resend(
                    api_key=resend_key,
                    from_email=from_email,
                    to_email=to_email,
                    subject=subject,
                    html=html_body,
                    text=plain_text,
                )
                print(f"[EMAIL SERVICE SUCCESS] Delivered OTP via Resend to {to_email}")
                return True, "Delivered via Resend"
            except Exception as e:
                err_str = f"Resend error: {str(e)}"
                print(f"[EMAIL SERVICE WARNING] {err_str}")
                errors.append(err_str)

        # 2. Try Brevo (Sendinblue) API (HTTP REST)
        brevo_key = os.environ.get("BREVO_API_KEY")
        if brevo_key:
            try:
                from_email = os.environ.get("EMAIL_FROM") or os.environ.get("SMTP_USER") or "noreply@skillbridge.edu"
                cls._send_via_brevo(
                    api_key=brevo_key,
                    from_email=from_email,
                    to_email=to_email,
                    subject=subject,
                    html=html_body,
                    text=plain_text,
                )
                print(f"[EMAIL SERVICE SUCCESS] Delivered OTP via Brevo to {to_email}")
                return True, "Delivered via Brevo"
            except Exception as e:
                err_str = f"Brevo error: {str(e)}"
                print(f"[EMAIL SERVICE WARNING] {err_str}")
                errors.append(err_str)

        # 3. Try SendGrid API (HTTP REST)
        sendgrid_key = os.environ.get("SENDGRID_API_KEY")
        if sendgrid_key:
            try:
                from_email = os.environ.get("EMAIL_FROM") or "noreply@skillbridge.edu"
                cls._send_via_sendgrid(
                    api_key=sendgrid_key,
                    from_email=from_email,
                    to_email=to_email,
                    subject=subject,
                    html=html_body,
                    text=plain_text,
                )
                print(f"[EMAIL SERVICE SUCCESS] Delivered OTP via SendGrid to {to_email}")
                return True, "Delivered via SendGrid"
            except Exception as e:
                err_str = f"SendGrid error: {str(e)}"
                print(f"[EMAIL SERVICE WARNING] {err_str}")
                errors.append(err_str)

        # 4. Try SMTP (e.g. Gmail App Password, Brevo SMTP, AWS SES)
        smtp_host = os.environ.get("SMTP_HOST") or os.environ.get("MAIL_SERVER")
        smtp_port = int(os.environ.get("SMTP_PORT") or os.environ.get("MAIL_PORT") or 587)
        smtp_user = os.environ.get("SMTP_USER") or os.environ.get("MAIL_USERNAME") or os.environ.get("GMAIL_USER")
        smtp_password = os.environ.get("SMTP_PASSWORD") or os.environ.get("MAIL_PASSWORD") or os.environ.get("GMAIL_APP_PASSWORD")
        smtp_tls = os.environ.get("SMTP_TLS", "true").lower() in ("true", "1", "yes")

        if smtp_host and smtp_user and smtp_password:
            try:
                from_email = os.environ.get("EMAIL_FROM") or f"SkillBridge <{smtp_user}>"
                cls._send_via_smtp(
                    host=smtp_host,
                    port=smtp_port,
                    user=smtp_user,
                    password=smtp_password,
                    use_tls=smtp_tls,
                    from_email=from_email,
                    to_email=to_email,
                    subject=subject,
                    html=html_body,
                    text=plain_text,
                )
                print(f"[EMAIL SERVICE SUCCESS] Delivered OTP via SMTP ({smtp_host}) to {to_email}")
                return True, f"Delivered via SMTP ({smtp_host})"
            except Exception as e:
                err_str = f"SMTP ({smtp_host}) error: {str(e)}"
                print(f"[EMAIL SERVICE WARNING] {err_str}")
                errors.append(err_str)

        # 5. If no providers were configured OR all configured providers failed
        if not status["has_live_provider"]:
            msg = (
                f"No email provider configured in Vercel environment variables. "
                f"Please add RESEND_API_KEY or SMTP_USER/SMTP_PASSWORD in Vercel Project Settings."
            )
            print(f"\n[EMAIL SERVICE NOTICE] {msg} Target: {to_email}, Code: {otp_code}\n")
            return False, msg
        else:
            combined_errors = "; ".join(errors)
            msg = f"Failed to deliver email through configured providers: {combined_errors}"
            print(f"\n[EMAIL SERVICE ERROR] {msg}\n")
            return False, msg

    @staticmethod
    def _send_via_resend(api_key: str, from_email: str, to_email: str, subject: str, html: str, text: str):
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json",
            "User-Agent": "SkillBridge-Backend/1.0",
        }
        data = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html,
            "text": text,
        }
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status >= 400:
                    resp_body = response.read().decode("utf-8", errors="ignore")
                    raise RuntimeError(f"Resend HTTP {response.status}: {resp_body}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Resend HTTP {e.code}: {err_body}")

    @staticmethod
    def _send_via_brevo(api_key: str, from_email: str, to_email: str, subject: str, html: str, text: str):
        url = "https://api.brevo.com/v3/smtp/email"
        sender_name = "SkillBridge"
        sender_email = from_email
        if "<" in from_email and ">" in from_email:
            sender_name = from_email.split("<")[0].strip()
            sender_email = from_email.split("<")[1].replace(">", "").strip()

        headers = {
            "api-key": api_key.strip(),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        data = {
            "sender": {"name": sender_name, "email": sender_email},
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html,
            "textContent": text,
        }
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status >= 400:
                    resp_body = response.read().decode("utf-8", errors="ignore")
                    raise RuntimeError(f"Brevo HTTP {response.status}: {resp_body}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Brevo HTTP {e.code}: {err_body}")

    @staticmethod
    def _send_via_sendgrid(api_key: str, from_email: str, to_email: str, subject: str, html: str, text: str):
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json",
        }
        data = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": from_email},
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": text},
                {"type": "text/html", "value": html},
            ],
        }
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status >= 400:
                    resp_body = response.read().decode("utf-8", errors="ignore")
                    raise RuntimeError(f"SendGrid HTTP {response.status}: {resp_body}")
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"SendGrid HTTP {e.code}: {err_body}")

    @staticmethod
    def _send_via_smtp(host: str, port: int, user: str, password: str, use_tls: bool, from_email: str, to_email: str, subject: str, html: str, text: str):
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        msg.attach(MIMEText(text, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        clean_user = user.strip()
        clean_pass = password.strip().replace(" ", "")  # Gmail app passwords often copy with spaces

        if port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, port, context=context, timeout=12) as server:
                server.login(clean_user, clean_pass)
                server.sendmail(from_email, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=12) as server:
                if use_tls:
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                server.login(clean_user, clean_pass)
                server.sendmail(from_email, [to_email], msg.as_string())
