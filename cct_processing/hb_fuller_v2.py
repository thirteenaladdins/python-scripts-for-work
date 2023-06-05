import math
import sys
from typing import List, Any
import json
from InquirerPy import prompt, inquirer
from InquirerPy.utils import color_print
import pandas as pd
import numpy as np
import pdb

# come back to this, refactor

HBF_CUSTOMERS = ['HBF912UK', 'HBF914UK']

ADDRESS_DATA_TABLE = {
    "Blois": ["FRHBFBLO01", "HB FULLER", "ALLEE ROBERT SCHUMAN C.S 1308", "BLOIS", "41013", "FR"],
    "Lueneburg": ["DEHBFLUE01", "H.B. Fuller Deutschland GmbH", "An der Roten Bleiche 2-3", "Lueneburg", "21335", "DE"],
    "Pianezze": ["ITHBFPIA01", "HB Fuller", "VIA DEL INDUSTRIA 8", "PIANEZZE", "36060", "IT"],
    "Nienburg": ["DEHBFNIE01", "HB FULLER DEUTSCHLAND PRODUKTIONS", "HENRIETTENSTRASSE 32", "NIENBURG", "31582", "DE"],
    "Mindelo": ["PTHBFMIN01", "HB FULLER", "Estrada Nacional 13/km16", "Mindelo", "4486-851", "PT"],
}

SELECTED_COLUMNS = ["Plant Name", "Sales Order Nbr", "Incoterms", "10-Digit UK Import", "Number Pieces",
                    "Qty Shipped Net Weight KG", "Customs Value", "Currency", "Calendar Week", "Country Of Origin",
                    "General description", "Date Creation Record", "EORI Nbr"]


class InputHandler:
    @staticmethod
    def get_input(self, message: str, choices: List[Any] = None, validate=None) -> Any:
        try:
            if choices:
                return inquirer.select(message, choices).execute()
            elif validate:
                return inquirer.text(message, validate=validate).execute()
            else:
                return inquirer.text(message).execute()
        except Exception as e:
            print(f"An error occurred while processing user input: {e}")
            sys.exit(1)

    @staticmethod
    def get_worksheets(self, file_path) -> List[str]:
        try:
            return pd.read_excel(file_path, None, engine='openpyxl').keys()
        except Exception as e:
            print(f"An error occurred while reading the Excel file: {e}")
            sys.exit(1)

    @staticmethod
    def sheet_selection(self, input_file):
        return self.get_input('Select a sheet:', self.get_worksheets(input_file))

    @staticmethod
    def data_threshold(self):
        return self.get_input("What's the minimum number of data-filled columns needed for a row to be valid?",
                              validate=lambda x: int(x) > 0)

    @staticmethod
    def user_input_selection(self):
        return self.get_input('Please enter Reference [box 7]:')

    @staticmethod
    def customer_selection(self):
        return self.get_input('Select a customer:', choices=HBF_CUSTOMERS)

    @staticmethod
    def week_selection(self, df):
        week_list = [str(week) for week in df['Calendar Week'].unique(
        ).tolist() if str(week) != 'nan']
        return self.get_input('Select a week:', choices=week_list)

    @staticmethod
    def select_incoterms(self, incoterms):
        while True:
            selected_incoterms = set()
            available_incoterms = list(set(incoterms) - selected_incoterms)

            while available_incoterms:
                selected_message = ' (selected incoterms: {})'.format(
                    selected_incoterms) if selected_incoterms else ''
                message = "Select incoterms (use Space to select, Enter to confirm) " + \
                    selected_message
                choices = [{'name': incoterm, 'value': incoterm}
                           for incoterm in available_incoterms]
                newly_selected = set(inquirer.checkbox(
                    message=message, choices=choices).execute())

                if not newly_selected:
                    color_print(formatted_text=[
                                ("class:red", "Please select a term ")], style={"red": "red", })
                else:
                    selected_incoterms.update(newly_selected)
                    break

            done = inquirer.confirm(
                f"You've selected these incoterms: {list(selected_incoterms)}. Do you want to proceed?").execute()
            if done:
                return list(selected_incoterms)

    @staticmethod
    def confirm_and_proceed(self, selected_incoterms, sheet, customer, valid_row_threshold, user_input, week_number, df_filtered):
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
            return True
        else:
            return False


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        else:
            return super(NpEncoder, self).default(obj)


