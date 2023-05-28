import math
import sys
from typing import List, Any

from InquirerPy import prompt, inquirer
from InquirerPy.utils import color_print
import pandas as pd


class ExcelProcessor:

    HBF_CUSTOMERS = ['HBF912UK', 'HBF914UK']

    address_data_table = {
        "Blois": ["FRHBFBLO01", "HB FULLER", "ALLEE ROBERT SCHUMAN C.S 1308", "BLOIS", "41013", "FR"],
        "Lueneburg": ["DEHBFLUE01", "H.B. Fuller Deutschland GmbH", "An der Roten Bleiche 2-3", "Lueneburg", "21335", "DE"],
        "Pianezze": ["ITHBFPIA01", "HB Fuller", "VIA DEL INDUSTRIA 8", "PIANEZZE", "36060", "IT"],
        "Nienburg": ["DEHBFNIE01", "HB FULLER DEUTSCHLAND PRODUKTIONS", "HENRIETTENSTRASSE 32", "NIENBURG", "31582", "DE"],
        "Mindelo": ["PTHBFMIN01", "HB FULLER", "Estrada Nacional 13/km16", "Mindelo", "4486-851", "PT"],
    }

    selected_columns = ["Plant Name", "Sales Order Nbr", "Incoterms", "10-Digit UK Import", "Number Pieces",
                        "Qty Shipped Net Weight KG", "Customs Value", "Currency", "Calendar Week", "Country Of Origin",
                        "General description", "Date Creation Record", "EORI Nbr"]

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
        self.input_file = input_file
        self.sheet = None
        self.valid_row_threshold = None
        self.user_input = None
        self.customer = None
        self.df = None
        self.incoterms = None
        self.weeks = None

    def run(self):
        self.sheet_selection()
        self.data_threshold()
        self.user_input_selection()
        self.customer_selection()
        self.process_data()

        # Confirmation and proceeding
        proceed = self.confirm_and_proceed(self.selected_incoterms,
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

    def post_confirmation_procedure(self):
        # continue with the rest of the pipeline after the confirmation step
        print("processing...")
        self.convert_df_to_json(self.df_filtered)
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
            'Select a customer:', choices=self.HBF_CUSTOMERS)

    def convert_df_to_json(self):
        self.df.to_json('output.json', orient='records', lines=True)

    def process_data(self):
        self.df = pd.read_excel(
            self.input_file, sheet_name=self.sheet, engine='openpyxl')

        self.df = self.df.dropna(thresh=int(self.valid_row_threshold))

        self.df = self.df[self.selected_columns].dropna()

        self.additional_header_data['customerReference'] = self.user_input
        self.additional_header_data['customerIdCCT'] = self.customer

        week_list = [str(week) for week in self.df['Calendar Week'].unique(
        ).tolist() if str(week) != 'nan']

        self.week_number = self.get_input('Select a week:', choices=week_list)

        self.df = self.df[self.df['Calendar Week'] == float(self.week_number)]

        incoterms = [str(incoterm) for incoterm in self.df['Incoterms'].unique(
        ).tolist() if str(incoterm) != 'nan']

        self.selected_incoterms = self.incoterm_selection(incoterms)

        self.df_filtered = self.df[self.df['Incoterms'].isin(
            self.selected_incoterms)]

        self.df['Number Pieces'] = self.df['Number Pieces'].apply(
            self.round_up_and_convert)

        self.additional_header_data["totalPackages_SAD06"] = self.df['Number Pieces'].sum(
        )
        self.additional_header_data["totalAmountInvoiced_SAD22"] = self.df['Customs Value'].sum(
        )
        self.additional_header_data["totalAmountInvoicedCurrency_SAD22"] = self.df['Currency'].unique().tolist()[
            0]

        self.df = self.df

    def incoterm_selection(self, incoterms):
        while True:
            selected_incoterms = []
            while True:
                available_incoterms = [
                    incoterm for incoterm in incoterms if incoterm not in selected_incoterms]

                if not available_incoterms:  # All incoterms have been selected
                    break

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

            if done:
                return selected_incoterms
            # No need for else return here. If done == False, loop will continue naturally.

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
        print("Please provide the path to the Excel file as a command line argument.")
        sys.exit(1)

    file_path = sys.argv[1]
    processor = ExcelProcessor(file_path)
    processor.run()

# todo: submit to CCT
# setup SFTP details - I'm almost there.
