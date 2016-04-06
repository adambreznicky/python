import arcpy

roads_feature_class = ""
route_id_field = ""
rte_order_field = ""
dfo_field = ""

current = ""
previous = ""
counter = 0
NEW_ORDER = 1

cursor = arcpy.da.SearchCursor(roads_feature_class, [route_id_field, rte_order_field, dfo_field], "", "", "", (None, "ORDER BY " + route_id_field + " ASC, " + dfo_field + " ASC"))
for row in cursor:
    current = row[0]
    if counter == 0:
        previous = current
        row[1] = NEW_ORDER
    elif previous == current and counter > 0:
        NEW_ORDER += 1
        row[1] = NEW_ORDER
    else:
        NEW_ORDER = 1
        row[1] = NEW_ORDER
    previous = current
    counter += 1
    print counter
    cursor.updateRow(row)

del cursor
del row

print "that's all folks!!"
