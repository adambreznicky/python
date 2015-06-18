import re
import xlsxwriter

workbook_path = "C:\\Users\\DHICKMA\\Documents\\BitBucket\ScriptTools\\read_dml\\DomainSummary.xlsx"
workbook = xlsxwriter.Workbook(workbook_path)

header_format = workbook.add_format()
header_format.set_bold()
header_format.set_bg_color('#D3D3D3')
header_format.set_border(2)

data_format = workbook.add_format()
data_format.set_bg_color('#D3D3D3')
data_format.set_border()

last_data_row_format = workbook.add_format()
last_data_row_format.set_bottom(2)
last_data_row_format.set_top(1)
last_data_row_format.set_right(1)
last_data_row_format.set_left(1)
last_data_row_format.set_bottom_color('black')
last_data_row_format.set_bg_color('#D3D3D3')

left_data_row_format = workbook.add_format()
left_data_row_format.set_left(2)
left_data_row_format.set_right(1)
left_data_row_format.set_top(1)
left_data_row_format.set_bottom(1)
left_data_row_format.set_left_color('black')
left_data_row_format.set_bg_color('#D3D3D3')

right_data_row_format = workbook.add_format()
right_data_row_format.set_right(2)
right_data_row_format.set_top(1)
right_data_row_format.set_left(1)
right_data_row_format.set_bottom(1)
right_data_row_format.set_right_color('black')
right_data_row_format.set_bg_color('#D3D3D3')


def get_fields(row):
    fields = [f.strip() for f in row.split(",")]
    return fields

def get_row_values(row):
    vals = [v.strip() for v in row.split(",")]
    return vals

def create_new_tab(domain_name, fields, row_dictionary):
    worksheet = workbook.add_worksheet(domain_name)
    for f in fields:
        worksheet.set_column(fields.index(f), fields.index(f), len(f) + 4)
        worksheet.write(0, fields.index(f), f, header_format)

    for k, v in row_dictionary.iteritems():
        for val in v:
            if val is None:
                val = 'NULL'

            if k == len(row_dictionary):
                worksheet.write(k, v.index(val), val.strip("'"), last_data_row_format)
            elif v.index(val) == 0:
                worksheet.write(k, v.index(val), val.strip("'"), left_data_row_format)
            elif v.index(val) == len(v) - 1:
                worksheet.write(k, v.index(val), val.strip("'"), right_data_row_format)
            else:
                worksheet.write(k, v.index(val), val.strip("'"), data_format)

def read_lines(dml_file):
    prev_domain_name = None
    prev_fields = None
    domain_dictionary = {}
    with open(dml_file) as DML:
        for row in DML:
            if row.startswith('INSERT INTO'):
                domain_name = row.split()[2]
                groups = re.findall('\(([^\)]+)\)', row)
                fields = get_fields(groups[0])
                values = get_row_values(groups[1])

                if domain_name != prev_domain_name and prev_domain_name is not None:
                    create_new_tab(prev_domain_name, prev_fields, domain_dictionary)
                    domain_dictionary = {}

                domain_dictionary[len(domain_dictionary) + 1] = values
                prev_domain_name = domain_name
                prev_fields = fields

if __name__ == '__main__':
    workbook_path = "C:\\Users\\DHICKMA\\Documents\\BitBucket\ScriptTools\\read_dml\workbooks.xlsx"
    read_lines("C:\\_GRID\\TC_Scripts\\GRID DDL+DML+Scripts 20140119\\GRID_Domain_Insert_DML.sql")
    workbook.close()
