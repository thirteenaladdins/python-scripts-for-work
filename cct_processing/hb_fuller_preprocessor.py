from PyInquirer import prompt
import pandas as pd
import sys

# this should be the interface, and then the hb fuller processor should be a separate file

# this preprocessor converts to the json file header
# so it creates a dataframe with the specified headers
# then the map to cct json file processes


# TODO:
#

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

# Select relevant columns
# item data
# workout what validation I should add to the data mapping

# basically if I can use this script for something else I should take out
# reusable parts and add them elsewhere

# TODO:add some additional validation -
# I do have a validation module but it's not finished

# check number of pieces are not in decimals

# after processing is done, transmit the file to sftp server - separate script.

# add this automatically based on the data we have
# fetch EUR exchange rate based on HMRC data

# the other thing is that we're assuming that someone is always going to use
# the HBF preprocessor

additional_header_data = {
    "interfaceVersion": "4.2",  # no additions needed # mandatory
    "customerIdCCT": "",
    "customerEmail": "mamer@als-cs.com",  # no additions needed # mandatory
    "customerReference": '',  # get this from the CLI
    "deliveryTerm_SAD20": "",  # fetch this data from the worksheet after selection is made
    # fetch this data from the worksheet - we can only pick one
    "deliveryTermPlace_SAD20": "",
    "countryOfExport_SAD15": "",  # pick the first?
    "countryOfDestination_SAD17": "",  # pick the first?
    "totalPackages_SAD06": "",  # sum of quantity in each line - sum this after the data
    "purchaseCountry_SAD11": "",  # pick first? Mandatory field
    "totalAmountInvoiced_SAD22": "",
    # highlight if there are multiple currencies in worksheet
    "totalAmountInvoicedCurrency_SAD22": ""
    # "totalGrossMass": 2914.0,  # sum of weight column - optional

}


# add invioce addresses? -
selected_columns = ["Plant Name",
                    "Sales Order Nbr",
                    "Incoterms",
                    "10-Digit UK Import",
                    "Number Pieces",
                    "Qty Shipped Net Weight KG",
                    "Customs Value",
                    "Currency",
                    "Country Of Origin",
                    "General description",
                    "Date Creation Record",
                    "EORI Nbr"]


# create table here
# can this be added in the BIS server instead? I can't see anything in the CCT Json that allows
# item level addresses
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

# is there any point of doing this?

# rename dataframe column names to CCT names

# check delivery terms


def process_excel(df):
    # rename columns to json schema headers
    # preprocess

    # "sequentialNo_SAD32": 6,
    # df.index = df.index.rename('sequentialNo_SAD32')
    # Create the new column
    df.insert(0, 'sequentialNo_SAD32', range(1, len(df) + 1))

    df.rename(columns={"Currency": "goodsValueCurrency"}, inplace=True)
    df.rename(
        columns={"General description": "goodsDescription_SAD31"}, inplace=True)
    df.rename(
        columns={"Qty Shipped Net Weight KG": "netMass_SAD38"}, inplace=True)

    # copy net weight to gross weight column
    df.rename(
        columns={"Qty Shipped Net Weight KG": "netMass_SAD38"}, inplace=True)

    #  grossMass_SAD35
    df.rename(
        columns={"General description": "goodsDescription_SAD31"}, inplace=True)
    df.rename(columns={"Number Pieces": "noOfPackages_SAD31"}, inplace=True)
    df.rename(
        columns={"10-Digit UK Import": "customerHSCode_SAD33im"}, inplace=True)
    df.rename(columns={"Customs Value": "itemPrice_SAD42"}, inplace=True)
    df.rename(
        columns={"Customs Value": "itemPrice_SAD42"}, inplace=True)
    df.rename(
        columns={"Country Of Origin": "countryOfOrigin_SAD34"}, inplace=True)
    df.rename(
        columns={"Sales Order Nbr": "invoiceNo"}, inplace=True)
    df['grossMass_SAD35'] = df['netMass_SAD38']

    # "Date Creation Record" - ???
    return df


# Add to invoice addresses
# for each line in the address, create a node in invoice addresses

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


# TODO:

# scan through Delivery terms data -
# create options based on the delivery terms for HBF -
# this will be in the HBF pre-processor

# Initialize a CustomsOrder
customs_order = {
    "addresses": [],
    "positions": [],
    "invoices": [],
}

# format CustomsOrder{
# "addresses": [
# ],
# "positions": [
# ]
# "invoices": [
# ]
#
#
# }
# convert data types
# add header data
# add address data
# add invoices
# format quantities to not be decimals

# I don't want to do too much in my own script, I want to s


def add_header_data():
    pass


def convert_df_to_json(df):
    # df.to_json()
    df.to_json('output.json', orient='records')

    #


# TODO: come back and amend this
# this will just have to match the 912 Reference, to be added as the importer
# setup in CCT
hbf_customers = [
    'HBF912UK (912)',
    'HBF914UK (914)'
]


def main(input_file):
    menu = get_worksheets(input_file)
    questions = [
        {
            'type': 'list',
            'name': 'sheet',
            'message': 'Select a sheet:',
            'choices': menu
        },
        {
            'type': 'input',
            'name': 'valid_row_threshold',
            'message': 'Enter the minimum number of non-null values in a row:',
            'validate': lambda val: val.isdigit() and int(val) > 0,
            'filter': lambda val: int(val)
        },
        {
            'type': 'input',
            'name': 'user_input',
            'message': 'Please enter Reference [box 7]:'
        },
        {
            'type': 'list',
            'name': 'customer_list',
            'message': 'Select a customer',
            'choices': hbf_customers
        }
    ]

    answers = prompt(questions)
    df = read_excel(input_file, answers['sheet'])
    df_remove_null = df.dropna(thresh=answers['valid_row_threshold'])
    additional_header_data['customerReference'] = answers['user_input']

    # FIXME: pass this data in from a separate script
    additional_header_data['customerReference'] = answers['user_input']
    additional_header_data['customerIdCCT'] = answers['customer_list']

    incoterms = df['Incoterms'].unique().tolist()

    # if there is more than one set of incoterms -

    questions = [
        {
            'type': 'list',
            'name': 'incoterm',
            'message': 'Select an incoterm:',
            'choices': incoterms
        }
    ]

    answers = prompt(questions)

    print('Selected incoterm:', answers['incoterm'])

    # if "incoterms" exists in dataset, then look at the list
    # processing...
    # prompt - analyse the incoterm
    # week 18, week 19 etc.

    # if there are multiple eori numbers in the dataset - prompt the user

    # if df['incoterm']

    # print(df.head())  # Now this line will print to the terminal normally
    df_subset = df_remove_null[selected_columns].copy()

    processed_df = process_excel(df_subset)

    print(df_subset)

    print(f"Succesfully processed json file")
    # output json file in json structure

    # do you want to transmit to CCT?

    convert_df_to_json(processed_df)

    # process the file here


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("format: python hb_fuller_preprocessor <excel workbook>")
        sys.exit(1)

    main(sys.argv[1])
