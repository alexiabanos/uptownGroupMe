import os
import requests
import urllib
from datetime import datetime
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set API access token and group ID
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
GROUP_ID = os.environ.get("GROUP_ID")

# Set user ID of the user whose photos you want to download
USER_ID = os.environ.get("GROUP_ID")

# Define the GroupMe API endpoints
MESSAGES_ENDPOINT = f"https://api.groupme.com/v3/groups/{GROUP_ID}/messages"

# Define the directory where downloaded photos will be saved
PHOTO_DIRECTORY = "./schedules"

# Define your email account details and recipient email addresses
EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_FROM = os.environ.get("EMAIL_FROM")
EMAIL_TO = os.environ.get("EMAIL_TO")

# Create the photo directory if it does not exist
os.makedirs(PHOTO_DIRECTORY, exist_ok=True)


# Define a function to download photos from a message
def download_photos_from_message(message):
    attachments = message.get("attachments", [])
    for attachment in attachments:
        if attachment["type"] == "image":
            photo_url = attachment["url"]
            photo_datetime = datetime.fromtimestamp(message["created_at"]).strftime("%m-%d-%y_%H:%M")
            photo_filename = os.path.join(PHOTO_DIRECTORY, f"{photo_datetime}.jpg")
            urllib.request.urlretrieve(photo_url, photo_filename)
            print(f"Downloaded photo {photo_filename}")
            # Send the downloaded photo as an email attachment
            subject = f"Uptown Sushi"
            body = f"{photo_datetime}"
            send_email(EMAIL_FROM, EMAIL_TO, subject, body, photo_filename)
            print(f"Sent photo {photo_filename} as email attachment to {', '.join(EMAIL_TO)}")


# Define a function to send an email with an attachment
def send_email(send_from, send_to, subject, body, attachment_path):
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Subject'] = subject
    msg.attach(MIMEText(body))
    with open(attachment_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
        msg.attach(part)
    smtp_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    smtp_server.login(EMAIL_USER, EMAIL_PASSWORD)
    smtp_server.sendmail(send_from, send_to, msg.as_string())
    smtp_server.close()


# Define a function to retrieve new messages from the GroupMe chat
def retrieve_new_messages():
    params = {"token": ACCESS_TOKEN}
    response = requests.get(MESSAGES_ENDPOINT, params=params)
    if response.status_code == 200:
        messages = response.json()["response"]["messages"]
        for message in messages:
            if message["sender_id"] == USER_ID:
                download_photos_from_message(message)


while True:
    # Call the function to retrieve new messages and download photos
    retrieve_new_messages()
    time.sleep(60 * 60)  # Retrieve new messages every hour