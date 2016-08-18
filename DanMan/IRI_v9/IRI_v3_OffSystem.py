__file__ = 'IRI_v3_OffSystem'
__date__ = '8/18/2016'
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

# retrieve and format the date
now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + "_" + curMonth + "_" + curDay
# assign variables to the parameters input when running the tool
input = arcpy.GetParameterAsText(0)
calRhino = arcpy.GetParameterAsText(1)
output = arcpy.GetParameterAsText(2)
translator = calRhino

# and away we go... first, we create an empty file geodatabase (fgdb) to store all the data
arcpy.AddMessage("Beginning")
arcpy.CreateFileGDB_management(output, "Wrkg_OffSystem.gdb")
workspace = output + os.sep + "Wrkg_OffSystem.gdb"
arcpy.AddMessage("Working database created.")
# set up a list which will ultimately be the location we dump all the data. lists are basically CSVs, and since we
# are dumping the output as a CSV, we will compile the data there
data = []
fields = ["PMIS_ID", "BEGIN_POINT", "END_POINT", "SECTION_LENGTH", "IRI", "RUTTING", "DATE", "ROUTE_ID"]
data.append(fields)

# make a temporary point layer of the input CSV from pavement using the Lat/Long fields
spref = "Coordinate Systems\\Geographic Coordinate Systems\\World\\WGS 1984.prj"
arcpy.MakeXYEventLayer_management(input, "Long", "Lat", "pointEvents", spref)
arcpy.AddMessage("Event Layer created.")
# save the temporary layer as a point feature class in our fgdb and add the necessary fields
pntfeature = workspace + os.sep + "allPoints"
arcpy.CopyFeatures_management("pointEvents", pntfeature)
arcpy.AddField_management(pntfeature, "BEGIN_POINT", "DOUBLE")
arcpy.AddField_management(pntfeature, "SECTION_LENGTH", "DOUBLE")
arcpy.AddField_management(pntfeature, "PMIS_ID", "TEXT", "", "", 20)
arcpy.AddMessage("Point feature class created.")
# loop through the point feature class to make a list of all the unqiue pmis_id's we're working with
initial = 0
excelID = []
cursor = arcpy.da.UpdateCursor(pntfeature, ["ROUTE_ID", "PMIS_ID"])
for row in cursor:
    pmis = row[0]
    initial += 1
    if pmis not in excelID:
        excelID.append(pmis)
    row[1] = row[0]
    cursor.updateRow(row)
del cursor
del row
arcpy.AddMessage("PMIS_IDs compiled.")
# create a copy of the linework and put it into our fgdb. add the necessary fields
rhino_lines = workspace + os.sep + "rhinolines"
arcpy.FeatureClassToFeatureClass_conversion(calRhino, workspace, "rhinolines")
arcpy.AddField_management(rhino_lines, "FRM_DFO", "DOUBLE")
arcpy.AddField_management(rhino_lines, "TO_DFO", "DOUBLE")
# overwrite the from and to DFO fields with the measures of the geometry so we arn't fooling ourselves
cursor = arcpy.da.UpdateCursor(rhino_lines, ["FRM_DFO", "TO_DFO", 'SHAPE@'])
for row in cursor:
    bp = row[2].firstPoint.M
    ep = row[2].lastPoint.M
    bpNew = float(format(float(bp), '.3f'))
    epNew = float(format(float(ep), '.3f'))
    row[0] = bpNew
    row[1] = epNew
    cursor.updateRow(row)
del cursor
del row
arcpy.AddMessage("Calibrated RHINO copied local.")
# add more fields to the fgdb linework so can establish a sequential order of records based on the
# route id and from measures
arcpy.AddField_management(rhino_lines, "RTE_ORDER", "SHORT")
arcpy.AddField_management(rhino_lines, "FLAG", "TEXT", "", "", 20)
# advanced sort the lines based on route id first, then from DFO. then we loop through the records and popualte
# a flag field so we can re-sort in this exact same order later in the process
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
# compile a reference dictionary store of all the from and to DFOs for the 'cascade' zipper process later
# where we tie all the records together
dictionary = {}
cursor = arcpy.da.SearchCursor(rhino_lines, ["FLAG", "FRM_DFO", "TO_DFO"])
for row in cursor:
    flag = row[0]
    fDFO = row[1]
    tDFO = row[2]
    dictionary[flag] = [fDFO, tDFO]
del cursor
# let's add the points and road lines feature classes from our fgdb to the mxd
roadslayer = ""
pointslayer = ""
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
# this is magic time. we'll use our PMIS_ID list and iterate through each one of the IDs using it to
# apply a query on each the points and the lines so only matching data is shown. then we run the
# locate tool to grab the measures. and then loop onto the next id. each iteration creates a new table
# in our fgdb. one table per pmis_id.
counter = 1
total = len(excelID)
arcpy.AddMessage("Finding measures for: ")
for pmis in excelID:
    try:
        pointslayer.definitionQuery = " PMIS_ID = '" + pmis + "' "
        rdQuery = " PMIS_ID = '" + pmis + "' "
        roadslayer.definitionQuery = rdQuery
        arcpy.RefreshActiveView()

        arcpy.LocateFeaturesAlongRoutes_lr(pointslayer, roadslayer, "FLAG", "230 Feet", workspace + os.sep + pmis, "FLAG POINT END_POINT")
        arcpy.AddMessage(str(counter) + "/" + str(total) + " " + pmis)
        counter += 1
    except:
        counter += 1
        arcpy.AddMessage("Bad PMIS: " + pmis)
arcpy.AddMessage("Tables created.")
# lets iterate through each of the output tables in the fgdb
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
    # now lets loop through all the records in the current table doing the zipper action and creating sequential events
    # out of the measures and using that dictionary from earlier
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
# merge together all the individual pmis id tables in the fgdb
arcpy.Merge_management(tables, workspace + os.sep + "merged")
arcpy.AddMessage("All tables merged successfully.")
# now we will loop through the all inclusive merged table and collect up all the data in a clean CSV format with
# only the fields we care about. we will pass the clean data into the CSV list we created at the beginning of this script
KGcounter = 0
KGlength = 0
cursor = arcpy.da.SearchCursor(workspace + os.sep + "merged", ["PMIS_ID", "BEGIN_POINT", "END_POINT", "SECTION_LENGTH", "AveIRI", "AveRUT_in____no_negative_rutting_allowed", "DateAcquired", "FLAG"])
for row in cursor:
    curFlag = row[7]
    curID = curFlag[:-2]
    data.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], curID])
    KGcounter += 1
    KGlength += float(row[4])
del cursor
arcpy.AddMessage("Data compiled.")
# save a CSV of the data
arcpy.AddMessage("Creating CSV report.")
final = open(output + os.sep + "IRI_Offsystem.csv", 'wb')
writer = csv.writer(final)
writer.writerows(data)
final.close()
arcpy.AddMessage("CSV written.")

# well that's it
arcpy.AddMessage("that's all folks!")
# we'll show the start and end time so the user knows how long it took for the whole script/tool to run
arcpy.AddMessage("started: " + str(now))
now2 = datetime.datetime.now()
arcpy.AddMessage("ended: " + str(now2))

print "that's all folks!"