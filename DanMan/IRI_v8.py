__file__ = 'IRI_v7'
__date__ = '1/28/2016'
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
# theMXD = "C:\\TxDOT\\Projects\\IRI_dan\\working\\Untitled.mxd"

inputlist = input.split(";")
inputcntr = 1
lengthinput = len(inputlist)
issuesReport = [["DISTRICT_FILE", "ROUTE_ID", "BEGIN_POINT", "END_POINT", "SECTION_LENGTH", "IRI", "RUTTING", "DATE", "ERROR_DESCRIPTION"]]
statsReport = [["DISTRICT_FILE", "LG Record Count", "KG Record Count", "Total Records Count", "Input Record Count", "Lost Records Count", "LG Records Length", "KG Records Length", "Total Routed Length"]]

arcpy.CreateFileGDB_management(output, "RhinoLines.gdb")
rhinospace = output + os.sep + "RhinoLines.gdb"
rhino_lines = rhinospace + os.sep + "rhinolines"
# arcpy.Copy_management(calRhino, rhino_lines)
arcpy.FeatureClassToFeatureClass_conversion(calRhino, rhinospace, "rhinolines")


# arcpy.AddField_management(rhino_lines, "FRM_DFO", "DOUBLE")
# arcpy.AddField_management(rhino_lines, "TO_DFO", "DOUBLE")
cursor = arcpy.da.UpdateCursor(rhino_lines, ["FRM_DFO", "TO_DFO", 'SHAPE@', "OBJECTID"])
for row in cursor:
    # arcpy.AddMessage(row[3])
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
arcpy.AddField_management(rhino_lines, "RTE_ORDER", "SHORT")
arcpy.AddField_management(rhino_lines, "FLAG", "TEXT", "", "", 30)
arcpy.AddMessage("Applying RTE_ORDER.")
cursor = arcpy.da.UpdateCursor(rhino_lines, ["RIA_RTE_ID", "FRM_DFO", "RTE_ORDER", "FLAG"], "", "", "", (None, "ORDER BY RIA_RTE_ID ASC, FRM_DFO ASC"))
# cursor = arcpy.da.UpdateCursor(rhino_lines, ["RTE_ID", "FRM_DFO", "RTE_ORDER", "FLAG", "RU", "F_SYSTEM", "SEC_NHS", "HPMS"], "", "", "", (None, "ORDER BY RTE_ID ASC, FRM_DFO ASC"))
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
    # ru = int(row[4])
    # fs = int(row[5])
    # nhs = int(row[6])
    # row[3] = current + "-" + str(order) + "-" + str(ru) + "-" + str(fs) + "-" + str(nhs) + "-" + str(row[7])
    row[3] = current + "-" + str(order)
    cursor.updateRow(row)
del cursor
arcpy.AddMessage("RTE_ORDER applied.")

dictionary = {}
cursor = arcpy.da.SearchCursor(rhino_lines, ["FLAG", "FRM_DFO", "TO_DFO"])
for row in cursor:
    flag = row[0]
    odr = flag.split("-")[0] + "-" + flag.split("-")[1] + "-" + flag.split("-")[2]
    fDFO = row[1]
    tDFO = row[2]
    dictionary[odr] = [fDFO, tDFO]
del cursor


