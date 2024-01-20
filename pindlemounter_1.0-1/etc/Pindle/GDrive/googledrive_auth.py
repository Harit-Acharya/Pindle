import sys
sys.path.insert(0, '/etc/Pindle/GDrive')
from Google import Create_Service
import os
import pickle

def authenticate(MAIL):
    CLIENT_SECRET_FILE = '/etc/Pindle/GDrive/credentials.json'
    API_NAME = 'drive'
    API_VERSION = 'v3'
    make = True
    SCOPES = ['https://www.googleapis.com/auth/drive']
    os.system('echo "inside authentication"')

    try:
        api = Create_Service(MAIL,CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
    except:
        os.system("sudo kill -9 $(ps -A | grep python3 | awk '{print $1}') ")

    os.system('echo "gotapi"')

    pickle_file = '/etc/Pindle/GDrive/{}_token_{}_{}.pickle'.format(MAIL,API_NAME,API_VERSION)
    if os.path.exists(pickle_file):
        with open(pickle_file, 'rb') as token:
            cred = pickle.load(token)

    os.system('echo "returning api,tokenki"')
    return api,cred.token