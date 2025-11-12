#!/usr/bin/env python3
"""
Google Contacts Exporter

Exports Google Contacts to CSV with creation and update timestamps
using the Google People API.
"""

import os
import sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd


# OAuth 2.0 scopes
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

# API configuration
API_NAME = 'people'
API_VERSION = 'v1'
TOKEN_FILE = 'token.json'
CLIENT_SECRET_FILE = 'client_secret.json'
OUTPUT_FILE = 'contacts_with_timestamps.csv'


def authenticate():
    """Authenticate with Google People API using OAuth 2.0."""
    creds = None
    
    # Check if token.json exists
    if os.path.exists(TOKEN_FILE):
        print("Loading existing credentials...")
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                print(f"Error: {CLIENT_SECRET_FILE} not found!")
                print("Please download your OAuth 2.0 Client ID credentials from")
                print("Google Cloud Console and save it as 'client_secret.json'")
                sys.exit(1)
            
            print("Starting OAuth authentication flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        print(f"Saving credentials to {TOKEN_FILE}...")
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds


def get_primary_value(items, key='value'):
    """Extract primary value from a list of items."""
    if not items:
        return ''
    
    # Find primary item
    for item in items:
        if item.get('metadata', {}).get('primary', False):
            return item.get(key, '')
    
    # If no primary, return first item's value
    return items[0].get(key, '')


def extract_contact_data(person):
    """Extract contact information from a person object."""
    # Extract name
    names = person.get('names', [])
    name = get_primary_value(names, 'displayName') or get_primary_value(names, 'givenName')
    
    # Extract email
    emails = person.get('emailAddresses', [])
    email = get_primary_value(emails, 'value')
    
    # Extract phone
    phones = person.get('phoneNumbers', [])
    phone = get_primary_value(phones, 'value')
    
    # Extract organization
    organizations = person.get('organizations', [])
    org_name = ''
    org_title = ''
    if organizations:
        # Find primary organization
        primary_org = None
        for org in organizations:
            if org.get('metadata', {}).get('primary', False):
                primary_org = org
                break
        
        if not primary_org:
            primary_org = organizations[0]
        
        org_name = primary_org.get('name', '')
        org_title = primary_org.get('title', '')
    
    # Extract metadata timestamps
    create_time = ''
    update_time = ''
    
    metadata = person.get('metadata', {})
    sources = metadata.get('sources', [])
    
    # Find CONTACT source
    contact_source = None
    for source in sources:
        if source.get('type') == 'CONTACT':
            contact_source = source
            break
    
    # If no CONTACT source found, use first source as fallback
    if not contact_source and sources:
        contact_source = sources[0]
    
    if contact_source:
        update_time = contact_source.get('updateTime', '')
        # createTime may not always be present
        create_time = contact_source.get('createTime', '')
    
    return {
        'Name': name,
        'Email': email,
        'Phone': phone,
        'Organization': org_name,
        'Title': org_title,
        'Created': create_time,
        'Updated': update_time
    }


def retrieve_all_contacts(service):
    """Retrieve all contacts from Google People API with pagination."""
    all_contacts = []
    page_token = None
    
    print("Retrieving contacts from Google People API...")
    
    try:
        while True:
            # Prepare request parameters
            request_params = {
                'resourceName': 'people/me',
                'personFields': 'metadata,names,emailAddresses,phoneNumbers,organizations',
                'pageSize': 1000
            }
            
            if page_token:
                request_params['pageToken'] = page_token
            
            # Make API request
            results = service.people().connections().list(**request_params).execute()
            
            connections = results.get('connections', [])
            all_contacts.extend(connections)
            
            print(f"Retrieved {len(connections)} contacts (total: {len(all_contacts)})...")
            
            # Check for next page
            page_token = results.get('nextPageToken')
            if not page_token:
                break
        
        print(f"Successfully retrieved {len(all_contacts)} contacts in total.")
        return all_contacts
    
    except HttpError as error:
        print(f"An error occurred while retrieving contacts: {error}")
        sys.exit(1)


def export_to_csv(contacts):
    """Export contacts to CSV file."""
    if not contacts:
        print("No contacts to export.")
        return
    
    print("Processing contact data...")
    
    # Extract data from all contacts
    contact_data = []
    for person in contacts:
        contact_data.append(extract_contact_data(person))
    
    # Create DataFrame
    df = pd.DataFrame(contact_data)
    
    # Export to CSV
    print(f"Exporting to {OUTPUT_FILE}...")
    df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    
    print(f"Successfully exported {len(contact_data)} contacts to {OUTPUT_FILE}")


def main():
    """Main function."""
    print("=" * 60)
    print("Google Contacts Exporter")
    print("=" * 60)
    print()
    
    # Authenticate
    print("Authenticating...")
    creds = authenticate()
    
    # Build service
    print("Initializing Google People API service...")
    try:
        service = build(API_NAME, API_VERSION, credentials=creds)
    except Exception as e:
        print(f"Error initializing API service: {e}")
        sys.exit(1)
    
    # Retrieve contacts
    contacts = retrieve_all_contacts(service)
    
    # Export to CSV
    export_to_csv(contacts)
    
    print()
    print("=" * 60)
    print("Export completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    main()

