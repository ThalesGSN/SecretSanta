import csv
import requests
import json
import argparse
import getpass
import smtplib
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string.templatelib import Template

# Load environment variables from .env file
load_dotenv()

RANDOM_ORG_URL = "https://api.random.org/json-rpc/4/invoke"

def parse_arguments():
    """Parses command-line arguments, using environment variables as defaults."""
    parser = argparse.ArgumentParser(
        description="Assigns and emails Secret Santas using random.org.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Core arguments
    parser.add_argument("--api-key", default=os.environ.get("RANDOM_ORG_API_KEY"), help="Your API key for random.org. Can also be set via RANDOM_ORG_API_KEY env var.")
    parser.add_argument("--participants-file", default="participants.csv", help="Path to the CSV file with participant names and emails.")
    parser.add_argument("--template-file", default="email-template.html", help="Path to the HTML email template.")
    
    # Event details for the template
    parser.add_argument("--event-date", default=os.environ.get("EVENT_DATE"), help="Date of the event. Can also be set via EVENT_DATE env var.")
    parser.add_argument("--expected-value", default=os.environ.get("EXPECTED_VALUE"), help="Suggested gift value. Can also be set via EXPECTED_VALUE env var.")
    parser.add_argument("--place", default=os.environ.get("PLACE"), help="Location of the event. Can also be set via PLACE env var.")
    parser.add_argument("--organizer-email", default=os.environ.get("ORGANIZER_EMAIL"), help="Organizer's email. Can also be set via ORGANIZER_EMAIL env var.")

    # Email server arguments
    parser.add_argument("--smtp-host", default=os.environ.get("SMTP_HOST"), help="SMTP server host. Can also be set via SMTP_HOST env var.")
    parser.add_argument("--smtp-port", type=int, default=os.environ.get("SMTP_PORT", 587), help="SMTP server port. Can also be set via SMTP_PORT env var.")
    parser.add_argument("--smtp-user", default=os.environ.get("SMTP_USER"), help="Username for the SMTP server. Can also be set via SMTP_USER env var.")
    
    # Action arguments
    parser.add_argument("--dry-run", action="store_true", help="Simulate the process and print emails to console instead of sending.")

    return parser.parse_args()

def validate_args(args):
    """Checks if all required arguments are present."""
    required = ["api_key", "event_date", "expected_value", "place", "organizer_email", "smtp_host", "smtp_user"]
    missing = [arg for arg in required if getattr(args, arg) is None]
    if missing:
        print("Error: Missing required configuration.")
        for arg in missing:
            print(f"  - Argument --{arg} is required, or its corresponding environment variable must be set.")
        return False
    return True

def load_participants(filename):
    """Loads participants from a CSV file."""
    # ... (implementation is unchanged)
    participants = []
    try:
        with open(filename, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if "Name" not in row or "Email" not in row:
                    print(f"Error: Missing 'Name' or 'Email' column in '{filename}'.")
                    return None
                participants.append({"name": row["Name"], "email": row["Email"]})
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return None
    return participants

def get_random_order(api_key, num_participants):
    """Fetches a random sequence of indices from random.org."""
    # ... (implementation is unchanged)
    payload = {
        "jsonrpc": "2.0",
        "method": "generateIntegers",
        "params": {"apiKey": api_key, "n": num_participants, "min": 0, "max": num_participants - 1, "replacement": False, "base": 10},
        "id": 1
    }
    try:
        response = requests.post(RANDOM_ORG_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        if "error" in result:
            print(f"Error from random.org API: {result['error']['message']}")
            return None
        return result["result"]["random"]["data"]
    except requests.exceptions.RequestException as e:
        print(f"Error calling random.org API: {e}")
        return None
    return None

def assign_secret_santas(participants, api_key):
    """Assigns Secret Santas and ensures no one gets themselves."""
    # ... (implementation is unchanged)
    n = len(participants)
    if n < 2: return []
    random_order_indices = get_random_order(api_key, n)
    if random_order_indices is None: return []
    
    givers = list(participants)
    receivers = [participants[i] for i in random_order_indices]
    
    for i in range(n):
        if givers[i]["email"] == receivers[i]["email"]:
            swap_index = (i + 1) % n
            receivers[i], receivers[swap_index] = receivers[swap_index], receivers[i]

    return list(zip(givers, receivers))

def read_template(filename):
    """Reads an email template file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Template file '{filename}' not found.")
        return None

def send_email(giver, receiver, args, smtp_password, template):
    """Constructs and sends a single Secret Santa email."""
    
    # Populate template
    giverName = giver["name"]
    body = template.replace("[PARTICIPANT_NAME]", giverName)
    body = body.replace("[DRAW_NAME]", receiver["name"])
    body = body.replace("[EVENT_DATE]", args.event_date)
    body = body.replace("[EXPECTED_VALUE]", args.expected_value)
    body = body.replace("[PLACE]", args.place)
    body = body.replace("[EMAIL_ORGANIZER]", args.organizer_email)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = Template("🎅 Ola $giverName Você tem um Amigo Secreto!")
    msg["From"] = args.smtp_user
    msg["To"] = giver["email"]
    
    msg.attach(MIMEText(body, "html"))

    if args.dry_run:
        print("--- DRY RUN: Email to " + giver['email'] + " ---")
        print(body)
        print("---------------------------------------\n")
        return True

    try:
        with smtplib.SMTP(args.smtp_host, args.smtp_port) as server:
            server.starttls()
            server.login(args.smtp_user, smtp_password)
            server.send_message(msg)
            print(f"✅ Email successfully sent to {giver['name']} ({giver['email']}).")
            return True
    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP authentication failed. Check your username and password.")
        return False
    except Exception as e:
        print(f"Error sending email to {giver['email']}: {e}")
        return False

def main():
    """Main function to run the Secret Santa assignment and send emails."""
    args = parse_arguments()
    if not validate_args(args):
        print("Invalid arguments.")
        return

    print("Starting Secret Santa assignment...")
    
    participants = load_participants(args.participants_file)
    if not participants: return

    assignments = assign_secret_santas(participants, args.api_key)
    if not assignments:
        print("Could not complete assignments.")
        return

    template = read_template(args.template_file)
    if not template: return

    smtp_password = None
    if not args.dry_run:
        smtp_password = getpass.getpass(f"Enter SMTP password for {args.smtp_user}: ")

    print("\n--- Sending Secret Santa Emails ---")
    all_sent = True
    for giver, receiver in assignments:
        if not send_email(giver, receiver, args, smtp_password, template):
            all_sent = False
            if not args.dry_run:
                break # Stop on first email error unless it's a dry run

    if all_sent:
        print("\nAssignment complete! All emails sent successfully.")
    else:
        print("\nAssignment finished, but some emails could not be sent.")

if __name__ == "__main__":
    main()

