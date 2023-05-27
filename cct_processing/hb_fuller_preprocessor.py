# from PyInquirer import prompt
# from prompt_toolkit import PromptSession
# from prompt_toolkit.completion import WordCompleter
# import prompt_engine
# from prompt_toolkit.shortcuts import checkboxlist_dialog
# from prompt_toolkit import PromptSession
# from prompt_toolkit.completion import WordCompleter
# from prompt_toolkit.validation import Validator

from InquirerPy import prompt, inquirer
from InquirerPy.utils import color_print
import pandas as pd
import sys

# TODO: come back and amend this
# this will just have to match the 912 Reference, to be added as the importer
# setup in CCT
HBF_CUSTOMERS = [
    'HBF912UK (912)',
    'HBF914UK (914)'
]


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


selected_columns = ["Plant Name", "Sales Order Nbr", "Incoterms", "10-Digit UK Import", "Number Pieces",
                    "Qty Shipped Net Weight KG", "Customs Value", "Currency", "Country Of Origin",
                    "General description", "Date Creation Record", "EORI Nbr"]

address_data_table = {
    "Blois": ["FRHBFBLO01", "HB FULLER", "ALLEE ROBERT SCHUMAN C.S 1308", "BLOIS", "41013", "FR"],
    "Lueneburg": ["DEHBFLUE01", "H.B. Fuller Deutschland GmbH", "An der Roten Bleiche 2-3", "Lueneburg", "21335", "DE"],
    "Pianezze": ["ITHBFPIA01", "HB Fuller", "VIA DEL INDUSTRIA 8", "PIANEZZE", "36060", "IT"],
    "Nienburg": ["DEHBFNIE01", "HB FULLER DEUTSCHLAND PRODUKTIONS", "HENRIETTENSTRASSE 32", "NIENBURG", "31582", "DE"],
    "Mindelo": ["PTHBFMIN01", "HB FULLER", "Estrada Nacional 13/km16", "Mindelo", "4486-851", "PT"],
}


def get_worksheets(input_file):
    excel_file = pd.ExcelFile(input_file)
    return excel_file.sheet_names


def read_excel(file_path, sheet_name=None):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    return df


def process_excel(df):
    df.insert(0, 'sequentialNo_SAD32', range(1, len(df) + 1))
    df.rename(columns={"Currency": "goodsValueCurrency",
                       "General description": "goodsDescription_SAD31",
                       "Qty Shipped Net Weight KG": "netMass_SAD38",
                       "Number Pieces": "noOfPackages_SAD31",
                       "10-Digit UK Import": "customerHSCode_SAD33im",
                       "Customs Value": "itemPrice_SAD42",
                       "Country Of Origin": "countryOfOrigin_SAD34",
                       "Sales Order Nbr": "invoiceNo"}, inplace=True)
    df['grossMass_SAD35'] = df['netMass_SAD38']
    return df


def add_address_data(row):
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


def convert_df_to_json(df):
    df.to_json('output.json', orient='records', lines=True)


# change colours

