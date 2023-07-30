import json
import gspread
import os
from google.oauth2 import service_account
from config import GOOGLE_JSON_AUTH, GOOGLE_SHEET_URL
from datetime import datetime, timedelta, timezone

EV_G_JSON_AUTH = os.environ.get('GOOGLE_JSON_AUTH')
EV_G_SHEET_URL = os.environ.get('GOOGLE_SHEET_URL')


class GSpreadService:
    def __init__(self):
        self.gc = None
        self.doc = None
        self.worksheet = None

    def ready(self):
        debug_now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")
        scopes = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
        ]

        # print(EV_G_JSON_AUTH)
        g_auth = GOOGLE_JSON_AUTH if EV_G_JSON_AUTH is None else EV_G_JSON_AUTH
        
        if EV_G_JSON_AUTH is not None:
            print(f'{debug_now} [DEBUG] Use G-Auth environ')
        else:
            print(f'{debug_now} [DEBUG] Use G-Auth config')
        
        if type(g_auth) == str:
            print(f'{debug_now} [DEBUG] G-Auth type : String')
            g_auth = json.loads(g_auth)
        elif type(g_auth) == dict:
            print(f'{debug_now} [DEBUG] G-Auth type : Dict')
            if 'auth' in g_auth:
                g_auth = json.loads(g_auth.auth)
            elif len(g_auth.keys()) == 1:
                g_auth = g_auth[g_auth.keys()[0]]
            else:
                print(f'{debug_now} [DEBUG] Unknown G-Auth Key')

        # print(type(g_auth), g_auth)
        credentials = service_account.Credentials.from_service_account_info(g_auth, scopes=scopes)
        self.gc = gspread.authorize(credentials)

        spreadsheet_url = GOOGLE_SHEET_URL if EV_G_SHEET_URL is None else EV_G_SHEET_URL
        print(f'{debug_now} [DEBUG] Use G-Spreadsheet url : {spreadsheet_url}')

        self.doc = self.gc.open_by_url(spreadsheet_url)

    def add_worksheet(self, name, columns=None):
        debug_now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")
        if self.doc is None:
            print(f'{debug_now} [DEBUG] Not set doc')
            return

        ws = self.doc.add_worksheet(title=name, rows='100', cols='100')
        if columns is not None:
            ws.append_row(columns)
        self.set_worksheet_by_name(name, columns)

    def set_worksheet_by_name(self, name, columns):
        debug_now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")
        if self.doc is None:
            print(f'{debug_now} [DEBUG] Not set doc')
            return
        try:
            self.worksheet = self.doc.worksheet(name)
        except gspread.exceptions.APIError:
            print(f'{debug_now} [DEBUG] APIError.. API re-request ')
            # APIError Exception 발생 시 재시도
            self.worksheet = self.doc.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            self.add_worksheet(name, columns=columns)

    def add_row(self, data):
        debug_now = datetime.now(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")
        if self.worksheet is None:
            print(f'{debug_now} [DEBUG] Not set worksheet')
            return

        self.worksheet.append_row(data)


# test
if __name__ == '__main__':
    g_test = GSpreadService()
    g_test.ready()
    g_test.set_worksheet_by_name('sessions', ['entry', 'leave', 'person', 'duration', 'goal'])
    # get all values
    # list_of_lists = g_test.worksheet.get_all_values()
    # print(list_of_lists)

    # get find cell
    cell_list = g_test.worksheet.findall("sudole#0")
    print(cell_list)
    # print(cell, cell.row, cell.col, cell.value)
