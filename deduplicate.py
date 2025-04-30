from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from collections import Counter
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')

# allows read-only access to Google Docs and Drive
SCOPES = [
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

def authenticate():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)   # this is so the program doesn't have to ask for creds more than once!
    if not creds or not creds.valid:    # .valid is a Boolean attribute of the Credentials object provided by the Credentials class
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)   # opens a browser window to let you log into your Google account and approve access
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return creds

def extract_words_from_doc(document_id):
    creds = authenticate()
    service = build('docs', 'v1', credentials=creds)
    doc = service.documents().get(documentId=document_id).execute()
    content = doc.get('body', {}).get('content', [])

    singular_words = set()   # using a set to avoid duplicates
    all_words = [] # using a list to consider duplicates
    for element in content:
        if 'paragraph' in element:
            for elem in element['paragraph']['elements']:
                text_run = elem.get('textRun')
                if text_run:
                    text = text_run.get('content', '')
                    clean_text = text.lower().strip()
                    if clean_text:  # checks whether clean_text is a non-empty string
                        singular_words.add(clean_text)
                        all_words.append(clean_text) 

    word_counts = Counter(all_words)
    duplicates_only = {word: count for word, count in word_counts.items() if count > 1}
    sorted_duplicates = sorted(duplicates_only.items(), key=lambda x: x[1], reverse=True)

    return all_words, list(singular_words), sorted_duplicates

if __name__ == '__main__':
    document_id = input("Enter your Google Doc ID (that's the the long string of letters and numbers in the URL of your document, after https://docs.google.com/document/d/!):").strip()
    all_words, singular_words, sorted_duplicates = extract_words_from_doc(document_id)
    print(f"\nFound {len(singular_words)} unique words!")
    print(f"\nFound {len(all_words)} words!")
    print("\nWords that appear more than once:\n")  # Shows only duplicates (count > 1), sorted by frequency
    for word, count in sorted_duplicates:
        print(f"{word}: {count}")