def main(input_file):
    sheets = get_worksheets(input_file)
    # excel_file = pd.ExcelFile()

    # df = read_excel(input_file, sheets[])
    # print(df.columns)

    sheet = inquirer.select(
        message="Select a sheet:",
        choices=sheets
    ).execute()

    valid_row_threshold = inquirer.text(
        message="Enter the minimum number of non-null values in a row:",
        validate=lambda val: val.isdigit() and int(val) > 0,
        transformer=lambda val: int(val)
    ).execute()

    user_input = inquirer.text(
        message='Please enter Reference [box 7]:'
    ).execute()

    customer_list = inquirer.select(
        message='Select a customer',
        choices=HBF_CUSTOMERS
    ).execute()

    df = read_excel(input_file, sheet)
    df_remove_null = df.dropna(thresh=int(valid_row_threshold))

    additional_header_data['customerReference'] = user_input
    additional_header_data['customerIdCCT'] = customer_list

    week_list = df['Calendar Week'].unique().tolist()

    week_list = [str(week_number)
                 for week_number in week_list if str(week_number) != 'nan']

    week_number = inquirer.select(
        message='Select a week',
        choices=week_list
    ).execute()

    incoterms = df['Incoterms'].unique().tolist()
    incoterms = [str(incoterm)
                 for incoterm in incoterms if str(incoterm) != 'nan']

    # this is quite confusing but it works.
    while True:
        selected_incoterms = []

        while True:
            available_incoterms = [
                incoterm for incoterm in incoterms if incoterm not in selected_incoterms]

            # so we break the loop if there are no incoterms to select
            if not available_incoterms:  # All incoterms have been selected
                break

            # here is where we need to break
            answers_2 = inquirer.checkbox(
                message="Select incoterms (use Space to select, Enter to confirm) " +
                (f' (selected incoterms: {selected_incoterms})' if selected_incoterms else ''),
                choices=[{'name': incoterm, 'value': incoterm}
                         for incoterm in available_incoterms]
            ).execute()

            if not answers_2:  # If the user didn't select any new incoterm, we move on to the confirmation step
                color_print(formatted_text=[("class:red", "Please select a term ")], style={
                            "red": "red", })
            else:
                for incoterm in answers_2:
                    if incoterm not in selected_incoterms:
                        selected_incoterms.append(incoterm)

                break

        done = inquirer.confirm(
            f"You've selected these incoterms: {selected_incoterms}. Do you want to proceed?",
        ).execute()

        # TODO: come back and add formatting style for all
        if done:
            # proceed with the rest of your code
            print("You selected the following settings:")
            print(f'Selected sheet: {sheet}')
            print(
                f"Minimum number of non-null values in a row: {valid_row_threshold}")
            print(f'Reference [box 7]: {user_input}')
            print(f'Week Number: {week_number}')
            print(f'Incoterms: {selected_incoterms}')

            inquirer.confirm(
                f"Do you want to proceed?",
            ).execute()

            break

        else:
            # If 'No' was selected, the outer loop will restart the selection process
            # is there anythign to do here?
            pass

    #
    # df_subset = df_remove_null[selected_columns].copy()
    # processed_df = process_excel(df_subset)

    print(f"Succesfully processed json file")
    # convert_df_to_json(processed_df)

# allow the user to go through each of the options
# and amend any mistakes.
# TODO: print summary to user before confirmation>
# I'll add this after the processing script is done. then
# TODO: if the columns don't exist, then notify the user and then move through the options


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("format: python hb_fuller_preprocessor <excel workbook>")
        sys.exit(1)

    main(sys.argv[1])

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

# from prompt_toolkit.shortcuts import get_input

    # selected_incoterms = []
    # for i, term in enumerate(incoterms, start=1):
    #     print(f"{i}. {term}")

    # while True:
    #     for i, term in enumerate(incoterms, start=1):
    #         print(f"{i}. {term}")
    #         # print("Selected incoterms: ", selected_incoterms)

    #     choice = get_input(
    #         "Select an incoterm (by number), type 'q' to finish, or 's' to show selected: ")
    #     print('Selected incoterms: ', selected_incoterms)
    #     # if choice.lower() == 'q':
    #     #     break
    #     # elif choice.lower() == 's':
    #     #     print("Selected incoterms: ", selected_incoterms)
    #     #     continue

    #     try:
    #         selected_incoterms.append(incoterms[int(choice) - 1])
    #         print("Added: ", incoterms[int(choice) - 1])
    #     except (ValueError, IndexError):
    #         print("Invalid choice, please try again.")

    #     print("Selected incoterms: ", selected_incoterms)

    # select by week
    # Result is a list of selected items
    # print(result)

    # questions = [
    #     {
    #         'type': 'checkbox',
    #         'name': 'incoterms',
    #         'message': 'Select incoterms:',
    #         'choices': [{'name': incoterm} for incoterm in incoterms],
    #         'validate': lambda answer: 'You must select at least one incoterm.' if len(answer) == 0 else True
    #     }
    # ]

    # answers = prompt(questions)

    # print('Selected incoterms:', ', '.join(answers['incoterms']))
