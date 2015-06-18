__file__ = 'IRI_v1'
__date__ = '5/20/2014'
__author__ = 'ABREZNIC'
import arcpy, os, datetime, csv, tpp

now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + "_" + curMonth + "_" + curDay

input = arcpy.GetParameterAsText(0)
calRhino = arcpy.GetParameterAsText(1)
output = arcpy.GetParameterAsText(2)
translator = arcpy.GetParameterAsText(3)
# theMXD = "C:\\TxDOT\\Projects\\IRI_dan\\working\\Untitled.mxd"

inputlist = input.split(";")
inputcntr = 1
lengthinput = len(inputlist)
issuesReport = [["DISTRICT_FILE", "PMIS_ID", "BEGIN_POINT", "END_POINT", "SECTION_LENGTH", "IRI", "RUTTING", "DATE", "ROUTE_ID", "ERROR_DESCRIPTION"]]
statsReport = [["DISTRICT_FILE", "KG Record Count", "Total Records Count", "Input Record Count", "Lost Records Count", "KG Records Length", "Total Routed Length"]]
ids = {}
cursor = arcpy.da.SearchCursor(translator, ["PMIS_ID", "RTE_ID"])
for row in cursor:
    pmis = row[0]
    if pmis is not None and pmis != "":
        id = row[1]
        if pmis not in ids.keys():
            ids[pmis] = [id]
        else:
            curList = ids[pmis]
            curList.append(id)
            ids[pmis] = curList
del cursor
del row
arcpy.AddMessage("PMIS_ID and RTE_ID translation compiled.")

for excel in inputlist:
    distName = str(excel).split("\\")[-1]
    if distName[-1] == "$":
        distName = distName[:-1]
    arcpy.AddMessage("Beginning " + str(inputcntr) + " of " + str(lengthinput) + ": " + distName)
    arcpy.CreateFileGDB_management(output, "Wrkg" + str(inputcntr) + ".gdb")
    workspace = output + os.sep + "Wrkg" + str(inputcntr) + ".gdb"
    arcpy.AddMessage("Working database created.")

    data = []
    fields = ["DISTRICT", "PMIS_ID", "BEGIN_POINT", "END_POINT", "SECTION_LENGTH", "IRI", "RUTTING", "DATE", "ROUTE_ID"]
    data.append(fields)

    # spref = "Coordinate Systems\\Geographic Coordinate Systems\\World\\GCS_WGS_1984.prj"
    spref = "Coordinate Systems\\Geographic Coordinate Systems\\World\\WGS 1984.prj"
    arcpy.MakeXYEventLayer_management(excel, "Long", "Lat", "pointEvents" + str(inputcntr), spref)
    arcpy.AddMessage("Event Layer created.")

    pntfeature = workspace + os.sep + "allPoints"
    arcpy.CopyFeatures_management("pointEvents" + str(inputcntr), pntfeature)
    arcpy.AddMessage("Point feature class created.")

    initial = 0
    excelID = []
    cursor = arcpy.da.SearchCursor(pntfeature, ["PMIS_ID"])
    for row in cursor:
        pmis = row[0]
        initial += 1
        if pmis not in excelID:
            excelID.append(pmis)
    del cursor
    del row
    arcpy.AddMessage("PMIS_IDs compiled.")

    rhino_lines = workspace + os.sep + "rhinolines"
    arcpy.Copy_management(calRhino, rhino_lines)
    arcpy.AddField_management(rhino_lines, "FRM_DFO", "DOUBLE")
    arcpy.AddField_management(rhino_lines, "TO_DFO", "DOUBLE")
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
    arcpy.AddField_management(rhino_lines, "RTE_ORDER", "SHORT")
    arcpy.AddField_management(rhino_lines, "FLAG", "TEXT", "", "", 20)
    arcpy.AddMessage("Applying RTE_ORDER.")
    cursor = arcpy.da.UpdateCursor(rhino_lines, ["RTE_ID", "FRM_DFO", "RTE_ORDER", "FLAG"], "", "", "", (None, "ORDER BY RTE_ID ASC, FRM_DFO ASC"))
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

    counter = 1
    total = len(excelID)
    arcpy.AddMessage("Finding measures for: ")
    for pmis in excelID:
        try:
            pmisList = ids[pmis]
            pointslayer.definitionQuery = " PMIS_ID = '" + pmis + "' "
            addition = ""
            for id in pmisList:
                addition += "'" + id + "', "
            addition = addition[:-2]
            rdQuery = "RTE_ID in (" + addition + ")"
            roadslayer.definitionQuery = rdQuery
            arcpy.RefreshActiveView()

            # label = id.replace("-", "")
            arcpy.LocateFeaturesAlongRoutes_lr(pointslayer, roadslayer, "FLAG", "230 Feet", workspace + os.sep + pmis, "FLAG POINT END_POINT")
            arcpy.AddMessage(str(counter) + "/" + str(total) + " " + pmis)
            counter += 1
        except:
            counter += 1
            arcpy.AddMessage("Bad PMIS: " + pmis)
            issuesReport.append(["PMIS_ID: " + pmis, "Found no RTE_ID", "", "", "", "", "", "", "PMIS_ID in excel but not in translator feature class or LocateFeatures tool failed"])
    arcpy.AddMessage("Tables created.")

    # alltables = []
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


    KGcounter = 0
    KGlength = 0
    cursor = arcpy.da.SearchCursor(workspace + os.sep + "merged", ["DISTRICT", "PMIS_ID", "BEGIN_POINT", "END_POINT", "SECTION_LENGTH", "IRI", "RUTTING", "DATE", "FLAG"])
    for row in cursor:
        curFlag = row[8]
        curID = curFlag[:-2]
        data.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], curID])
        KGcounter += 1
        KGlength += float(row[4])
        if float(row[4]) > 1:
            problem = [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], "Abnormally large SECTION_LENGTH"]
            issuesReport.append(problem)
        if float(row[4]) == 0:
            problem = [row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], "Zero length SECTION_LENGTH"]
            issuesReport.append(problem)
    del cursor
    arcpy.AddMessage("Data compiled.")

    arcpy.AddMessage("Creating CSV report.")
    final = open(output + os.sep + distName + "_Plotted_" + str(inputcntr) + ".csv", 'wb')
    writer = csv.writer(final)
    writer.writerows(data)
    final.close()
    arcpy.AddMessage("CSV written.")

    TOTALcounter = KGcounter
    TOTALlength = KGlength
    DIFFcounter = initial - TOTALcounter
    statsReport.append([distName, KGcounter, TOTALcounter, initial, DIFFcounter, KGlength, TOTALlength])

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