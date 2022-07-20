# python standard library
import os 
import time
import shutil

# from watchdog.observers import Observer
# from watchdog.events import PatternMatchingEventHandler

# make this a function
# replace this with the windows path
magic_directory_path ="/home/mo/Magic Folder"
directory_renamed_files = "/home/mo/Rename Directory"

#we shall store all the file names in this list

from os import listdir
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


# watch file for changes
def fileWatcher(my_dir: str, pollTime: int):
    while True:
        if 'watching' not in locals(): #Check if this is the first time the function has run
            previousFileList = get_files_in_directory(directory_renamed_files)
            watching = 1
            print('First Time')
            print(previousFileList)
        
        time.sleep(pollTime)

        # get list of files from rename directory
        rename_file_list = get_files_in_directory(directory_renamed_files)
        magic_file_list = get_files_in_directory(magic_directory_path)
        # print(rename_file_list)

        
        # comapre lists to find the new file...
        fileDiff = listComparison(rename_file_list, magic_file_list)
        print(fileDiff)
        
        if fileDiff not in rename_file_list:    
            shutil.move(magic_directory_path + f"/{fileDiff}", directory_renamed_files)
            print('File moved')
        else:
            continue
        
        
        # previousFileList = newFileList
        # if len(fileDiff) == 0: continue
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



