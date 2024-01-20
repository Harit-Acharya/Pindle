import io
from Google import Create_Service
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import os

def search(api,stype,sname):
    fid = ''
    if stype == 'file':
        query = "mimeType != 'application/vnd.google-apps.folder' and name contains '{}'".format(sname)
    else:
        query = "mimeType = 'application/vnd.google-apps.folder' and name contains '{}'".format(sname)
    page_token = None
    while True:
        print("in loop")
        response = api.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()
        for file in response.get('files', []):
            # Process change
            if file.get('name') == sname:
                fid = file.get('id')
                break
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return fid

def download(api,filename,destination,type):
    fileid = search(api,type,filename)
    request = api.files().get_media(fileId=fileid)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fd=fh, request=request )
    done = False
    while not done:
        status, done = downloader.next_chunk()
    fh.seek(0)
    with open(os.path.join(destination,filename),'wb+') as f:
        f.write(fh.read())
        f.close()

def upload(api,filename,parent,type):
    folder_id = search(api,type,os.path.basename(filename))
    if folder_id == "":
        fid = search(api,'folder',parent)
        file_metadata = {
            "name": os.path.basename(filename),
            "parents":[fid]
        }
        media = MediaFileUpload(filename, resumable=True)
        file = api.files().create(body=file_metadata, media_body=media, fields='id').execute()
    else:
        file_metadata = {
            "name": os.path.basename(filename)
        }
        media = MediaFileUpload(filename, resumable=True)
        file = api.files().update(fileId=folder_id,body=file_metadata, media_body=media, fields='id').execute()

def authenticate():
    CLIENT_SECRET_FILE = 'credentials.json'
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']
    api = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    return api

def create_folder(api,parent,name,type):
    fid = search(api,type,parent)
    file_metadata = {
        "name": name,
        'mimeType': 'application/vnd.google-apps.folder',
        "parents": [fid]
    }
    file = api.files().create(body=file_metadata,fields='id').execute()

def delete(api,name,type):
    file_id = search(api,type,name)
    try:
        api.files().delete(fileId=file_id).execute()
    except:
        pass