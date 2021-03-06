__file__ = 'IRI_v1'
__date__ = '11/25/2014'
__author__ = 'ABREZNIC'
import arcpy, os, datetime, csv

now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + "_" + curMonth + "_" + curDay

input = arcpy.GetParameterAsText(0)
excel = os.path.dirname(input)
output = os.path.dirname(excel)

arcpy.CreateFileGDB_management(output, "Wrkg" + today + ".gdb")
workspace = output + os.sep + "Wrkg" + today + ".gdb"
arcpy.AddMessage("Working database created.")

# spref = "Coordinate Systems\\Geographic Coordinate Systems\\World\\GCS_WGS_1984.prj"
spref = "Coordinate Systems\\Geographic Coordinate Systems\\World\\WGS 1984.prj"
arcpy.MakeXYEventLayer_management(input, "Long", "Lat", "pointEvents", spref)
arcpy.AddMessage("Event Layer created.")

pntfeature = workspace + os.sep + "allPoints"
arcpy.CopyFeatures_management("pointEvents", pntfeature)
arcpy.AddMessage("Point feature class created.")

ids = []
cursor = arcpy.da.SearchCursor(pntfeature, ["ROUTE_ID"])
for row in cursor:
    id = row[0]
    if id not in ids:
        ids.append(id)
del cursor
del row
arcpy.AddMessage("RTE_IDs compiled.")

roadslayer = ""
pointslayer = ""
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
newlayer = arcpy.mapping.Layer(pntfeature)
arcpy.mapping.AddLayer(df, newlayer)
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.name == "TXDOT_Roadways":
        roadslayer = lyr
    if lyr.name == "allPoints":
        pointslayer = lyr
arcpy.AddMessage("Layers acquired.")

counter = 1
total = len(ids)
arcpy.AddMessage("Finding measures for: ")
for id in ids:
    roadslayer.definitionQuery = " RTE_ID = '" + id + "' "
    pointslayer.definitionQuery = " ROUTE_ID = '" + id + "' "
    arcpy.RefreshActiveView()
    arcpy.AddMessage(str(counter) + "/" + str(total) + " " + id)
    arcpy.LocateFeaturesAlongRoutes_lr(pointslayer, roadslayer, "RTE_ID", "230 Feet", workspace + os.sep + "locate" + str(counter), "RID POINT END_POINT")
    counter += 1
arcpy.AddMessage("Tables created.")

# alltables = []
arcpy.env.workspace = workspace
tables = arcpy.ListTables()

for table in tables:
    cursor = arcpy.da.UpdateCursor(table, ["BEGIN_POINT", "END_POINT", "SECTION_LENGTH"], None, None, False, (None, "ORDER BY END_POINT ASC"))
    last = 999999
    for row in cursor:
        end = float(format(float(row[1]), '.3f'))
        if last == 999999:
            begin = end - .1
            if begin < 0:
                begin = 0
            row[0] = str(begin)
        else:
            begin = last
            row[0] = str(begin)
        row[1] = end
        len = end - begin
        if len < .05:
            cursor.deleteRow()
        elif len > .3:
            begin = end - .1
            if begin < 0:
                begin = 0
            row[0] = str(begin)
            len = end - begin
            row[2] = float(format(float(len), '.3f'))
            cursor.updateRow(row)
            last = end
        else:
            row[2] = float(format(float(len), '.3f'))
            cursor.updateRow(row)
            last = end
        arcpy.AddMessage(row)
    del cursor
    del row
arcpy.AddMessage("Measure difference fields populated.")

arcpy.Merge_management(tables, workspace + os.sep + "merged")
arcpy.AddMessage("All tables merged successfully.")

data = []
lg = []
fields = ["ROUTE_ID", "BEGIN_POINT", "END_POINT", "SECTION_LENGTH", "IRI", "RUTTING", "DATE"]
data.append(fields)
lg.append(fields)
cursor = arcpy.da.SearchCursor(workspace + os.sep + "merged", fields)
for row in cursor:
    id = row[0]
    if id[-2:] == "LG":
        lg.append(row)
    elif id[-2:] == "RG":
        THEid = id[:-2]
        newid = THEid + "KG"
        fixed = [newid, row[1], row[2], row[3], row[4], row[5], row[6]]
        data.append(fixed)
    else:
        data.append(row)
del cursor
del row
arcpy.AddMessage("Data compiled.")

leftover = open(output + os.sep + "LG_RECS.csv", 'wb')
writer = csv.writer(leftover)
writer.writerows(lg)
leftover.close()
final = open(output + os.sep + "IRI_Plotted.csv", 'wb')
writer = csv.writer(final)
writer.writerows(data)
final.close()
arcpy.AddMessage("CSV written.")

arcpy.AddMessage("that's all folks!")
print "that's all folks!"