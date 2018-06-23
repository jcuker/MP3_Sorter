import mutagen
import os
import re
import errno
import shutil
import sys
import codecs
import time
import getpass
from unidecode import unidecode

# globals
start_time = None
last_interval = None
success_count = 0
fail_count = 0
file = None
recurse = False
path = None
dest_path = None
overwriting_dir = False

# remove all illegal windows pathname chars ->  \ / : " * ? < > |
def format_string(s):
    pattern = None
    if os.name == 'nt':
        pattern = r'[\\/:"*?<>|]+'
    else:
        pattern = r'/'
    temp = re.sub(pattern, "", s)
    # whitespace at the end of a pathname causes errors
    if temp.endswith(" "):
        temp = temp[:-1]
    # same with newline chars, but why would this exist?
    if temp.endswith("\r\n"):
        temp = temp[:-2]
    elif temp.endswith("\n"):
        temp = temp[:-1]
    return temp


# TODO - this function needs to be refactored to handle unix and windows
def process_directory(path):
    global success_count
    global fail_count
    global file
    global start_time
    global last_interval
    global dest_path
    global generate_logs
    global recurse
    global overwriting_dir

    for file_name in os.listdir(path):
        if int(time.time() - last_interval) >= 15:
            print("Still working - no need to panic! Processed " + str(success_count + fail_count) + " files so far.")
            last_interval = time.time()

        full_path = path + file_name

        if os.path.isdir(full_path) and recurse:
            if os.name == 'nt':
                process_directory(full_path + '\\')
            else:
                process_directory(full_path)
            try:
                os.rmdir(full_path)
            except OSError:
                continue
        elif os.path.isdir(full_path):
            continue

        try:
            obj = mutagen.File(full_path)
        except:
            continue

        if not isinstance(obj, mutagen.FileType):
            continue

        artist = ""
        album = ""

        if 'TPE2' in obj.tags:
            artist = format_string(str(obj.tags["TPE2"]))
        elif 'TCOM' in obj.tags:
            artist = format_string(str(obj.tags["TCOM"]))
        elif 'TPE1' in obj.tags:
            artist = format_string(str(obj.tags["TPE1"]))
        else:
            artist = "Unknown Artist"

        if 'TALB' in obj.tags:
            album = format_string(str(obj.tags["TALB"]))
        elif 'TOAL' in obj.tags:
            album = format_string(str(obj.tags["TOAL"]))
        else:
            album = "Unknown Album"

        artist_folder_path = None
        if os.name == 'nt':
            artist_folder_path = dest_path + artist + '\\'
        else:
            artist_folder_path = dest_path + artist + '/'
        
        album_folder_path = artist_folder_path + album 

        # check to see if artist directory exists
        if( not os.path.isdir(artist_folder_path)):
            try:
                os.makedirs(artist_folder_path)
                if generate_logs:
                    file.write(unidecode("Created " + artist + " folder.\n"))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        # check to see if album directory exists
        if( not os.path.isdir(album_folder_path)):
            try:
                os.makedirs(album_folder_path)
                if generate_logs:
                    file.write(unidecode("Created " + album + " folder under " + artist + " folder.\n"))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        try:
            shutil.move(full_path, album_folder_path)
            if generate_logs:
                file.write(unidecode("Successfully moved " + file_name + " to " + album_folder_path + '\n'))
            success_count += 1
        except Exception as e:
            if(overwriting_dir):
                file.write(unidecode("Successfully processed " + file_name + ". No need to move as it's already in correct location " + '\n'))
                success_count += 1
            else:            
                if generate_logs:
                    file.write(unidecode("Error with following -> album: " + album + " Artist: " + artist + '\n'))
                    file.write(unidecode(full_path + " : " + album_folder_path + "\n"))
                fail_count += 1
            continue

