# python standard library
import os 
import time
import shutil
import re

# from watchdog.observers import Observer
# from watchdog.events import PatternMatchingEventHandler

# make this a function
# replace this with the windows path
magic_directory_path ="/home/mo/Magic Folder"
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

file_list = list_all_files(magic_directory_path)


for name in file_list:
    print(name)

# check for duplicates
# get most recent addition to the folder

# using this to compare the two lists. 
# If the file is in the new list but not in the old list, it is a new file
def listComparison(OriginalList: list, NewList: list):
    differencesList = [x for x in NewList if x not in OriginalList] #Note if files get deleted, this will not highlight them
    return(differencesList)

# check if the file is in the target directory
# maybe not be a file
def rename_files(file: str, target_list: list):
    # s = 'Name(something)'
    
    # whats next? 
    # for file in file_list:
    if file in target_list:
        # if split the file by the target
        if '- (' in file:
            print('File with this name already exists')
            # rename the file, increment the number
            number_in_parens = re.search('\(([^)]+)', file).group(1)
            # instead of renaming the file - just rename the file name - then move the file
            # os.rename(file + f'{int(number_in_parens) + 1}')
            new_number = str(int(number_in_parens) + 1)
            file = file.split('- (')[0] + f'- ({new_number})'
            
            # print(file)
            rename_files(file , target_list)

    else:
        print(file)
        shutil.move(magic_directory_path + f"/{file}", target_directory)
        print('File moved to target directory')




# watch file for changes
def fileWatcher(my_dir: str, pollTime: int):
    while True:
        if 'watching' not in locals(): #Check if this is the first time the function has run
            previousFileList = get_files_in_directory(target_directory)
            watching = 1
            print('First Time')
            print(previousFileList)
        
        time.sleep(pollTime)

        # get list of files from rename directory
        rename_file_list = get_files_in_directory(target_directory)
        magic_file_list = get_files_in_directory(magic_directory_path)
        # print(rename_file_list)

        file_name = magic_file_list[0]
        # if previous file list is empty
        # move file from magic directory to rename directory
        
        # comapre lists to find the new file...
        file_diff = listComparison(rename_file_list, magic_file_list)
        
        # if multiple files are added,, loop through and move to rename directory
        # recursively rename and move files
        
        rename_files(file_name, rename_file_list)
            

                    
        
            
        
        
        
        

        
        

        
        # previousFileList = newFileList
        
        # doThingsWithNewFiles(fileDiff)
        # compare file
        # print(fileDiff)

        # if the new file name matches the old file name, rename the file
        # if fileDiff in previousFileList:
        #     extension = '- 001'
        #     print('File Renamed')
        #     # rename the file
        #     os.rename(fileDiff, fileDiff + f'{extension}')
        #     # print('File Renamed')



# we could use two directories. 
# one to move the file into - one to check if the name of the file is already there

# get list from rename directory - get current file in magic folder


# now we have two processes.

if __name__ == "__main__":
    fileWatcher(magic_directory_path, 1)


# read folder name from file path
# get all files in directory - put file names into list - or tuple?
# get file name from newly added file
# compare file names in list of files

# if exists - add - (001) to file 
# check 
# if 001 exists add - (002)

# check file name - 



