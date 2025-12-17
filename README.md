# 🎅 Secret Santa Script

A Python-based command-line tool to automate your Secret Santa assignments with true randomness from `random.org` and send beautiful, customized HTML emails to participants.

## ✨ Features

- **Truly Random Assignments:** Uses the `random.org` API to ensure fair and unpredictable shuffling.
- **Automated Email Notifications:** Sends each participant a personalized HTML email revealing who they are the Secret Santa for.
- **Customizable HTML Template:** Easily modify the look and feel of the email by editing the `email-template.html` file.
- **Secure:** Prompts for your SMTP password securely and does not store it.
- **Flexible Configuration:** All settings, from participants to event details, are configured via command-line arguments.
- **Dry Run Mode:** Test your setup and preview emails in the console without actually sending anything.

## ⚙️ Setup

### 1. Prerequisites

- Python 3.7+
- A `random.org` API key. You can get a free one [here](https://api.random.org/api-keys).
- Your email account's SMTP details (host, port, username).
  - **Note for Gmail users:** You will likely need to generate an **"App Password"** to use with this script. See Google's documentation [here](https://support.google.com/accounts/answer/185833).

### 2. Install Dependencies

This project uses the `requests` library to communicate with the `random.org` API. Install it using pip:

```bash
pip install requests
```

### 3. Configure Participants

Create a `participants.csv` file in the same directory with two columns: `Name` and `Email`.

**Example `participants.csv`:**

```csv
Name,Email
Alice,alice@example.com
Bob,bob@example.com
Charlie,charlie@example.com
Diana,diana@example.com
```

## 🚀 Usage

Run the script from your terminal, providing all the necessary arguments. The script will then securely prompt you for your SMTP password to send the emails.

### Command

```bash
python main.py \
  --api-key "your-random-org-api-key" \
  --participants-file "participants.csv" \
  --event-date "25 de Dezembro de 2024" \
  --expected-value "R$50,00" \
  --place "Na casa da Vó" \
  --organizer-email "organizer@example.com" \
  --smtp-host "smtp.gmail.com" \
  --smtp-port 587 \
  --smtp-user "your-email@gmail.com"
```

### Arguments

| Argument                | Description                                                 |
| ----------------------- | ----------------------------------------------------------- |
| `--api-key`             | **(Required)** Your API key for `random.org`.               |
| `--participants-file`   | **(Required)** Path to your CSV file of participants.       |
| `--template-file`       | Path to the HTML email template (defaults to `email-template.html`). |
| `--event-date`          | **(Required)** The date of your event for the email template. |
| `--expected-value`      | **(Required)** The suggested gift value for the email.      |
| `--place`               | **(Required)** The event location for the email.            |
| `--organizer-email`     | **(Required)** The organizer's email for the email footer.  |
| `--smtp-host`           | **(Required)** Your email provider's SMTP server address.   |
| `--smtp-port`           | The SMTP server port (defaults to `587`).                   |
| `--smtp-user`           | **(Required)** Your email address for SMTP login.           |
| `--dry-run`             | (Optional) Simulate and print emails without sending.       |


### Testing with Dry Run

To check your setup and see what the emails will look like, add the `--dry-run` flag to the end of the command. This will print the full HTML content of each email to your console instead of connecting to your email server.

```bash
python main.py [..all your arguments..] --dry-run
```