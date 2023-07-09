import gspread
import os
from google.oauth2 import service_account
from config import GOOGLE_JSON_AUTH, GOOGLE_SHEET_URL

EV_G_JSON_AUTH = os.environ.get('GOOGLE_JSON_AUTH')
EV_G_SHEET_URL = os.environ.get('GOOGLE_SHEET_URL')


class GSpreadService:
    def __init__(self):
        self.gc = None
        self.doc = None
        self.worksheet = None

    def ready(self):
        scopes = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
        ]

        # print(EV_G_JSON_AUTH)

        credentials = service_account.Credentials.from_service_account_info(GOOGLE_JSON_AUTH if EV_G_JSON_AUTH is None else EV_G_JSON_AUTH, scopes=scopes)
        self.gc = gspread.authorize(credentials)

        spreadsheet_url = GOOGLE_SHEET_URL if EV_G_SHEET_URL is None else EV_G_SHEET_URL

        self.doc = self.gc.open_by_url(spreadsheet_url)

    def add_worksheet(self, name, columns=None):
        if self.doc is None:
            return

        ws = self.doc.add_worksheet(title=name, rows='100', cols='100')
        if columns is not None:
            ws.append_row(columns)
        self.set_worksheet_by_name(name)

    def set_worksheet_by_name(self, name):
        self.worksheet = self.doc.worksheet(name)

    def add_row(self, data):
        if self.worksheet is None:
            return

        self.worksheet.append_row(data)


# test
if __name__ == '__main__':
    g_test = GSpreadService()
    g_test.ready()
    g_test.set_worksheet_by_name('sessions')
    #### get all values
    # list_of_lists = g_test.worksheet.get_all_values()
    # print(list_of_lists)

    #### get find cell
    cell_list = g_test.worksheet.findall("sudole#0")
    print(cell_list)
    # print(cell, cell.row, cell.col, cell.value)
