import time
import threading
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import logging
import json
import os

def getusr_paths():
    with open('path_settings.json','r') as f:
        paths = json.load(f)
    return paths['paths']

def get_from_file():
    with open('category_settings.json') as f:
        categories = json.load(f)

    with open('extension_settings.json') as f:
        extensions = json.load(f)

    return extensions,categories

def FindFormat(filename):
    extensions,categories = get_from_file()
    format_of = os.path.splitext(filename)[-1]
    for data_type in extensions:
        if format_of[1:] in extensions[data_type] and categories[data_type]==1:
            if extensions[data_type][format_of[1:]]==1:
                return data_type
    return 'NIL'

class Event(LoggingEventHandler):
    @staticmethod
    def on_any_event(event, **kwargs):
        if event.is_directory:
            return None
        #Create a watchdog in Python to look for filesystem changes 
        elif event.event_type == 'created':
            # Event is created, you can process it now ``
            file_path_with_name = event.src_path
            category = FindFormat(file_path_with_name)
            if category != 'NIL': 
                command = f'sudo ln -s {file_path_with_name} /root/{category}'
                print(command)
                #os.system(command)

        elif event.event_type == 'deleted':
            #Event is modified, you can process it now
            file_path_with_name = event.src_path
            filename = os.path.basename(file_path_with_name)
            category = FindFormat(filename)
            if category != 'NIL': 
                command = f'rm -f /root/{category}/{filename}'
                print(command)
                #os.system(command)
        
        elif event.event_type == 'moved':
            file_src,file_dst = os.path.basename(event.src_path),os.path.basename(event.dest_path)
            src_path = os.path.dirname(os.path.abspath(event.src_path))
            dst_path = os.path.dirname(os.path.abspath(event.dest_path))
            if src_path == dst_path:
                category = FindFormat(file_src)
                if category != 'NIL':
                    command = f'rm /root/{category}/{file_src}'
                    print(command)
                    #os.system(command)
                    command = f'sudo ln -sr {file_dst} /{category}'
                    print(command)
                    #os.system(command)
			
paths = getusr_paths()

event_handler = Event()

watcher = Observer()
threads = [] 

for i in paths:
    targetPath = i
    print(i)
    watcher.schedule(event_handler, targetPath, recursive=True)
    threads.append(watcher)

watcher.start()

# try:
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     watcher.stop()

watcher.join()
