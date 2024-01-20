import json
import os

with open("/etc/Pindle/OneDrive/onedrive_conf.json",'r') as f:
    mounts = json.load(f)

for mail_id,mount_point in mounts.items():
    os.system("python3 /usr/bin/onedrivefs.py {} {}".format(mail_id,mount_point))
