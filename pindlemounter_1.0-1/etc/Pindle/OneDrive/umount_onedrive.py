import json
import os

try:
	with open("/etc/Pindle/OneDrive/onedrive_conf.json",'r') as f:
		mounts = json.load(f)

	for mount_point in mounts.values():
		os.system("fusermount -u {}".format(mount_point))
except:
	pass
