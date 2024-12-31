import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
import time

# Function to read the email template and extract subject and body
def read_email_template(file):
    # Read the template file content from the uploaded file (not from a file path)
    content = file.read().decode("utf-8")

    # Find where the subject ends (at the [BODY] tag)
    subject_end = content.find("[BODY]")
    if subject_end == -1:
        raise ValueError("The email template does not contain the '[BODY]' tag")

    # Extract the subject (text before the [BODY] tag)
    subject = content[:subject_end].strip()

    # Extract the body (text after the [BODY] tag)
    body_template = content[subject_end + len("[BODY]"):].strip()
    
    return subject, body_template


# Function to send emails using the SMTP server
def send_email(smtp_server, smtp_port, sender_email, sender_password, receiver_email, subject, body):
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            st.success(f"Email successfully sent to {receiver_email}")
    except Exception as e:
        st.error(f"Failed to send email to {receiver_email}: {str(e)}")


# Function to send bulk emails from a CSV file
def send_bulk_emails(csv_file, smtp_server, smtp_port, sender_email, sender_password, subject, body_template):
    # Load the CSV file containing email addresses and names
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        st.error(f"Failed to read CSV file: {str(e)}")
        return

    # Send an email to each person in the CSV file
    for index, row in df.iterrows():
        name = row['Name']
        receiver_email = row['Email']
        # Personalize the body with the recipient's name
        personalized_body = body_template.replace("[NAME]", name)

        send_email(smtp_server, smtp_port, sender_email, sender_password, receiver_email, subject, personalized_body)
        time.sleep(1)  # To avoid hitting rate limits, add a short delay


# Streamlit UI for input
def main():
    st.title("Automated Email Sender")

    # Input fields for SMTP server, port, and sender credentials
    smtp_server = st.text_input("SMTP Server (e.g., smtp.gmail.com)")
    smtp_port = st.number_input("SMTP Port (e.g., 587 for TLS)", min_value=1, value=587)
    sender_email = st.text_input("Sender Email Address")
    sender_password = st.text_input("Sender Email Password", type="password")

    # Upload CSV file with email list
    uploaded_file = st.file_uploader("Upload CSV with Email Addresses", type=["csv"])
    if uploaded_file:
        # Read and display the CSV data for verification
        df = pd.read_csv(uploaded_file)
        st.write(df)

    # Email template file
    email_template_file = st.file_uploader("Upload Email Template", type=["txt"])
    if email_template_file:
        # Extract subject and body from the template
        try:
            subject, body_template = read_email_template(email_template_file)
            st.write(f"Subject: {subject}")
            st.write(f"Body Template: {body_template[:100]}...")  # Show the first 100 characters of the body

            # Send emails button
            if st.button("Send Emails"):
                if smtp_server and sender_email and sender_password:
                    st.info("Sending emails...")
                    send_bulk_emails(uploaded_file, smtp_server, smtp_port, sender_email, sender_password, subject, body_template)
                else:
                    st.error("Please provide SMTP server credentials.")
        except Exception as e:
            st.error(f"Error processing email template: {str(e)}")

if __name__ == "__main__":
    main()
