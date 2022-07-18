# python standard library
import os 
import time

# from watchdog.observers import Observer
# from watchdog.events import PatternMatchingEventHandler

# make this a function
# replace this with the windows path
directory_path ="/home/mo/Magic Folder"
#we shall store all the file names in this list

from os import listdir
from os.path import isfile, join

#function to return files in a directory
def file_in_directory(my_dir: str):
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

file_list = list_all_files(directory_path)


for name in file_list:
    print(name)

# check for duplicates
# get most recent addition to the folder
    
def listComparison(OriginalList: list, NewList: list):
    differencesList = [x for x in NewList if x not in OriginalList] #Note if files get deleted, this will not highlight them
    return(differencesList)



def fileWatcher(my_dir: str, pollTime: int):
    while True:
        if 'watching' not in locals(): #Check if this is the first time the function has run
            previousFileList = file_in_directory(directory_path)
            watching = 1
            print('First Time')
            print(previousFileList)
        
        time.sleep(pollTime)
        
        newFileList = file_in_directory(directory_path)
        
        fileDiff = listComparison(previousFileList, newFileList)
        
        previousFileList = newFileList
        if len(fileDiff) == 0: continue
        # doThingsWithNewFiles(fileDiff)
        print(fileDiff)


if __name__ == "__main__":
    fileWatcher(directory_path, 10)


# read folder name from file path
# get all files in directory - put file names into list - or tuple?
# get file name from newly added file
# compare file names in list of files

# if exists - add - (001) to file 
# check 
# if 001 exists add - (002)

# check file name - 



