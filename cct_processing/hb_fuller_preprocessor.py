from PyInquirer import prompt
import pandas as pd
import sys

# this should be the interface, and then the hb fuller processor should be a separate file

# this preprocessor converts to the json file header
# so it creates a dataframe with the specified headers
# then the map to cct json file processes

# Select relevant columns
# item data
selected_columns = ["Plant Name", "Currency", "General description", "Qty Shipped Net Weight KG",
                    "Sales Order Nbr", "Number Pieces", "Date Creation Record", "Customs Value",
                    "10-Digit UK Import", "Country Of Origin", "EORI Nbr"]

# additional header data
# totalPackages_SAD06 - sum of total packages

# #### Mandatory Header Data

# interfaceVersion
# customerIdCCT
# customerEmail
# customerReference
# deliveryTerm_SAD20
# deliveryTermPlace_SAD20
# countryOfExport_SAD15
# countryOfDestination_SAD17

# role
# eoriNo
# vatNo
# customerAddressNo
# mdmAddressNo
# invoicingAddressNo
# accountNo
# name1
# name2
# name3
# street
# houseNo
# zipcode
# city
# country
# province
# postofficeBox
# traderid
# unlocode
# reference
# contactName
# email
# phone

# "sequentialNo_SAD32": 6,
# "invoiceNo": "SI-A014216",
# "itemNo": "TG7X50610/BE/08A",
# "customerHSCode_SAD33ex": "87163950",
# "noOfPackages_SAD31": 1,
# "grossMass_SAD35": 996.43,
# "netMass_SAD38": 860.0,
# "itemPrice_SAD42": 9263.0,
# "goodsValueCurrency": "EUR",
# "goodsDescription_SAD31": "HBX506 RIGHT HAND:",
# "countryOfOrigin_SAD34": "GB"

# plant name - this is mapped to address column data

# Position level

# Plant Name" - address data

# "sequentialNo_SAD32": 6,
# Currency" - goodsValueCurrency
# "General description" - goodsDescription_SAD31
# "Qty Shipped Net Weight KG" - netMass_SAD38, grossMass_SAD35
# "Sales Order Nbr" - invoiceNo
# "Number Pieces" - noOfPackages_SAD31
# "Date Creation Record" - ???
# "Customs Value" - itemPrice_SAD42
# "10-Digit UK Import"- customerHSCode_SAD33ex
# "Country Of Origin" - countryOfOrigin_SAD34

# "EORI Nbr - not mapped anywhere. - but we should check that the information on the
# sheet we're working with corresponds to the correct information

# there is one of these per item because it's EIDR
# to the position data?

# this is optional anyway - map one per line item, then match the data
#### Invoice data ####
# invoiceNo - Sales Order Nbr
# invoiceDate - Date Creation Record
# invoiceReference -
# invoiceAmount - Customs Value
# invoiceCurrency - Currency


# map this data to a json file?
#

# create table here
address_data_table = {
    "Blois": ["FRHBFBLO01", "HB FULLER", "ALLEE ROBERT SCHUMAN C.S 1308", "BLOIS", "41013", "FR"],
    "Lueneburg": ["DEHBFLUE01", "H.B. Fuller Deutschland GmbH", "An der Roten Bleiche 2-3", "Lueneburg", "21335", "DE"],
    "Pianezze": ["ITHBFPIA01", "HB Fuller", "VIA DEL INDUSTRIA 8", "PIANEZZE", "36060", "IT"],
    "Nienburg": ["DEHBFNIE01", "HB FULLER DEUTSCHLAND PRODUKTIONS", "HENRIETTENSTRASSE 32", "NIENBURG", "31582", "DE"],
    "Mindelo": ["PTHBFMIN01", "HB FULLER", "Estrada Nacional 13/km16", "Mindelo", "4486-851", "PT"],
}


def add_address_data(row):
    # check if address is in table
    # "Plant Name"
    address_rows = {}
    plant_names = ["Blois", "Lueneburg", "Pianezze", "Nienburg", "Mindelo"]

    for name in plant_names:
        if name in row["Plant Name"]:
            data = address_data_table[name]

            address_rows = {
                "Exporter Name": data[1],
                "Exporter Street":  data[2],
                "Exporter City": data[3],
                "Exporter PostCode": data[4],
                "Exporter Country": data[5],
                "Exporter ShortCode": data[0],
                "Dispatch Country": data[5],
                "Destination Country": 'GB',
            }

    return address_rows


def get_worksheets(input_file):
    excel_file = pd.ExcelFile(input_file)
    return excel_file.sheet_names


def read_excel(file_path, sheet_name=None):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df


def main(input_file):
    menu = get_worksheets(input_file)
    questions = [
        {
            'type': 'list',
            'name': 'sheet',
            'message': 'Select a sheet:',
            'choices': menu
        }
    ]
    answers = prompt(questions)
    df = read_excel(input_file, answers['sheet'])
    print(df.head())  # Now this line will print to the terminal normally

    # process the file here


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("format: python hb_fuller_preprocessor <excel workbook>")
        sys.exit(1)

    main(sys.argv[1])
