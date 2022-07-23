# python standard library
import os 
import time
import shutil
import re

# from watchdog.observers import Observer
# from watchdog.events import PatternMatchingEventHandler

# make this a function
# replace this with the windows path
magic_directory ="/home/mo/Magic Folder"
target_directory = "/home/mo/Rename Directory"

#we shall store all the file names in this list

from os import listdir, rename
from os.path import isfile, join

#function to return files in a directory
def get_files_in_directory(my_dir: str):
    only_files = [f for f in listdir(my_dir) if isfile(join(my_dir, f))]
    return(only_files)

# os.walk? 
# run this is in a while loop -  benchmark resource comsumption while idle

file_list = []

def list_all_files(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            #append the file name to the list
            file_list.append(os.path.join(root,file))
    return file_list

# using this to compare the two lists. 
# If the file is in the new list but not in the old list, it is a new file
def listComparison(OriginalList: list, NewList: list):
    differencesList = [x for x in NewList if x not in OriginalList] #Note if files get deleted, this will not highlight them
    return(differencesList)

# check if the new file is in the target directory
# if it is, rename the file
def rename_files(file: str, target_list: list):
    if file in target_list:
        print('File with this name already exists')
        if '- (' in file:
            # rename the file, increment the number
            number_in_parens = re.search('\(([^)]+)', file).group(1)
            # instead of renaming the file - just rename the file name - then move the file
            # os.rename(file + f'{int(number_in_parens) + 1}')

            new_number = str(int(number_in_parens) + 1)
            file = file.split('- (')[0] + f' - ({new_number.zfill(3)})'
            return rename_files(file , target_list)
        
        else: 
            return rename_files(file + ' - (001)', target_list)

    else:
        # here we return the original file if no changes 
        # have been made or the new file name
        return file


def move_file_to_target(file_name: str, new_file_name: str, current_directory: str, target_directory: str):
    if file_name != new_file_name:
        os.rename(current_directory + '/' + file_name, current_directory + '/' + new_file_name)
        shutil.move(magic_directory + f"/{new_file_name}", target_directory)
        print("File renamed")
    
    else: 
        shutil.move(magic_directory + f"/{file_name}", target_directory)
        print('File moved to target directory')


# watch file for changes
def fileWatcher(my_dir: str, pollTime: int):
    while True:
        if 'watching' not in locals(): #Check if this is the first time the function has run
            if os.path.exists(magic_directory): 
                pass
            
            else: 
                print('Magic folder does not exist... creating...')
                os.mkdir(magic_directory)

            if os.path.exists(target_directory): 
                continue

            else:
                print('Target directory does not exist... creating...')
                os.mkdir(target_directory)


            previousFileList = get_files_in_directory(target_directory)
            watching = 1
            print('First Time')
            print(previousFileList)
        
        time.sleep(pollTime)

        if os.path.exists(magic_directory): 
            continue
            
        else: 
            print('Magic folder does not exist... creating...')
            os.mkdir(magic_directory)

        if os.path.exists(target_directory): 
            continue

        else:
            print('Target directory does not exist... creating...')
            os.mkdir(target_directory)

        # get list of files from rename directory
        target_directory_file_list = get_files_in_directory(target_directory)
        magic_file_list = get_files_in_directory(magic_directory)

        # compare lists to find the new file
        # file_diff = listComparison(target_directory_file_list, magic_file_list)
        
        
        if len(magic_file_list) > 0:
            file_name = magic_file_list[0]
        
        else: 
            continue

        # generate new name for file
        new_file_name = rename_files(file_name, target_directory_file_list)
        # print(new_file_name)

        # print(file_name, new_file_name)
        # move file to target directory
        move_file_to_target(file_name, new_file_name, magic_directory, target_directory,)

        
# TODO get a file list from the current directory
# iterate through the list, work on multiple files at a time instead of one per second
        

if __name__ == "__main__":
    fileWatcher(magic_directory, 1)
