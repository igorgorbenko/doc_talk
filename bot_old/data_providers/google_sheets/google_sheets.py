import gspread
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetsClient:
    def __init__(self, credentials_path, spreadsheet_url):
        self.credentials_path = credentials_path
        self.spreadsheet_url = spreadsheet_url
        self.client = None
        self.spreadsheet = None
        self.worksheet = None
        self.authenticate()
        self.open_spreadsheet()

    def authenticate(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_path, scope)
        self.client = gspread.authorize(credentials)

    def open_spreadsheet(self):
        self.spreadsheet = self.client.open_by_url(self.spreadsheet_url)
        self.worksheet = self.spreadsheet.sheet1

    def append_row(self, row_data):
        self.worksheet.append_row(row_data)


if __name__ == "__main__":
    credentials_path = './sa-secret.json'
    spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1TyDfC_pECHpxktPvXwx1dwBpIgmW5tHOYaS58P7tRr8/edit#gid=0'
    google_sheets_client = GoogleSheetsClient(credentials_path, spreadsheet_url)
    new_row = ["Value 1", "Value 2", "Value 3"]
    google_sheets_client.append_row(new_row)
