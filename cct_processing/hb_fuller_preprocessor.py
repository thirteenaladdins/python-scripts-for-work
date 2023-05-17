# there are two things, first we need to fetch the appropriate columns
# this maps the data and formats the information into the appropriate format, 
# we can use the CCT json data structure to 

# this might have to be moved out of this folder, but I'll keep it here for now

# from the top - input the file
# select the sheet
# then process the file -
# submit the file to SFTP server

# this is for 912 and 914
# in the BIS mapping then process the file based on necessary parameters
# quantity rounded up to the nearest integer
# addresses on the item level
# addresses are added based on the plant name

# information we need from the file
# can we send addresses at the item level here?
# the rest can be added in the mapping
# additional information can be supplied in the json - such as Y CLE etc

# turn this into a command line script

address_data_table = {
    "Blois": ["FRHBFBLO01", "HB FULLER", "ALLEE ROBERT SCHUMAN C.S 1308", "BLOIS", "41013", "FR"],
    "Lueneburg": ["DEHBFLUE01", "H.B. Fuller Deutschland GmbH", "An der Roten Bleiche 2-3", "Lueneburg", "21335", "DE"],
    "Pianezze": ["ITHBFPIA01", "HB Fuller", "VIA DEL INDUSTRIA 8", "PIANEZZE", "36060", "IT"],
    "Nienburg": ["DEHBFNIE01", "HB FULLER DEUTSCHLAND PRODUKTIONS", "HENRIETTENSTRASSE 32", "NIENBURG", "31582", "DE"],
    "Mindelo": ["PTHBFMIN01", "HB FULLER", "Estrada Nacional 13/km16", "Mindelo", "4486-851", "PT"]
};

# HB Fuller specific columns
# fetch these columns, map them to the correct part of the data structure
selected_columns = ["Plant Name", "Currency", "General description", "Qty Shipped Net Weight KG", 
"Sales Order Nbr", "Number Pieces", "Date Creation Record", "Customs Value", 
"10-Digit UK Import", "Country Of Origin", "EORI Nbr"
];

# read workbook - 
# output sheet names
# select sheets

# then process 
# output to command line

import pandas as pd
import openpyxl as openpyxl
import sys
import curses

# df = pd.read_excel(input_file, dtype=str)
# valid_row_threshold = 10
# df_cleaned = df.dropna(thresh=valid_row_threshold)

# df = pd.read_excel(excel_workbook)

def get_worksheets(input_file):
    # Get sheet names
    excel_file = pd.ExcelFile(input_file)
    sheet_names = excel_file.sheet_names
    return sheet_names

def display_menu(workbook):
    for name in workbook:
        print(name)

def get_user_selection():
    return input("Please select a worksheet: ")

# do we run the validation script and check that the information has been formatted correctly?
# probably no point starting from scratch as the work has already been done
# but it will be useful for me to do it again so I can understand it better
# we need the header data as well. 

# CCT Customer ID

def main():
    if len(sys.argv) != 2:
        print("format: python hb_fuller_preprocessor.py <filename>")
        sys.exit(1)

    else:
        excel_file = sys.argv[1]

    # input_file = sys.argv[1]
    sheet_names = get_worksheets(excel_file)
    curses.initscr()



if __name__ == "__main__":
    main()
