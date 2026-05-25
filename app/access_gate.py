import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


def get_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    try:
        creds = Credentials.from_service_account_file(
            os.getenv("GOOGLE_CREDENTIALS_PATH", "google_credentials.json"),
            scopes=scopes
        )
    except FileNotFoundError:
        creds = Credentials.from_service_account_info(
            dict(st.secrets["google_credentials"]),
            scopes=scopes
        )
    client = gspread.authorize(creds)
    return client.open_by_key(
        os.getenv("GOOGLE_SHEET_ID") or st.secrets["GOOGLE_SHEET_ID"]
    )


def is_approved(email: str) -> bool:
    try:
        sheet = get_sheet()
        approved = sheet.worksheet("approved")
        emails = approved.col_values(1)
        return email.lower().strip() in [e.lower().strip() for e in emails]
    except Exception:
        return False


def submit_access_request(name, email, company, linkedin, reason):
    from dotenv import load_dotenv
    load_dotenv()

    # 1. Write to Google Sheet — always runs first
    sheet = get_sheet()
    requests_tab = sheet.worksheet("requests")
    requests_tab.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        name, email, company, linkedin, reason, "pending"
    ])

    # 2. Send email via Gmail SMTP — fails silently, never crashes the app
    try:
        gmail_user = os.getenv("GMAIL_USER", "Karamjeet.6613@gmail.com")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")
        sheet_url = f"https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEET_ID')}"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🔐 Access Request: {name} from {company}"
        msg["From"] = gmail_user
        msg["To"] = gmail_user  # sends to yourself

        html = f"""
        <div style="font-family: sans-serif; max-width: 560px; margin: 0 auto;">

          <h2 style="color: #111;">🔐 New Access Request — Astra AI</h2>

          <table cellpadding="10" style="border-collapse:collapse; width:100%; background:#f9f9f9; border-radius:8px;">
            <tr>
              <td style="color:#555; width:120px;"><b>Name</b></td>
              <td style="color:#111;">{name}</td>
            </tr>
            <tr style="background:#fff;">
              <td style="color:#555;"><b>Email</b></td>
              <td style="color:#111;">{email}</td>
            </tr>
            <tr>
              <td style="color:#555;"><b>Company</b></td>
              <td style="color:#111;">{company}</td>
            </tr>
            <tr style="background:#fff;">
              <td style="color:#555;"><b>LinkedIn</b></td>
              <td style="color:#111;">{linkedin or '—'}</td>
            </tr>
            <tr>
              <td style="color:#555;"><b>Reason</b></td>
              <td style="color:#111;">{reason or '—'}</td>
            </tr>
            <tr style="background:#fff;">
              <td style="color:#555;"><b>Time</b></td>
              <td style="color:#111;">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</td>
            </tr>
          </table>

          <br>

          <a href="{sheet_url}"
             style="display:inline-block; background:#22c55e; color:#fff;
                    padding:14px 28px; border-radius:8px; text-decoration:none;
                    font-weight:bold; font-size:15px;">
            ✅ Open Sheet to Approve
          </a>

          <br><br>

          <p style="color:#888; font-size:12px; line-height:1.6;">
            To approve: click the button above → go to the <b>approved</b> tab
            → add <b>{email}</b> in Column A → save.<br>
            They'll get full access automatically on their next refresh.
          </p>

          <p style="color:#ccc; font-size:11px;">Astra AI · Access Gate</p>

        </div>
        """

        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, gmail_user, msg.as_string())

        print("✅ Email notification sent successfully")

    except Exception as e:
        print(f"Email notification skipped (non-critical): {e}")