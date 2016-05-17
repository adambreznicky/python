__file__ = 'IRI_v2'
__date__ = '3/29/2014'
__author__ = 'ABREZNIC'
"""
The MIT License (MIT)

Copyright (c) 2016 Texas Department of Transportation
Author: Adam Breznicky

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import arcpy, os, datetime, csv

now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + "_" + curMonth + "_" + curDay

input = arcpy.GetParameterAsText(0)
calRhino = arcpy.GetParameterAsText(1)
output = arcpy.GetParameterAsText(2)


ids = []
cursor = arcpy.da.SearchCursor(input, ["ROUTE_ID"])
for row in cursor:
    if row[0] not in ids:
        ids.append(row[0])
del cursor
del row
arcpy.AddMessage("route ids compiled.")


arcpy.AddMessage("Beginning")
arcpy.CreateFileGDB_management(output, "Wrkg_OffSystem.gdb")
workspace = output + os.sep + "Wrkg_OffSystem.gdb"
arcpy.AddMessage("Working database created.")



pntfeature = workspace + os.sep + "allPoints"
arcpy.CopyFeatures_management(input, pntfeature)
arcpy.AddField_management(pntfeature, "BEGIN_POINT", "DOUBLE")
arcpy.AddField_management(pntfeature, "SECTION_LENGTH", "DOUBLE")
arcpy.AddMessage("Point feature class created.")

initial = 0
# excelID = []
cursor = arcpy.da.UpdateCursor(pntfeature, ["ROUTE_ID", "PMIS_ID"])
for row in cursor:
    # pmis = row[0]
    initial += 1
    # if pmis not in excelID:
    #     excelID.append(pmis)
    # row[1] = row[0]
    # cursor.updateRow(row)
del cursor
del row
arcpy.AddMessage("total # of points compiled.")

rhino_lines = workspace + os.sep + "rhinolines"
arcpy.Copy_management(calRhino, rhino_lines)
# arcpy.AddField_management(rhino_lines, "FRM_DFO", "DOUBLE")
# arcpy.AddField_management(rhino_lines, "TO_DFO", "DOUBLE")
cursor = arcpy.da.UpdateCursor(rhino_lines, ["FRM_DFO", "TO_DFO", 'SHAPE@', 'ROUTE_ID', 'LOC_ERROR'])
for row in cursor:
    try:
        bp = row[2].firstPoint.M
        ep = row[2].lastPoint.M
        bpNew = float(format(float(bp), '.3f'))
        epNew = float(format(float(ep), '.3f'))
        row[0] = bpNew
        row[1] = epNew
        cursor.updateRow(row)
    except:
        arcpy.AddMessage("bad geom: " + row[3] + " " + row[4])
del cursor
del row
arcpy.AddMessage("Calibrated RHINO copied local.")
arcpy.AddField_management(rhino_lines, "RTE_ORDER", "SHORT")
arcpy.AddField_management(rhino_lines, "FLAG", "TEXT", "", "", 20)
arcpy.AddMessage("Applying RTE_ORDER.")
cursor = arcpy.da.UpdateCursor(rhino_lines, ["ROUTE_ID", "FRM_DFO", "RTE_ORDER", "FLAG"], "", "", "", (None, "ORDER BY ROUTE_ID ASC, FRM_DFO ASC"))
counter = 0
order = 1
previous = ""
for row in cursor:
    current = row[0]
    if counter == 0:
        row[2] = order
    elif counter != 0 and previous == current:
        order += 1
        row[2] = order
    else:
        order = 1
        row[2] = order
    previous = current
    counter += 1
    row[3] = current + "-" + str(order)
    cursor.updateRow(row)
del cursor
arcpy.AddMessage("RTE_ORDER applied.")

dictionary = {}
cursor = arcpy.da.SearchCursor(rhino_lines, ["FLAG", "FRM_DFO", "TO_DFO"])
for row in cursor:
    flag = row[0]
    fDFO = row[1]
    tDFO = row[2]
    dictionary[flag] = [fDFO, tDFO]
del cursor

roadslayer = ""
pointslayer = ""
# mxd = arcpy.mapping.MapDocument(theMXD)
mxd = arcpy.mapping.MapDocument("CURRENT")
df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.name == "rhinolines":
        arcpy.mapping.RemoveLayer(df, lyr)
    if lyr.name == "allPoints":
        arcpy.mapping.RemoveLayer(df, lyr)
newlayerpnt = arcpy.mapping.Layer(pntfeature)
arcpy.mapping.AddLayer(df, newlayerpnt)
newlayerline = arcpy.mapping.Layer(rhino_lines)
arcpy.mapping.AddLayer(df, newlayerline)
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.name == "rhinolines":
        roadslayer = lyr
    if lyr.name == "allPoints":
        pointslayer = lyr
arcpy.AddMessage("Layers acquired.")

issues = []
counter = 1
total = len(ids)
arcpy.AddMessage("Finding measures for: ")
for id in ids:
    try:
        pointslayer.definitionQuery = "ROUTE_ID = '" + id + "' "
        roadslayer.definitionQuery = "ROUTE_ID = '" + id + "' "
        arcpy.RefreshActiveView()

        label = id
        if "-" in label:
            label = id.replace("-", "")
        arcpy.LocateFeaturesAlongRoutes_lr(pointslayer, roadslayer, "FLAG", "230 Feet", workspace + os.sep + "R" + label, "FLAG POINT END_POINT")
        arcpy.AddMessage(str(counter) + "/" + str(total) + " " + id)
        counter += 1
    except:
        counter += 1
        arcpy.AddMessage("Bad id: " + id)
        issues.append(id)
arcpy.AddMessage("Tables created.")

arcpy.env.workspace = workspace
tables = arcpy.ListTables()

for table in tables:
    numbDict = {}
    cursor = arcpy.da.SearchCursor(table, ["FLAG"])
    for row in cursor:
        flag = row[0]
        if flag not in numbDict.keys():
            numbDict[flag] = 1
        else:
            curNumb = numbDict[flag]
            curNumb += 1
            numbDict[flag] = curNumb
    del cursor
    arcpy.AddMessage(table)
    counter = 1
    previous = ""
    last = ""
    cursor = arcpy.da.UpdateCursor(table, ["FLAG", "BEGIN_POINT", "END_POINT", "SECTION_LENGTH"], None, None, False, (None, "ORDER BY FLAG ASC, END_POINT ASC"))
    for row in cursor:
        current = row[0]
        total = numbDict[current]
        if counter == 1 and counter != total:
            values = dictionary[current]
            beginner = float(format(float(values[0]), '.3f'))
            segEnd = float(format(float(row[2]), '.3f'))
            if abs(segEnd - beginner) > 1:
                segSrt = segEnd - .1
                row[1] = float(format(float(segSrt), '.3f'))
                row[2] = segEnd
                row[3] = row[2] - row[1]
            else:
                row[1] = beginner
                row[2] = segEnd
                row[3] = row[2] - row[1]
        elif counter == 1 and counter == total:
            values = dictionary[current]
            row[1] = float(format(float(values[0]), '.3f'))
            row[2] = float(format(float(values[1]), '.3f'))
            row[3] = row[2] - row[1]
            counter = 0
        elif previous == current and counter != total:
            row[1] = last
            row[2] = float(format(float(row[2]), '.3f'))
            row[3] = row[2] - last
        elif previous == current and counter == total:
            values = dictionary[current]
            ender = float(format(float(values[1]), '.3f'))
            if abs(ender - last) > 1:
                row[1] = last
                row[2] = float(format(float(row[2]), '.3f'))
                row[3] = row[2] - last
            else:
                row[1] = last
                row[2] = float(format(float(values[1]), '.3f'))
                row[3] = row[2] - last
            counter = 0
        else:
            arcpy.AddMessage("problem with " + current)
        last = row[2]
        cursor.updateRow(row)
        previous = current
        counter += 1
    del cursor
arcpy.AddMessage("Measure difference fields populated.")

arcpy.Merge_management(tables, workspace + os.sep + "merged")
arcpy.AddMessage("All tables merged successfully.")

data = []
fields = ["PMIS_ID", "BEGIN_POINT", "END_POINT", "SECTION_LENGTH", "IRI", "RUTTING", "DATE", "ROUTE_ID"]
data.append(fields)

KGcounter = 0
KGlength = 0
cursor = arcpy.da.SearchCursor(workspace + os.sep + "merged", ["PMIS_ID", "BEGIN_POINT", "END_POINT", "SECTION_LENGTH", "AVEIRI", "AVERUT_IN_", "DATEACQUIR", "FLAG"])
for row in cursor:
    curFlag = row[7]
    curID = curFlag[:-2]
    data.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], curID])
    KGcounter += 1
    KGlength += float(row[4])
    # if float(row[4]) > 1:
    #     problem = [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], "Abnormally large SECTION_LENGTH"]
    #     issuesReport.append(problem)
    # if float(row[4]) == 0:
    #     problem = [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], "Zero length SECTION_LENGTH"]
    #     issuesReport.append(problem)
del cursor
arcpy.AddMessage("Data compiled.")

arcpy.AddMessage("Creating CSV report.")
final = open(output + os.sep + "IRI_Offsystem.csv", 'wb')
writer = csv.writer(final)
writer.writerows(data)
final.close()
arcpy.AddMessage("CSV written.")

TOTALcounter = KGcounter
TOTALlength = KGlength
DIFFcounter = initial - TOTALcounter


arcpy.AddMessage("that's all folks!")

arcpy.AddMessage("started: " + str(now))
now2 = datetime.datetime.now()
arcpy.AddMessage("ended: " + str(now2))

arcpy.AddMessage("ISSUES:")
arcpy.AddMessage(issues)
print "that's all folks!"