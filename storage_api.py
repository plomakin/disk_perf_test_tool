from gspread import WorksheetNotFound, login
import json
import os
from config import ROW_COUNT


def get_work_sheet(sheet, name, column_names):
    try:
        work_sheet = sheet.worksheet(name)
    except WorksheetNotFound:
        work_sheet = sheet.add_worksheet(title=name, rows=ROW_COUNT,
                                         cols=max(40, len(column_names)))

        for i in range(1, len(column_names) + 1):
            work_sheet.update_cell(1, i, column_names[i - 1])

    return work_sheet


def get_row_number(work_sheet):
    num = 2

    while num < work_sheet.row_count and work_sheet.cell(num, 1).value != "":
        num += 1

    if num == work_sheet.row_count:
        work_sheet.append_row(["" for x in range(work_sheet.col_count)])

    return num


def append_row(work_sheet, row):
    row_number = get_row_number(work_sheet)

    i = 1
    for k in row.keys():
        work_sheet.update_cell(row_number, i, row[k])
        i += 1


class Measurement(object):
    def __init__(self):
        self.build = ""
        self.build_type = 0  # GA/Master/Other
        self.md5 = ""
        self.results = {
            "": (float, float)
        }


class Storage(object):
    def store(self, data):
        pass

    def retrieve(self, id):
        pass


class GoogleDocsStorage(Storage):

    def __init__(self, doc_id, work_sheet_name, email=None, password=None):
        self.gc = login(email, password)
        self.sh = self.gc.open_by_key(doc_id)
        self.work_sheet = get_work_sheet(self.sh, work_sheet_name, 40)

    def store(self, data):
        append_row(self.work_sheet, data)

    def retrieve(self, id):
        row_number = self.find_by_id(id)

        if row_number != -1:
            vals = self.work_sheet.row_values(row_number)
            m = Measurement()
            m.build = vals.pop("build_id")
            m.build_type = vals.pop("type")
            m.md5 = vals.pop("iso_md5")
            m.results = {k: vals[k] for k in vals.keys()}
        else:
            return None

    def find_by_id(self, row_id):
        for i in range(1, self.work_sheet):
            if self.work_sheet.cell(i, 1) == row_id:
                return i

        return -1


class DiskStorage(Storage):
    def __init__(self, file_name):
        self.file_name = file_name

        if not os.path.exists(file_name):
            with open(file_name, "w+") as f:
                f.write(json.dumps([]))

    def store(self, data):
        with open(self.file_name, "rt") as f:
            raw_data = f.read()
            document = json.loads(raw_data)
            document.append(data)

        with open(self.file_name, "w+") as f:
            f.write(json.dumps(document))

    def retrieve(self, id):
        with open(self.file_name, "rt") as f:
            raw_data = f.read()
            document = json.loads(raw_data)

            for row in document:
                if row["build_id"] == id:
                    m = Measurement()
                    m.build = row.pop("build_id")
                    m.build_type = row.pop("type")
                    m.md5 = row.pop("iso_md5")
                    m.results = {k: row[k] for k in row.keys()}

                    return m
        return None

