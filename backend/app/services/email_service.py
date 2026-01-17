import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from loguru import logger

class EmailService:
    @staticmethod
    def send_premium_welcome(to_email: str):
        """Send professional welcome email to new PRO subscribers"""
        smtp_email = settings.SMTP_EMAIL
        smtp_password = settings.SMTP_PASSWORD

        if not smtp_email or not smtp_password:
            logger.warning("SMTP credentials not set. Skipping email.")
            return

        subject = "Welcome to CASH MAELSTROM | Institutional Tier Unlocked"
        
        # HTML Template with Dark Mode aesthetics
        html_content = f"""
        <html>
            <body style="background-color: #0b1120; color: #e2e8f0; font-family: 'Courier New', monospace; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #334155; border-radius: 8px; overflow: hidden;">
                    
                    <!-- Header -->
                    <div style="background-color: #0f172a; padding: 20px; text-align: center; border-bottom: 1px solid #334155;">
                        <h1 style="color: #6366f1; margin: 0; letter-spacing: 2px;">CASH MAELSTROM</h1>
                        <p style="font-size: 10px; color: #64748b; margin-top: 5px;">QUANTUM MARKET RESEARCH INSTITUTE</p>
                    </div>

                    <!-- Body -->
                    <div style="padding: 30px; background-color: #1e293b;">
                        <h2 style="color: #cbd5e1; margin-top: 0;">Payment Successful</h2>
                        <p style="color: #94a3b8; line-height: 1.6;">
                            Welcome to the <span style="color: #818cf8; font-weight: bold;">Institutional Tier</span>.
                        </p>
                        <p style="color: #94a3b8; line-height: 1.6;">
                            You have successfully unlocked advanced capabilities within the Hive Mind:
                        </p>
                        <ul style="color: #cbd5e1; line-height: 1.8;">
                            <li>🔓 <strong>Strategist & Defender Agents</strong>: Enabled</li>
                            <li>🔓 <strong>PDF Reports</strong>: Unlimited Downloads</li>
                            <li>🔓 <strong>Deep Dive Analysis</strong>: Full Access</li>
                        </ul>
                        
                        <div style="margin-top: 30px; padding: 15px; background-color: #334155; border-left: 4px solid #10b981; color: #e2e8f0; font-size: 14px;">
                            "The market is a device for transferring money from the impatient to the patient." - Warren Buffett
                        </div>
                    </div>

                    <!-- Footer -->
                    <div style="background-color: #0f172a; padding: 15px; text-align: center; font-size: 10px; color: #475569;">
                        &copy; 2026 CASH MAELSTROM. All systems operational.<br>
                        This is an automated message. Do not reply.
                    </div>
                </div>
            </body>
        </html>
        """

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"CASH MAELSTROM <{smtp_email}>"
            msg["To"] = to_email
            
            part = MIMEText(html_content, "html")
            msg.attach(part)

            # Gmail SMTP
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(smtp_email, smtp_password)
                server.sendmail(smtp_email, to_email, msg.as_string())
            
            logger.success(f"📧 Premium Welcome Email sent to {to_email}")
        
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

    @staticmethod
    def send_new_user_welcome(to_email: str, verification_link: str = None):
        """Send welcome email to NEW users (sign-up)"""
        smtp_email = settings.SMTP_EMAIL
        smtp_password = settings.SMTP_PASSWORD

        if not smtp_email or not smtp_password:
            logger.warning("SMTP credentials not set. Skipping email.")
            return

        subject = "Action Required: Verify Identity | CASH MAELSTROM"
        
        # HTML Template for New Users
        # Using the verification link for the main button
        target_link = verification_link if verification_link else settings.FRONTEND_URL

        html_content = f"""
        <html>
            <body style="background-color: #0b1120; color: #e2e8f0; font-family: 'Courier New', monospace; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; border: 1px solid #334155; border-radius: 8px; overflow: hidden;">
                    
                    <!-- Header -->
                    <div style="background-color: #0f172a; padding: 20px; text-align: center; border-bottom: 1px solid #334155;">
                        <h1 style="color: #6366f1; margin: 0; letter-spacing: 2px;">CASH MAELSTROM</h1>
                        <p style="font-size: 10px; color: #64748b; margin-top: 5px;">ESTABLISHED 2026</p>
                    </div>

                    <!-- Body -->
                    <div style="padding: 30px; background-color: #1e293b;">
                        <h2 style="color: #cbd5e1; margin-top: 0;">Identity Verification Required</h2>
                        <p style="color: #94a3b8; line-height: 1.6;">
                            Your neural link to the <span style="color: #818cf8; font-weight: bold;">Hive Mind</span> is initializing.
                        </p>
                        <p style="color: #94a3b8; line-height: 1.6;">
                            <strong>Security Protocol:</strong> Access denied until biometrics are confirmed.
                        </p>
                        
                        <div style="margin-top: 30px; text-align: center;">
                            <a href="{target_link}" style="background-color: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 16px;">VERIFY IDENTITY &rarr;</a>
                        </div>

                        <p style="font-size: 11px; color: #475569; margin-top: 30px; text-align: center;">
                            If you did not initiate this link, terminate connection immediately.
                        </p>
                    </div>

                    <!-- Footer -->
                    <div style="background-color: #0f172a; padding: 15px; text-align: center; font-size: 10px; color: #475569;">
                        &copy; 2026 CASH MAELSTROM. All systems operational.<br>
                        This is an automated message. Do not reply.
                    </div>
                </div>
            </body>
        </html>
        """

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"CASH MAELSTROM <{smtp_email}>"
            msg["To"] = to_email
            
            part = MIMEText(html_content, "html")
            msg.attach(part)

            # Gmail SMTP
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(smtp_email, smtp_password)
                server.sendmail(smtp_email, to_email, msg.as_string())
            
            logger.success(f"📧 New User Welcome Email sent to {to_email}")
        
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