def initWindows():
    global recurse
    global path
    global file
    global dest_path
    global generate_logs
    global overwriting_dir

    path = input("Directory to work in? EX. C:\\Users\\" + getpass.getuser() + "\\Music\\\n")
    if not path.endswith('\\'):
        path += '\\'
    if not os.path.isdir(path):
        print("Path is not valid.")
        sys.exit()

    os.system('cls')
    recurse = input("Recurse through all internal directories? (y/n)\n")
    if recurse.lower() == 'y':
        recurse = True
    else:
        recurse = False
    
    os.system('cls')
    dest_path = input("Directory to save to? Note: will create if doesn't exist.\n")
    if not dest_path.endswith('\\'):
        dest_path += '\\'
    if not os.path.isdir(dest_path):
        try:
            os.makedirs(dest_path)
        except:
            print("Path is not valid.")
            sys.exit()

    if(path == dest_path):
        overwriting_dir = True

    os.system('cls')
    generate_logs = input("Generate usage logs? (y/n)\n")

    if generate_logs.lower() == 'y':
        generate_logs = True
    else:
        generate_logs = False

    os.system('cls')
    print("Working in " + path)
    print("Moving files to " + dest_path)
    stop = input("Is this correct? (y/n)\n")
    stop = stop.lower()
    if stop != 'y':
        print("Exiting before doing any work.")
        sys.exit()

    if generate_logs:
        try:
            # remove prev logs if exist
            open(os.path.join(dest_path, 'MP3Sorter_log.txt'), 'w+').close()
            file = open(os.path.join(dest_path, 'MP3Sorter_log.txt'), "a+")
        except:
            generate_logs = 'n'

def initLinux():
    global recurse
    global file
    global path
    global dest_path
    global generate_logs

    path = input("Directory to work in? EX. /home/" + getpass.getuser() + "/Music \n")
    
    if not os.path.isdir(path):
        print("Path is not valid.")
        sys.exit()

    os.system('clear')
    recurse = input("Recurse through all internal directories? (y/n)\n")
    if recurse.lower() == 'y':
        recurse = True
    else:
        recurse = False
    
    os.system('clear')
    dest_path = input("Directory to save to? Note: will create if doesn't exist.\n")
    if not os.path.isdir(dest_path):
        try:
            os.makedirs(dest_path)
        except:
            print("Path is not valid.")
            sys.exit()

    os.system('clear')
    generate_logs = input("Generate usage logs? (y/n)\n")
    if generate_logs.lower() == 'y':
        generate_logs = True
    else:
        generate_logs = False

    os.system('clear')
    print("Working in " + path)
    print("Moving files to " + dest_path)
    stop = input("Is this correct? (y/n)\n")
    stop = stop.lower()
    if stop != 'y':
        print("Exiting before doing any work.")
        sys.exit()

    # ensure path has the necessary appended char after printing
    if not path.endswith('/'):
        path += '/'
    if not dest_path.endswith('/'):
        dest_path += '/'

    if generate_logs:
        try:
            # remove prev logs if exist
            open(os.path.join(dest_path, 'MP3Sorter_log.txt'), 'w+').close()
            file = open(os.path.join(dest_path, 'MP3Sorter_log.txt'), "a+")
        except:
            generate_logs = 'n'

def main():
    global success_count
    global fail_count
    global start_time
    global last_interval
    global recurse
    global path
    global dest_path
    global generate_logs

    if(os.name == 'nt'):
        initWindows()
    else:
        initLinux()

    start_time = time.time()
    last_interval = start_time
    
    print("Starting ...")
    process_directory(path)

    run_time = time.time() - start_time

    os.system('cls' if os.name == 'nt' else 'clear')
    print("Successfully processed " + str(success_count) + " files with " + str(fail_count) + " failures in " + str(int(run_time)) + " seconds.")
    if generate_logs:
        if os.name == 'nt':
            print("Log file located at " + dest_path + "MP3Sorter_log.txt")
        else:
            print("Log file located at " + dest_path + "MP3Sorter_log.txt")
        
main()