import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_discord_notification(jobs):
    """
    Send job notifications to Discord
    Requires: DISCORD_WEBHOOK_URL in .env
    """
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("⚠️  No Discord webhook URL configured")
        return
    
    import requests
    
    # Create message
    message = f"**🔍 Found {len(jobs)} Relevant Jobs!**\n\n"
    
    for i, job in enumerate(jobs[:5], 1):  # Limit to 5 jobs to avoid Discord message limits
        message += f"**{i}. {job['title']}**\n"
        message += f"🏢 {job['company']}\n"
        message += f"📍 {job['location']}\n"
        message += f"🔗 {job['url']}\n\n"
    
    if len(jobs) > 5:
        message += f"_...and {len(jobs) - 5} more jobs. Check your dashboard for details._\n"
    
    # Send to Discord
    data = {"content": message}
    response = requests.post(webhook_url, json=data)
    
    if response.status_code != 204:
        print(f"❌ Discord notification failed: {response.status_code}")


def send_email_notification(jobs):
    """
    Send job notifications via email
    Requires in .env:
    - SMTP_SERVER (e.g., smtp.gmail.com)
    - SMTP_PORT (e.g., 587)
    - SMTP_USERNAME (your email)
    - SMTP_PASSWORD (app password)
    - EMAIL_TO (recipient email)
    """
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    email_to = os.getenv("EMAIL_TO")
    
    if not all([smtp_server, smtp_username, smtp_password, email_to]):
        print("⚠️  Email not configured")
        return
    
    # Create email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔍 {len(jobs)} New Relevant Jobs Found"
    msg["From"] = smtp_username
    msg["To"] = email_to
    
    # HTML email body
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2>🔍 Found {len(jobs)} Relevant Jobs!</h2>
        <p>Here are today's job matches:</p>
    """
    
    for i, job in enumerate(jobs, 1):
        html += f"""
        <div style="border-left: 4px solid #4A90E2; padding-left: 15px; margin: 20px 0;">
          <h3>{i}. {job['title']}</h3>
          <p><strong>🏢 Company:</strong> {job['company']}</p>
          <p><strong>📍 Location:</strong> {job['location']}</p>
          <p><strong>📝 Summary:</strong></p>
          <p style="color: #666;">{job.get('summary', 'No summary available')}</p>
          <p><a href="{job['url']}" style="color: #4A90E2;">View Job Posting →</a></p>
        </div>
        """
    
    html += """
      </body>
    </html>
    """
    
    # Attach HTML
    part = MIMEText(html, "html")
    msg.attach(part)
    
    # Send email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
    except Exception as e:
        print(f"❌ Email notification failed: {e}")


def send_test_notification():
    """Test notifications with dummy data"""
    test_jobs = [
        {
            "title": "Machine Learning Engineer",
            "company": "DeepMind",
            "location": "London, UK",
            "url": "https://example.com/job1",
            "summary": "Exciting role working on cutting-edge AI research..."
        }
    ]
    
    print("📤 Sending test notifications...")
    send_discord_notification(test_jobs)
    send_email_notification(test_jobs)
    print("✅ Test complete!")


if __name__ == "__main__":
    send_test_notification()