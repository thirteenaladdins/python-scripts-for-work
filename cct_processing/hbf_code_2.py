from InquirerPy import prompt, inquirer
import pandas as pd
import sys

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
    plant_names = ["Blois", "Lueneburg", "Pianezze", "Nienburg", "Mindelo"]
    for name in plant_names:
        if name in row['Plant Name']:
            address_data = address_data_table[name]
            row['consignorEORI'] = address_data[0]
            row['consignorName'] = address_data[1]
            row['consignorAddress'] = address_data[2]
            row['consignorTown'] = address_data[3]
            row['consignorPostCode'] = address_data[4]
            row['consignorCountry'] = address_data[5]
    return row


def add_address_to_df(df):
    df = df.apply(add_address_data, axis=1)
    return df


def main():
    input_file = sys.argv[1]  # Get the input file from command line argument
    sheet_names = get_worksheets(input_file)

    for sheet in sheet_names:
        df = read_excel(input_file, sheet)
        df = df[selected_columns]  # Select only the columns that are needed
        df = process_excel(df)  # Rename and add new columns
        df = add_address_to_df(df)  # Add address data to each row

        # TODO: Add additional_header_data to df

        # TODO: Write df to a new excel file


if __name__ == "__main__":
    main()
