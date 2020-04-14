import xlrd
from datetime import date, datetime

import xlwt

file = 'data/paipai.xlsx'

sheet1_start_row = 2
sheet1_start_col = 1

sheet2_start_row = 6
sheet2_start_col = 0


def read_excel():
    # 打开文件
    wb = xlrd.open_workbook(filename=file)
    # 通过索引获取表格
    sheet1 = wb.sheet_by_index(0)
    # 通过名字获取表格 wb.sheet_by_name('年级')
    sheet2 = wb.sheet_by_index(1)
    # print(sheet2.name, sheet2.nrows, sheet2.ncols)
    # # 获取行内容
    # rows = sheet1.row_values(2)
    # # 获取列内容
    # cols = sheet1.col_values(3)
    # print(rows)
    # print(cols)
    # print(sheet1.cell_value(1, 0))

    f = xlwt.Workbook()
    target_sheet = f.add_sheet('data', cell_overwrite_ok=True)

    data = [['date', 'time', 'count', 'alert', 'final', 'avg', 'person', 'start', 'data']]
    for row2 in range(sheet2_start_row, sheet2.nrows):
        # print(sheet2.row(row2))
        # for col in range(sheet1_start_col, sheet1.ncols):
        col = row2 - sheet2_start_row + 1
        for row in range(sheet1_start_row, sheet1.nrows):
            item = [sheet2.row(row2)[0].value, sheet1.cell_value(row, 0), sheet2.row(row2)[1].value,
                    sheet2.row(row2)[2].value, sheet2.row(row2)[3].value,
                    sheet2.row(row2)[4].value, sheet2.row(row2)[5].value, sheet1.cell_value(sheet1_start_row, col),
                    sheet1.cell_value(row, col)]
            data.append(item)

    print(len(data))

    for i in range(len(data)):
        for j in range(len(data[i])):
            # print(type(data[i][j]))
            target_sheet.write(i, j, data[i][j])

    f.save('test.xls')


if __name__ == '__main__':
    read_excel()
