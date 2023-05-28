from InquirerPy import prompt, inquirer
from InquirerPy.utils import color_print
import pandas as pd
import sys

# TODO: come back and amend this
# this will just have to match the 912 Reference, to be added as the importer
# setup in CCT

# TODO:add some additional validation -
# I do have a validation module but it's not finished

# TODO: highlight if there are multiple currencies in worksheet

# TODO: allow the user to go through each of the options
# and amend any mistakes, or restart the process

# TODO: if the columns don't exist, then notify the user and then move through the options

# TODO: differentiate settings, between 912/914 and 3rd party as the headers are different
# or look for both column headers, if the first one doesn't exist, look for the second

# give an option, return the actual code
HBF_CUSTOMERS = [
    'HBF912UK',
    'HBF914UK'
]

additional_header_data = {
    "interfaceVersion": "4.2",  # no additions needed # mandatory
    "customerIdCCT": "",
    "customerEmail": "mamer@als-cs.com",  # no additions needed # mandatory
    "customerReference": '',  # get this from the CLI
    "deliveryTerm_SAD20": "",  # PICK FIRST
    "deliveryTermPlace_SAD20": "Dunkinfield",
    "countryOfExport_SAD15": "DE",  # fill with generic data - DE
    "countryOfDestination_SAD17": "GB",  # fill with generic data- GB
    "totalPackages_SAD06": "",  # sum of quantity in each line - sum this after the data
    "purchaseCountry_SAD11": "GB",  # pick first? Mandatory field

    # optional?
    "totalAmountInvoiced_SAD22": "",
    "totalAmountInvoicedCurrency_SAD22": ""

    # "totalGrossMass": 2914.0,  # sum of weight column - optional

}

# 912 / 914
selected_columns = ["Plant Name", "Sales Order Nbr", "Incoterms", "10-Digit UK Import", "Number Pieces",
                    "Qty Shipped Net Weight KG", "Customs Value", "Currency", "Calendar Week", "Country Of Origin",
                    "General description", "Date Creation Record", "EORI Nbr"]

# 912 3rd party


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

    customer = inquirer.select(
        message='Select a customer',
        choices=HBF_CUSTOMERS
    ).execute()

    df = read_excel(input_file, sheet)
    df_remove_null = df.dropna(thresh=int(valid_row_threshold))

    additional_header_data['customerReference'] = user_input
    additional_header_data['customerIdCCT'] = customer

    week_list = df['Calendar Week'].unique().tolist()

    week_list = [str(week_number)
                 for week_number in week_list if str(week_number) != 'nan']

    week_number = inquirer.select(
        message='Select a week',
        choices=week_list
    ).execute()

    df_subset = df_remove_null[selected_columns].copy()

    # filter by week
    df_subset_filtered = df_subset[df_subset['Calendar Week'] == float(
        week_number)].copy()

    incoterms = df_subset_filtered['Incoterms'].unique().tolist()
    incoterms = [str(incoterm)
                 for incoterm in incoterms if str(incoterm) != 'nan']

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

        df_filtered = df_subset_filtered[df_subset_filtered['Incoterms'].isin(
            selected_incoterms)].copy()

        # TODO: come back and add formatting style for all
        if done:
            # proceed with the rest of your code

            color_print(formatted_text=[("class:bold", "You selected the following settings: ")], style={
                "bold": "bold", })

            color_print(formatted_text=[
                        ("brown", "Selected sheet: "), ("blue bold", sheet)])

            color_print(formatted_text=[
                        ("brown", "Selected customer: "), ("blue bold", customer)])

            color_print(formatted_text=[
                        ("brown", "Minimum number of non-null values in a row: "), ("blue bold", valid_row_threshold)])
            color_print(formatted_text=[
                        ("brown", "Reference [box 7]: "), ("blue bold", user_input)])
            color_print(formatted_text=[
                        ("brown", "Week Number: "), ("blue bold", week_number)])

            color_print(formatted_text=[
                        ("brown", "Incoterms: "), ("blue bold", ', '.join(selected_incoterms))])

            finalise = inquirer.confirm(
                f"Do you want to proceed?",
            ).execute()

            if finalise:
                print(f"dataframe is {df_filtered}")
                break

            else:
                # start again
                pass

    additional_header_data["deliveryTerm_SAD20"] = selected_incoterms[0]

    # # this should be done after we have worked out which of the rows we're going to be using
    # first, go through

    import math

    def round_up_and_convert(value):
        if value == 0:
            return 1
        elif math.isclose(value, int(value)):
            return int(value)
        else:
            return math.ceil(value)

    df_filtered['Number Pieces'] = df_filtered['Number Pieces'].apply(
        round_up_and_convert)

    additional_header_data["totalPackages_SAD06"] = df_filtered['Number Pieces'].sum(
    )

    # sum of quantity in each line - sum this after the data
    additional_header_data["totalAmountInvoiced_SAD22"] = df_filtered['Customs Value'].sum(
    )

    currency = df_filtered['Currency'].unique().tolist()

    additional_header_data["totalAmountInvoicedCurrency_SAD22"] = currency[0]

    processed_df = process_excel(df_subset)

    print(f"Succesfully processed json file")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("format: python hb_fuller_preprocessor <excel workbook>")
        sys.exit(1)

    main(sys.argv[1])

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
