def availableIDs():
    import arcpy
    from arcpy import env
    import datetime

    now = datetime.datetime.now()
    suffix = now.strftime("%Y%m%d")
    Output = arcpy.GetParameterAsText(0)
    dbaseNAME = "Connection to Comanche.sde"
    cntyQUERY = arcpy.GetParameterAsText(1)
    if int(cntyQUERY) < 1 or int(cntyQUERY) > 254:
        arcpy.AddError("You did not enter a valid county number! Try again.")

    subfiles = "Database Connections\\" + dbaseNAME + "\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
    countyref = "Database Connections\\" + dbaseNAME + "\\TPP_GIS.APP_TPP_GIS_ADMIN.County\\TPP_GIS.APP_TPP_GIS_ADMIN.County"
    arcpy.AddMessage("Connection Established!")
    where = """ "SUBFILE" = 2 AND "COUNTY" = """ + cntyQUERY

    qursor = arcpy.SearchCursor(countyref)
    for row in qursor:
        numb = row.getValue("CNTY_NBR")
        name = row.getValue("CNTY_NM")
        if numb == int(cntyQUERY):
            answer = name
    arcpy.AddMessage("County found!")

    NumList = sorted([])

    cursor = arcpy.SearchCursor(subfiles, where)
    for row in cursor:
        RteID = row.RTE_ID
        try:
            IDNum = int(RteID.split("A")[-1])
        except:
            pass
        NumList.append(IDNum)
    arcpy.AddMessage("Route ID numbers identified!")

    NoDupe = []
    for i in NumList:
        if i not in NoDupe:
            NoDupe.append(i)
    arcpy.AddMessage("Duplicates removed!")

    mini = min(NoDupe)
    maxi = max(NoDupe)
    rainge = range(mini, maxi + 1)
    missing = []

    for n in rainge:
        if n not in NoDupe:
            missing.append(n)
    arcpy.AddMessage("Missing Route ID numbers identified!")

    arcpy.CreateTable_management(Output, answer + "_" + cntyQUERY + "_AvailableRouteIDs" + suffix + ".dbf")
    final = Output + "\\" + answer + "_" + cntyQUERY + "_AvailableRouteIDs" + suffix + ".dbf"
    arcpy.AddField_management(final, "RTE_NUM", "TEXT", "", "", "5")
    arcpy.AddField_management(final, "RTE_ID", "TEXT", "", "", "9")
    arcpy.AddMessage("Final table created!")

    kursor = arcpy.InsertCursor(final)
    for k in missing:
        row = kursor.newRow()
        if len(str(cntyQUERY)) == 2:
            countynumber = str("0" + cntyQUERY)
        else:
            countynumber = str(cntyQUERY)
        if len(str(k)) == 4:
            RTEpart2 = "AA" + str(k)
        elif len(str(k)) == 3:
            RTEpart2 = "AA0" + str(k)
        elif len(str(k)) == 2:
            RTEpart2 = "AA00" + str(k)
        elif len(str(k)) == 1:
            RTEpart2 = "AA000" + str(k)
        else:
            RTEpart2 = "A" + str(k)
        row.setValue("RTE_NUM", str(k))
        row.setValue("RTE_ID", countynumber + RTEpart2)
        kursor.insertRow(row)
    arcpy.AddMessage("Route IDs inserted!")
    arcpy.DeleteField_management(final, "Field1")

    try:
        arcpy.MakeTableView_management(final, answer + "_" + cntyQUERY + "_AvailableRouteIDs" + suffix)
        arcpy.RefreshActiveView()
    except:
        pass

    arcpy.AddMessage("WooHoo! Go get them route IDs!")




availableIDs()
print "success!!"