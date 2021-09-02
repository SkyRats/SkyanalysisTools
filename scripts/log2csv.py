import os
import io
import shutil

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload


PROJECT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
TMP_DIR = os.path.join(PROJECT_DIR, 'tmp')
LOGS_DIR = os.path.join(PROJECT_DIR, 'logs')


def check_dir(dir):
    e = os.path.exists(dir)
    if not e:
        print("Creating directory", dir)
        os.makedirs(dir)
    return e

def login():
    """Logs in to Google API and returns a service object"""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    check_dir(os.path.join(TMP_DIR))
    token_path = os.path.join(TMP_DIR, 'token.json')
    credentials_path = os.path.join(PROJECT_DIR, 'credentials.json')
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.file']

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(token_path, 'w') as token:
            token.write(creds.to_json()) # Save the credentials for the next run

    service = build('drive', 'v3', credentials=creds)
    return service

def listFiles(service):
    pass
    # filesIDS = []
    # listed = drive.ListFile().GetList()
    # for file in listed:
    #     filesIDS = file['id']
    #     print(file['id'])

def download(drive_service):
    file_id = '1HKJueorr0Asuu9xRUl8iXg5KIDgep1BY'
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download " + str(int(status.progress() * 100)))
        



'''
function listFiles() {
  var files = DriveApp.getFiles();
  while ( files.hasNext() ) {
    var file = files.next();
    Logger.log( file.getName() + ' ' + file.getId() );
  }
}  
'''

def readDirs():
    dirs = []
    file = open("./dirs.txt", 'r')
    with file as reader:
        dir = reader.readline()
        while dir != '':
            dir = reader.readline()
            print(dir)
            dirs.append('./logs/' + dir)
    return dirs

def process_ulg(filepath):
    """Converts a .ulg file into CSV files and split them into the corresponding folders
    
    Parameters
    ----------
    filepath: str
        Absolute filepath to the ULOG file to be processed
    """
    print("Processing", filepath)
    # Check is csv temporary folder exists and is empty
    csv_dir = os.path.join(TMP_DIR, 'csv')
    e = check_dir(csv_dir)
    if e and not os.listdir(csv_dir):
        print("Directory", csv_dir, "not empty, deleting all contents")
        for f in os.listdir(csv_dir):
            os.remove(os.path.join(csv_dir, f))

    # Convert ulg to csv
    print("Converting ulg to csv")
    os.system(f"ulog2csv -o {csv_dir} {filepath}")

    # Moving csv to folders 
    print("Moving files to appropriate folders")
    filename = os.path.basename(filepath)[:-4]
    for csv in os.listdir(csv_dir):
        log_dir = os.path.join(LOGS_DIR, csv[len(filename)+1:-4])
        check_dir(log_dir)
        # TODO: No momento o programa não confere se o arquivo já existe. O que fazer?
        shutil.move(os.path.join(csv_dir, csv), os.path.join(log_dir, f'{filename}.csv')) 
    # Move ulg to folder
    ulg_dir = os.path.join(LOGS_DIR, 'ulg')
    check_dir(ulg_dir)
    shutil.move(filepath, os.path.join(ulg_dir, f'{filename}.ulg'))
    print("Done!")


def process_all(unprocessed_dir):
    for f in os.listdir(unprocessed_dir):
        if f != ".gitkeep":
            process_ulg(os.path.join(unprocessed_dir, f))


def main():
    process_all(os.path.join(PROJECT_DIR, 'unprocessed'))


if __name__ == '__main__':    
    main()

    # ========== TESTES ================
    # service = login()
    # download(service)

    # # Call the Drive v3 API
    # results = service.files().list(
    #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
    # items = results.get('files', [])

    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print(u'{0} ({1})'.format(item['name'], item['id']))

    # request = service.files().get_media(fileId=items[0]['id'])
    # fh = io.BytesIO()
    # downloader = MediaIoBaseDownload(fh, request)
    # done = False
    # while done is False:
    #     status, done = downloader.next_chunk()
    #     print("Download " + str(int(status.progress() * 100)))