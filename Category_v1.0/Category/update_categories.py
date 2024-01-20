"""

After applying settings using GUI app
this script will make changes accordingly
Previous links or categories will be cleared
new settings will be applied

"""
import os
import json
from shutil import rmtree
import pathlib

def settings_fromfile():
    with open('category_settings.json','r') as f:
        categories = json.load(f)

    with open('extension_settings.json','r') as f:
        extensions = json.load(f)

    with open('path_settings.json', 'r') as f:
        paths = json.load(f)

    return categories,extensions,paths['paths'],paths['dirs']

def apply():
    categories,extensions,paths,dirs = settings_fromfile()
    """
    we'll loop through list of paths selected by user 
    and categorize them as per categories and extensions
    """
    for dir in dirs.values():
        try:
            rmtree(dir)
        except:
            pass

    for path in paths:
        for root,subdirectories,files in os.walk(path):
            for subdirectory in subdirectories:
                os.path.join(root,subdirectory)
            for file in files:
                for data_type in extensions:
                    if pathlib.Path(file).suffix in extensions[data_type] and categories[data_type] == 1:
                        if extensions[data_type][pathlib.Path(file).suffix] == 1:
                            try:
                                print("ln -sr " + os.path.join(root, file) + " " + dirs[data_type])
                                #os.system("ln -sr "+os.path.join(root,file)+" "+dirs[data_type])
                            except:
                                pass
    return "completed"
