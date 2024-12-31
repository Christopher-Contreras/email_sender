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
    # Display the raw contents of the uploaded CSV to debug
    st.write("Uploaded CSV file content:")
    st.text(csv_file.getvalue().decode("utf-8"))  # Show raw CSV content in the app

    try:
        # Attempt to read the CSV file
        df = pd.read_csv(csv_file)
        
        # If the CSV is empty, show an error
        if df.empty:
            st.error("The CSV file is empty. Please check the file content.")
            return

        # Show the loaded CSV for debugging purposes
        st.write("CSV Loaded Successfully!")
        st.write(df)  # This will display the CSV data in Streamlit UI

    except Exception as e:
        # Handle any error that occurs when reading the CSV
        st.error(f"Failed to read CSV file: {str(e)}")
        return

    # Send email logic (if CSV was successfully read)
    for index, row in df.iterrows():
        name = row['Name']
        receiver_email = row['Email']
        company = row['Company']
        
        # Personalize the email body with recipient's information
        personalized_body = body_template.replace("{Name}", name).replace("{Company}", company)
        
        # Send the email here (yo
