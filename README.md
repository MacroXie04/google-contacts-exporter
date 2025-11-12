# Google Contacts Exporter

A lightweight Python tool that uses the Google People API to export your Google Contacts — including full metadata such as creation and update timestamps, emails, phone numbers, and organization info — into a structured CSV file.

## Features

- OAuth 2.0 authentication flow for Google user login
- Retrieve all contact information using the Google People API
- Extract contact fields: Name, Email, Phone, Organization, Title
- Extract metadata timestamps: Creation time and Update time
- Automatic pagination handling for accounts with more than 1,000 contacts
- Clean CSV output with UTF-8 encoding

## Prerequisites

- Python 3.9 or higher
- A Google account with contacts
- Google Cloud Console project with People API enabled

## Setup Instructions

### 1. Enable Google People API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** > **Library**
4. Search for "People API" and click on it
5. Click **Enable**

### 2. Create OAuth 2.0 Credentials

1. In Google Cloud Console, go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth client ID**
3. If prompted, configure the OAuth consent screen:
   - Choose **External** (unless you have a Google Workspace account)
   - Fill in the required fields (App name, User support email, Developer contact)
   - Add scopes: `https://www.googleapis.com/auth/contacts.readonly`
   - Add test users if your app is in testing mode
4. For Application type, select **Desktop app**
5. Give it a name (e.g., "Contacts Exporter")
6. Click **Create**
7. Download the credentials JSON file
8. Rename the downloaded file to `client_secret.json` and place it in the project root directory

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

1. Make sure `client_secret.json` is in the project root directory
2. Run the script:

```bash
python contacts_exporter.py
```

3. On first run, you'll be prompted to:
   - Open a browser window for Google authentication
   - Sign in with your Google account
   - Grant permissions to access your contacts
4. The script will save your credentials to `token.json` for future use
5. Once complete, your contacts will be exported to `contacts_with_timestamps.csv`

## Output Format

The CSV file contains the following columns:

| Column | Description |
|--------|-------------|
| Name | Contact's full name |
| Email | Primary email address |
| Phone | Primary phone number |
| Organization | Organization name |
| Title | Job title |
| Created | Contact creation timestamp (ISO 8601 format) |
| Updated | Last update timestamp (ISO 8601 format) |

### Example Output

```csv
Name,Email,Phone,Organization,Title,Created,Updated
John Doe,john@example.com,+1 555 555 1234,Acme Corp,Software Engineer,2021-06-02T18:44:32Z,2024-10-05T09:21:17Z
Jane Smith,jane@example.com,+1 555 555 5678,Tech Inc,Product Manager,2020-03-15T10:30:00Z,2024-09-20T14:22:45Z
```

## Notes

- The script uses read-only access to your contacts
- Credentials are stored locally in `token.json` and will be reused for subsequent runs
- If you have more than 1,000 contacts, the script automatically handles pagination
- Missing fields (e.g., phone numbers, organizations) will appear as empty strings in the CSV
- Timestamps are in ISO 8601 format (UTC) as returned by the Google People API

## Troubleshooting

### "client_secret.json not found" error

Make sure you've downloaded your OAuth 2.0 credentials from Google Cloud Console and saved them as `client_secret.json` in the project root directory.

### Authentication errors

- Delete `token.json` and run the script again to re-authenticate
- Make sure the People API is enabled in your Google Cloud project
- Verify that your OAuth consent screen is properly configured

### Permission errors

- Ensure you've granted the necessary permissions during the OAuth flow
- Check that the `contacts.readonly` scope is added to your OAuth consent screen

## License

MIT License - see LICENSE file for details