arcpy.AddMessage("Converting CSVs to DBFs")
dbf_List = []
for excel in inputlist:
    csv_name = excel.split("\\")[-1]
    dist_name = csv_name.split("_")[0].replace(" ", "")
    arcpy.AddMessage(dist_name)
    csv_bundle = []
    f = open(excel, 'rt')
    reader = csv.reader(f)
    header = 0
    for row in reader:
        if header == 0:
            header += 1
        else:
            csv_bundle.append(row)

    arcpy.CreateTable_management(output, "IRI_" + dist_name + ".dbf")
    the_dbf = output + os.sep + "IRI_" + dist_name + ".dbf"
    arcpy.AddField_management(the_dbf, "ROUTE_ID", "TEXT", "", "", 50)
    arcpy.AddField_management(the_dbf, "LANE", "TEXT", "", "", 5)
    arcpy.AddField_management(the_dbf, "BEGIN_POIN", "DOUBLE", 18, 5)
    arcpy.AddField_management(the_dbf, "END_POINT", "DOUBLE", 18, 5)
    arcpy.AddField_management(the_dbf, "SECTION_LE", "DOUBLE", 18, 5)
    arcpy.AddField_management(the_dbf, "LAT", "DOUBLE", 18, 5)
    arcpy.AddField_management(the_dbf, "LONG", "DOUBLE", 18, 5)
    arcpy.AddField_management(the_dbf, "IRI", "DOUBLE", 18, 5)
    arcpy.AddField_management(the_dbf, "RUTTING", "DOUBLE", 18, 5)
    arcpy.AddField_management(the_dbf, "DATE", "TEXT", "", "", 50)
    arcpy.AddField_management(the_dbf, "TIME", "TEXT", "", "", 50)
    arcpy.DeleteField_management(the_dbf, "Field1")

    cursor = arcpy.da.InsertCursor(the_dbf, ["ROUTE_ID", "LANE", "LAT", "LONG", "IRI", "RUTTING", "DATE", "TIME"])
    for line in csv_bundle:
        try:
            rte_id = line[0].strip() + "-" + line[1][0] + "G"
            date = str(line[11])[:8]
            time = str(line[11])[8:]
            insert_line = [rte_id, line[1], line[2], line[3], line[9], line[10], date, time]
            cursor.insertRow(insert_line)
        except:
            arcpy.AddMessage(line)

    del cursor

    dbf_List.append(the_dbf)


