import streamlit as st
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_emails(smtp_server, smtp_port, sender_email, sender_password, subject, body_template, contacts_file):
    try:
        # Load the contact list
        contacts = pd.read_csv(contacts_file)

        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Send emails
        for _, contact in contacts.iterrows():
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = contact['Email']
            msg['Subject'] = subject

            # Personalize the body using placeholders
            body = body_template.format(**contact.to_dict())
            msg.attach(MIMEText(body, 'plain'))
            server.sendmail(sender_email, contact['Email'], msg.as_string())

        server.quit()
        return "Emails sent successfully!"
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.title("Automated Email Sender")
st.write("Send personalized emails from a master contact list.")

# Email server configuration
st.header("Email Configuration")
smtp_server = st.text_input("SMTP Server", "smtp.gmail.com")
smtp_port = st.number_input("SMTP Port", 587)
sender_email = st.text_input("Your Email")
sender_password = st.text_input("Your Password", type="password")

# Email template configuration
st.header("Email Template")
subject = st.text_input("Email Subject", "Hello {Name}!")
body_template = st.text_area(
    "Email Body Template",
    "Hi {Name},\n\nThis is a personalized email for {Company}.\n\nBest regards,\nYour Name",
)

# Upload contacts CSV file
st.header("Upload Contacts")
contacts_file = st.file_uploader(
    "Upload a CSV file with at least 'Name', 'Email', and other fields for personalization.",
    type="csv",
)

# Send emails button
if st.button("Send Emails"):
    if not all([smtp_server, smtp_port, sender_email, sender_password, contacts_file]):
        st.error("Please fill in all fields and upload a contacts file.")
    else:
        result = send_emails(
            smtp_server,
            smtp_port,
            sender_email,
            sender_password,
            subject,
            body_template,
            contacts_file,
        )
        if "successfully" in result:
            st.success(result)
        else:
            st.error(result)
