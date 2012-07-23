#!/usr/bin/python

from xlrd import open_workbook, xldate_as_tuple, xldate, XL_CELL_BLANK, XL_CELL_EMPTY
import csv
import json

from datetime import datetime


###
###  the CSV Bit
###
def csv_to_json(csv_file, delimiter):
    csvreader = csv.reader(open(csv_file, 'rb'), delimiter=delimiter, quotechar='"')
    data = []
    for row in csvreader:
        r = []
        for field in row:
            if field == '':
                field = None
            else:
                field = unicode(field, 'ISO-8859-1')
            r.append(field)
        data.append(r)
    jsonStruct = {
        'header': data[0],
        'data': data[1:]
    }
    return json.dumps(jsonStruct)


###
###  the Excel Bit
###
def excel_to_dict(excel_file, fields):
    wb = open_workbook(excel_file, 'formatting_info=True')
    rows = []
    for s in wb.sheets():
        rows = rows + process_sheet(s, wb, fields)

    return rows


def excel_to_json(excel_file, fields):
    return json.dumps(excel_to_dict(excel_file, fields))


def parse_value(val, wb, cell_type=1):
    code = 'utf-8'
    if isinstance(val, float):
        if cell_type == 3:
            val = str(parse_date(val, wb))
        else:
            val = str(val)
    if isinstance(val, unicode):
        val = val.encode(code)
    if isinstance(val, str):
        val = unicode(val, errors='replace')
        val = val.replace('\n', '')
        val = val.encode(code)

    val = val.replace('\'', '\\\'')
    return str(val)


def parse_date(val, wb):
    try:
        date_value = xldate_as_tuple(val, wb.datemode)
        t = datetime(* (date_value)).strftime('%d/%m/%Y')
        return t
    except xldate.XLDateAmbiguous:
        return val
    except Exception:
        return val


def get_excel_first_row(sheet, wb):
    fields = []
    for col in range(sheet.ncols):
        val = sheet.cell(0, col).value
        cell_type = sheet.cell_type(0, col)
        fields.append(parse_value(val, wb, cell_type))
    return fields


def process_sheet(sheet, wb, fields):
    rows = []
    dud_types = set([XL_CELL_BLANK, XL_CELL_EMPTY])
    field_names = get_excel_first_row(sheet, wb)
    if field_names:  # ignore empty sheets
        if set(field_names) == set(fields):  # only process sheets with the right columns
            for row in range(sheet.nrows):
                if not all(ty in dud_types for ty in sheet.row_types(row)):  # discard empty/blank rows
                    if row > 0:  # ignore titles
                        elem = dict()
                        for col in range(0, len(field_names)):  # (s.ncols):
                            val = sheet.cell(row, col).value
                            cell_type = sheet.cell_type(row, col)
                            elem[field_names[col]] = parse_value(val, wb, cell_type)

                        rows.append(elem)
        else:
            rows.append({'error': 'Column names are different from Blibb fields in sheet ' + sheet.name})
    return rows



# excel_file = 'test-json.xls'
# fields = ['Name', 'Email', 'Title']
# json_data = excel_to_json(excel_file, fields)
# try:
#   f = open("excel.json", "w")
#   f.writelines(json_data)
# except Exception, e:
#   raise e
# finally:
#   f.close()