class ExcelProcessor:

    additional_header_data = {
        "interfaceVersion": "4.2",  # no additions needed # mandatory
        "customerIdCCT": "",
        "customerEmail": "mamer@als-cs.com",  # no additions needed # mandatory
        "customerReference": "",  # get this from the CLI
        "deliveryTerm_SAD20": "",  # PICK FIRST
        "deliveryTermPlace_SAD20": "Dunkinfield",
        "countryOfExport_SAD15": "DE",  # fill with generic data - DE
        "countryOfDestination_SAD17": "GB",  # fill with generic data- GB
        "totalPackages_SAD06": "",  # sum of quantity in each line - sum this after the data
        "purchaseCountry_SAD11": "GB",  # pick first? Mandatory field
        "totalAmountInvoiced_SAD22": "",
        "totalAmountInvoicedCurrency_SAD22": ""
        # "totalGrossMass": 2914.0,  # sum of weight column - optional
    }

    def __init__(self, input_file):
        # create function that generates the different address roles
        roles = ['CN', 'CZ', 'RE', 'RI', 'RT']

        header_address_data = []

        for role in roles:
            address_data = {
                "role": role,
                "eoriNo": "GB570487130006",
                "name1": "ALS Customs Services Dover Limited",
                "street": "Lord Warden House, Lord Warden Square",
                "zipcode": "CT17 9EQ",
                "city": "Dover",
                "country": "GB",
                "province": "Kent"
            }
            header_address_data.append(address_data)

        self.input_file = input_file
        self.input_handler = InputHandler()
        self.sheet = None
        self.valid_row_threshold = None
        self.user_input = None
        self.customer = None
        self.df = None
        self.df_filtered = None
        self.incoterms = None
        self.weeks = None
        self.addresses = header_address_data

    def run(self):
        self.sheet = self.input_handler.sheet_selection(self.input_file)
        self.valid_row_threshold = self.input_handler.data_threshold()
        self.user_input = self.input_handler.user_input_selection()
        self.customer = self.input_handler.customer_selection()
        # self.incoterms = self.input_handler.select_incoterms()

        self.process_data()

        self.rename_df = self.prepare_df_for_json(self.df_filtered)

        # print(rename_df)
        # Confirmation and proceeding
        proceed = self.input_handler.confirm_and_proceed(self.selected_incoterms,
                                                         self.sheet,
                                                         self.customer,
                                                         self.valid_row_threshold,
                                                         self.user_input,
                                                         self.week_number,
                                                         self.df_filtered)
        if not proceed:
            # If user doesn't want to proceed, return or handle this situation accordingly
            # TODO:
            return
        else:
            # If user wants to proceed, you can continue the pipeline
            self.post_confirmation_procedure()

    def drop_columns(self, df, drop_columns):
        if isinstance(df, pd.DataFrame):
            for col in drop_columns:
                try:
                    df.drop([col], inplace=True, axis=1)
                except KeyError:
                    print(f"Unable to drop column: {col}")
        else:
            print("Error: Expected a DataFrame but got a {}".format(type(df)))

    def post_confirmation_procedure(self):
        # continue with the rest of the pipeline after the confirmation step
        # print("processing...")
        df_invoices = self.df_filtered.copy()

        columns_to_drop = ['customerHSCode_SAD33im', 'noOfPackages_SAD31', 'netMass_SAD38', 'countryOfOrigin_SAD34',
                           'goodsDescription_SAD31', 'grossMass_SAD35', 'sequentialNo_SAD32']

        # print(df_invoices.columns)

        self.drop_columns(df_invoices, columns_to_drop)

        df_invoices.rename(columns={
            "Sales Order Nbr": "invoiceNo",
            "Date Creation Record": "invoiceDate",
            "itemPrice_SAD42": "invoiceAmount",
            "goodsValueCurrency": "invoiceCurrency"
        }, inplace=True)

        self.invoices = df_invoices.to_dict('records')
        # pdb.set_trace()
        self.convert_df_to_json()
        print("Successfully processed json file")

    def sheet_selection(self):
        self.sheet = self.get_input(
            'Select a sheet:', self.get_worksheets(self.input_file))

    def data_threshold(self):
        self.valid_row_threshold = self.get_input(
            "What's the minimum number of data-filled columns needed for a row to be valid?",
            validate=lambda x: int(x) > 0
        )

    def user_input_selection(self):
        self.user_input = self.get_input('Please enter Reference [box 7]:')

    def customer_selection(self):
        self.customer = self.get_input(
            'Select a customer:', choices=HBF_CUSTOMERS)

    def create_customs_order_dict(self):
        # print(self.df_filtered)
        positions = self.df_filtered.astype('object').where(
            pd.notnull(self.df_filtered), None)
        return {
            "CustomsOrder": {
                **self.additional_header_data,
                "addresses": self.addresses,
                "positions": positions.to_dict(orient='records'),
                "invoice": self.invoices
            }
        }

    def prepare_df_for_json(self, df):
        self.df_filtered.insert(0, 'sequentialNo_SAD32',
                                range(1, len(self.df_filtered) + 1))
        self.df_filtered.rename(columns={
            "Currency": "goodsValueCurrency",
            "General description": "goodsDescription_SAD31",
            "Qty Shipped Net Weight KG": "netMass_SAD38",
            "Number Pieces": "noOfPackages_SAD31",
            "10-Digit UK Import": "customerHSCode_SAD33im",
            "Customs Value": "itemPrice_SAD42",
            "Country Of Origin": "countryOfOrigin_SAD34",
            "Sales Order Nbr": "invoiceNo"}, inplace=True)

        self.df_filtered['grossMass_SAD35'] = self.df_filtered['netMass_SAD38']

        # change types of columns
        self.df_filtered['invoiceNo'] = df['invoiceNo'].astype(
            'int').astype('str')
        self.df_filtered['customerHSCode_SAD33im'] = df['customerHSCode_SAD33im'].astype(
            'int').astype('str')

        self.df_filtered['Date Creation Record'] = pd.to_datetime(
            df['Date Creation Record']).dt.strftime('%Y-%m-%d')

        columns_to_drop = ["Plant Name", "Incoterms",
                           "Calendar Week", "EORI Nbr"]

        self.drop_columns(self.df_filtered, columns_to_drop)

        self.df_filtered = self.df_filtered

    def convert_df_to_json(self):
        customs_order_dict = self.create_customs_order_dict()
        with open('output.json', 'w') as f:
            json.dump(customs_order_dict, f, cls=NpEncoder)

    def process_data(self):
        self.df = pd.read_excel(
            self.input_file, sheet_name=self.sheet, engine='openpyxl')

        self.df = self.df.dropna(thresh=int(self.valid_row_threshold))

        self.df = self.df[SELECTED_COLUMNS].dropna()

        self.additional_header_data['customerReference'] = self.user_input
        self.additional_header_data['customerIdCCT'] = self.customer

        week_list = [str(week) for week in self.df['Calendar Week'].unique(
        ).tolist() if str(week) != 'nan']

        self.week_number = self.get_input('Select a week:', choices=week_list)

        self.df = self.df[self.df['Calendar Week'] == float(self.week_number)]

        incoterms = [str(incoterm) for incoterm in self.df['Incoterms'].unique(
        ).tolist() if str(incoterm) != 'nan']

        self.selected_incoterms = self.incoterms = self.input_handler.select_incoterms(
            incoterms)

        self.additional_header_data['deliveryTerm_SAD20'] = self.selected_incoterms[0]

        self.df_filtered = self.df[self.df['Incoterms'].isin(
            self.selected_incoterms)]

        self.df_filtered['Number Pieces'] = self.df_filtered['Number Pieces'].apply(
            self.round_up_and_convert)

        self.additional_header_data["totalPackages_SAD06"] = self.df_filtered['Number Pieces'].sum(
        )
        self.additional_header_data["totalAmountInvoiced_SAD22"] = self.df_filtered['Customs Value'].sum(
        )
        self.additional_header_data["totalAmountInvoicedCurrency_SAD22"] = self.df_filtered['Currency'].unique().tolist()[
            0]

        self.df_filtered = self.df_filtered

    @staticmethod
    def get_worksheets(file_path) -> List[str]:
        try:
            return pd.read_excel(file_path, None, engine='openpyxl').keys()
        except Exception as e:
            print(f"An error occurred while reading the Excel file: {e}")
            sys.exit(1)

    @staticmethod
    def get_input(message: str, choices: List[Any] = None, validate=None) -> Any:
        try:
            if choices:
                return inquirer.select(message, choices).execute()
            elif validate:
                return inquirer.text(message, validate=validate).execute()
            else:
                return inquirer.text(message).execute()
        except Exception as e:
            print(f"An error occurred while processing user input: {e}")
            sys.exit(1)

    @staticmethod
    def round_up_and_convert(value):
        if value == 0:
            return 1
        elif math.isclose(value, int(value)):
            return int(value)
        else:
            return math.ceil(value)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("format: python hb_fuller_preprocessor <excel workbook>")
        sys.exit(1)

    file_path = sys.argv[1]
    processor = ExcelProcessor(file_path)
    processor.run()
