import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
import time
import io

# Function to read the email template and extract subject and body
def read_email_template(file):
    content = file.read().decode("utf-8")
    subject_end = content.find("[BODY]")
    if subject_end == -1:
        raise ValueError("The email template does not contain the '[BODY]' tag")
    subject = content[:subject_end].strip()
    body_template = content[subject_end + len("[BODY]"):].strip()
    return subject, body_template

# Function to send emails using the SMTP server
def send_email(smtp_server, smtp_port, sender_email, sender_password, receiver_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            st.success(f"Email successfully sent to {receiver_email}")
    except Exception as e:
        st.error(f"Failed to send email to {receiver_email}: {str(e)}")

# Function to send bulk emails from a CSV file
def send_bulk_emails(csv_file, smtp_server, smtp_port, sender_email, sender_password, subject, body_template):
    try:
        # Read the raw content of the uploaded CSV for debugging
        raw_csv = csv_file.getvalue().decode("utf-8")
        st.text(raw_csv)  # Show raw CSV content
        
        # Attempt to read the CSV
        df = pd.read_csv(csv_file)
        
        # Check if CSV is empty
        if df.empty:
            st.error("The CSV file is empty. Please check the file content.")
            return
        
        # If CSV is valid, show the content for debugging
        st.write("CSV Loaded Successfully!")
        st.write(df)  # Display the DataFrame for debugging purposes
    except pd.errors.EmptyDataError:
        st.error("The CSV file is empty. Please upload a valid CSV.")
    except pd.errors.ParserError:
        st.error("There was an issue parsing the CSV file. Ensure the file format is correct.")
    except Exception as e:
        st.error(f"Failed to process the CSV file: {str(e)}")
        return

        # Show the loaded CSV for debugging purposes
        st.write("CSV Loaded Successfully!")
        st.write(df)  # Display the CSV data in Streamlit UI
    except pd.errors.EmptyDataError:
        st.error("The CSV file is empty.")
        return
    except pd.errors.ParserError:
        st.error("There was an issue parsing the CSV file. Please ensure the format is correct.")
        return
    except Exception as e:
        st.error(f"Failed to process the CSV file: {str(e)}")
        return

    # Send email logic (if CSV was successfully read)
    for index, row in df.iterrows():
        name = row['Name']
        receiver_email = row['Email']
        company = row['Company']
        
        # Personalize the email body with recipient's information
        personalized_body = body_template.replace("{Name}", name).replace("{Company}", company)
        
        # Send the email here
        send_email(smtp_server, smtp_port, sender_email, sender_password, receiver_email, subject, personalized_body)

# Streamlit UI for input
def main():
    st.title("Automated Email Sender")

    # Input fields for SMTP server, port, and sender credentials
    smtp_server = st.text_input("SMTP Server (e.g., smtp.gmail.com or smtp.mail.yahoo.com)")
    smtp_port = st.number_input("SMTP Port (e.g., 587 for TLS)", min_value=1, value=587)
    sender_email = st.text_input("Sender Email Address")
    sender_password = st.text_input("Sender Email Password", type="password")

    # Upload CSV file with email list
    uploaded_file = st.file_uploader("Upload CSV with Email Addresses", type=["csv"])
    if uploaded_file:
        try:
            # Debugging the CSV content
            st.write("Raw CSV content:")
            raw_csv = uploaded_file.getvalue().decode("utf-8")
            st.text(raw_csv)  # Show raw CSV content for debugging
            
            # Attempt to read the CSV
            df = pd.read_csv(uploaded_file)
            st.write("CSV Loaded Successfully!")
            st.write(df)  # Display the DataFrame for debugging purposes
        except pd.errors.EmptyDataError:
            st.error("The CSV file is empty. Please upload a valid CSV.")
        except pd.errors.ParserError:
            st.error("There was an issue parsing the CSV file. Ensure the file format is correct.")
        except Exception as e:
            st.error(f"Failed to read CSV file: {str(e)}")

    # Email template file
    email_template_file = st.file_uploader("Upload Email Template", type=["txt"])
    if email_template_file:
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
