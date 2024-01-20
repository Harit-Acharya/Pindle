import json
import os

print("mouting strted")
with open("/etc/Pindle/GDrive/gdrive_conf.json",'r') as f:
    mounts = json.load(f)

for mail_id,mount_point in mounts.items():
    os.system("python3 /usr/bin/gdrivefs.py {} {}".format(mail_id,mount_point))

print("mounted")
