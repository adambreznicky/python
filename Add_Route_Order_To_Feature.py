import arcpy
from arcpy import env
arcpy.env.overwriteOutput = True

env.workspace = r"C:\_GRID\Concurrencies.gdb"

RteTable = r"Route_Concurrent"
rows = arcpy.UpdateCursor(RteTable,"","","","RTE_ID A; LEN_FROM A")
row = rows.next()

current = ""
previous = ""
counter = 0
NEW_ORDER = 1

while row:
    current = row.RTE_ID

    if counter == 0:
        previous = current
        row.RTE_ORDER = NEW_ORDER

    elif previous == current and counter > 0:
        NEW_ORDER += 1
        row.RTE_ORDER = NEW_ORDER
    else:
        NEW_ORDER = 1
        row.RTE_ORDER = NEW_ORDER

    previous = current
    counter += 1
    print counter
    rows.updateRow(row)
    row = rows.next()

del rows
del row