arcpy.AddMessage("Processing the DBFs")
for dbf in dbf_List:
    distName = str(dbf).split("\\")[-1]
    if distName[-1] == "$":
        distName = distName[:-1]
    if distName[-4:] == ".dbf":
        distName = distName[:-4]
    arcpy.AddMessage("Beginning " + str(inputcntr) + " of " + str(lengthinput) + ": " + distName)
    arcpy.CreateFileGDB_management(output, "Wrkg" + str(inputcntr) + ".gdb")
    workspace = output + os.sep + "Wrkg" + str(inputcntr) + ".gdb"
    arcpy.AddMessage("Working database created.")

    data = []
    lg = []
    fields = ["ROUTE_ID", "BEGIN_POIN", "END_POINT", "SECTION_LE", "IRI", "RUTTING", "DATE", "TIME", "LANE"]
    # fields = ["ROUTE_ID", "BEGIN_POIN", "END_POINT", "SECTION_LE", "IRI", "RUTTING", "DATE"]
    data.append(fields)
    lg.append(fields)

    # spref = "Coordinate Systems\\Geographic Coordinate Systems\\World\\GCS_WGS_1984.prj"
    spref = "Coordinate Systems\\Geographic Coordinate Systems\\World\\WGS 1984.prj"
    arcpy.MakeXYEventLayer_management(dbf, "Long", "Lat", "pointEvents" + str(inputcntr), spref)
    arcpy.AddMessage("Event Layer created.")

    pntfeature = workspace + os.sep + "allPoints"
    arcpy.CopyFeatures_management("pointEvents" + str(inputcntr), pntfeature)
    arcpy.AddMessage("Point feature class created.")

    initial = 0
    ids = []
    cursor = arcpy.da.SearchCursor(pntfeature, ["ROUTE_ID", "LANE"])
    for row in cursor:
        id = row[0]
        lane = row[1]
        combo = id + "-" + lane
        initial += 1
        if combo not in ids:
            ids.append(combo)
    del cursor
    del row
    arcpy.AddMessage("RTE_IDs compiled.")

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

    counter = 1
    total = len(ids)
    arcpy.AddMessage("Finding measures for: ")
    for combo in ids:
        id = combo.split("-")[0] + "-" + combo.split("-")[1]
        lane = combo.split("-")[2]
        rteName = combo.split("-")[0]
        roadslayer.definitionQuery = " RIA_RTE_ID = '" + rteName + "-KG' "
        pointslayer.definitionQuery = " ROUTE_ID = '" + id + "' AND LANE = '" + lane + "'"
        arcpy.RefreshActiveView()
        arcpy.AddMessage(str(counter) + "/" + str(total) + " " + combo)
        label = combo.replace("-", "")
        arcpy.LocateFeaturesAlongRoutes_lr(pointslayer, roadslayer, "FLAG", "230 Feet", workspace + os.sep + label, "FLAG POINT END_POINT")
        counter += 1
    arcpy.AddMessage("Tables created.")

    # alltables = []
    arcpy.env.workspace = workspace
    tables = arcpy.ListTables()

    for table in tables:
        arcpy.AddMessage(table)
        arcpy.AddField_management(table, "ODR_FLAG", "TEXT", "", "", 20)

        numbDict = {}
        cursor = arcpy.da.UpdateCursor(table, ["FLAG", "ODR_FLAG"])
        for row in cursor:
            flag = row[0]
            odr = flag.split("-")[0] + "-" + flag.split("-")[1] + "-" + flag.split("-")[2]
            if odr not in numbDict.keys():
                numbDict[odr] = 1
            else:
                curNumb = numbDict[odr]
                curNumb += 1
                numbDict[odr] = curNumb
            row[1] = odr
            cursor.updateRow(row)
        del cursor

        counter = 1
        previous = ""
        last = ""
        # cursor = arcpy.da.UpdateCursor(table, ["ODR_FLAG", "BEGIN_POINT", "END_POINT", "SECTION_LENGTH"], None, None, False, (None, "ORDER BY ODR_FLAG ASC, END_POINT ASC"))
        cursor = arcpy.da.UpdateCursor(table, ["ODR_FLAG", "BEGIN_POIN", "END_POINT", "SECTION_LE"], None, None, False, (None, "ORDER BY ODR_FLAG ASC, END_POINT ASC"))
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
                    row[3] = round(row[2] - row[1], 3)
                else:
                    row[1] = beginner
                    row[2] = segEnd
                    row[3] = round(row[2] - row[1], 3)
            elif counter == 1 and counter == total:
                values = dictionary[current]
                row[1] = float(format(float(values[0]), '.3f'))
                row[2] = float(format(float(values[1]), '.3f'))
                row[3] = round(row[2] - row[1], 3)
                counter = 0
            elif previous == current and counter != total:
                row[1] = last
                row[2] = float(format(float(row[2]), '.3f'))
                row[3] = round(row[2] - last, 3)
            elif previous == current and counter == total:
                values = dictionary[current]
                ender = float(format(float(values[1]), '.3f'))
                if abs(ender - last) > 1:
                    row[1] = last
                    row[2] = float(format(float(row[2]), '.3f'))
                    row[3] = round(row[2] - last, 3)
                else:
                    row[1] = last
                    row[2] = float(format(float(values[1]), '.3f'))
                    row[3] = round(row[2] - last, 3)
                counter = 0
            else:
                arcpy.AddMessage("problem with " + current)
            last = row[2]
            if row[3] == 0:
                cursor.deleteRow()
            else:
                cursor.updateRow(row)
            previous = current
            counter += 1
        del cursor
    arcpy.AddMessage("Measure difference fields populated.")

    arcpy.Merge_management(tables, workspace + os.sep + "merged")
    arcpy.AddMessage("All tables merged successfully.")

    # arcpy.AddField_management(workspace + os.sep + "merged", "RU", "TEXT", "", "", 5)
    # arcpy.AddMessage("RU field created.")
    # arcpy.AddField_management(workspace + os.sep + "merged", "F_SYSTEM", "TEXT", "", "", 5)
    # arcpy.AddMessage("Functional System field created.")
    # arcpy.AddField_management(workspace + os.sep + "merged", "SEC_NHS", "TEXT", "", "", 5)
    # arcpy.AddMessage("NHS field created.")
    # arcpy.AddField_management(workspace + os.sep + "merged", "HPMS", "TEXT", "", "", 5)
    # arcpy.AddMessage("HPMS Keeper field created.")
    # arcpy.AddMessage("Fields created.")
    # cursor = arcpy.da.UpdateCursor(workspace + os.sep + "merged", ["FLAG", "RU", "F_SYSTEM", "SEC_NHS"])
    ## cursor = arcpy.da.UpdateCursor(workspace + os.sep + "merged", ["FLAG", "RU", "F_SYSTEM", "SEC_NHS", "HPMS"])
    # for row in cursor:
    #     flag = row[0]
    #     row[1] = flag.split("-")[3]
    #     row[2] = flag.split("-")[4]
    #     row[3] = flag.split("-")[5]
    #     # row[4] = flag.split("-")[6]
    #     cursor.updateRow(row)
    # del cursor

    LGcounter = 0
    KGcounter = 0
    LGlength = 0
    KGlength = 0
    cursor = arcpy.da.SearchCursor(workspace + os.sep + "merged", fields, None, None, False, (None, "ORDER BY ROUTE_ID ASC, LANE ASC, BEGIN_POIN ASC"))
    for row in cursor:
        id = row[0]
        if id[-2:] == "LG":
            lg.append(row)
            LGcounter += 1
            LGlength += float(row[3])
        elif id[-2:] == "RG":
            THEid = id[:-2]
            newid = THEid + "KG"
            fixed = [newid, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]]
            # fixed = [newid, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]]
            data.append(fixed)
            KGcounter += 1
            KGlength += float(row[3])
            if float(row[3]) > 1:
                problem = [distName, newid, row[1], row[2], row[3], row[4], row[5], row[6], "Abnormally large SECTION_LENGTH"]
                issuesReport.append(problem)
            if float(row[3]) == 0:
                problem = [distName, newid, row[1], row[2], row[3], row[4], row[5], row[6], "Zero length SECTION_LENGTH"]
                issuesReport.append(problem)
        else:
            data.append(row)
            KGcounter += 1
            KGlength += float(row[3])
            if float(row[3]) > 1:
                problem = [distName, id, row[1], row[2], row[3], row[4], row[5], row[6], "Abnormally large SECTION_LENGTH"]
                issuesReport.append(problem)
            if float(row[3]) == 0:
                problem = [distName, id, row[1], row[2], row[3], row[4], row[5], row[6], "Zero length SECTION_LENGTH"]
                issuesReport.append(problem)
    del cursor
    arcpy.AddMessage("Data compiled.")

    arcpy.AddMessage("Creating CSV reports.")
    leftover = open(output + os.sep + distName + "_LG.csv", 'wb')
    writer = csv.writer(leftover)
    writer.writerows(lg)
    leftover.close()
    final = open(output + os.sep + distName + "_Plotted.csv", 'wb')
    writer = csv.writer(final)
    writer.writerows(data)
    final.close()
    arcpy.AddMessage("CSV written locally.")
    arcpy.AddMessage("T:\\DATAMGT\\HPMS-DATA\\2015Data\\Pavement\\IRI\\IRIData\\Output_From_Script" + os.sep + distName + "_LG.csv")
    leftover = open("T:\\DATAMGT\\HPMS-DATA\\2015Data\\Pavement\\IRI\\IRIData\\Output_From_Script" + os.sep + distName + "_LG.csv", 'wb')
    writer = csv.writer(leftover)
    writer.writerows(lg)
    leftover.close()
    final = open("T:\\DATAMGT\\HPMS-DATA\\2015Data\\Pavement\\IRI\\IRIData\\Output_From_Script" + os.sep + distName + "_Plotted.csv", 'wb')
    writer = csv.writer(final)
    writer.writerows(data)
    final.close()
    arcpy.AddMessage("CSV written to T drive.")

    pointsName = distName.split("_")[-1]
    arcpy.FeatureClassToFeatureClass_conversion(pntfeature, "T:\\DATAMGT\\HPMS-DATA\\2015Data\\Pavement\\IRI\\IRIData\\Output_From_Script\\All_Points.gdb", pointsName)
    arcpy.AddMessage("allpoints feature class transferred to T drive.")

    TOTALcounter = LGcounter + KGcounter
    TOTALlength = LGlength + KGlength
    DIFFcounter = initial - TOTALcounter
    statsReport.append([distName, LGcounter, KGcounter, TOTALcounter, initial, DIFFcounter, LGlength, KGlength, TOTALlength])

    inputcntr += 1
if len(issuesReport) > 1:
    arcpy.AddMessage("Creating errors report...")
    errors = open(output + os.sep + "00ISSUES_Investigate.csv", 'wb')
    writer = csv.writer(errors)
    writer.writerows(issuesReport)
    errors.close()
arcpy.AddMessage("Creating stats report...")
stats = open(output + os.sep + "00Statistics.csv", 'wb')
writer = csv.writer(stats)
writer.writerows(statsReport)
stats.close()

arcpy.AddMessage("that's all folks!")

arcpy.AddMessage("started: " + str(now))
now2 = datetime.datetime.now()
arcpy.AddMessage("ended: " + str(now2))
print "that's all folks!"