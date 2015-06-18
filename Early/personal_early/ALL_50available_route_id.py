
import arcpy
import datetime, xlwt

dbaseNAME = "Connection to Comanche.sde"

subfiles = "Database Connections\\" + dbaseNAME + "\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
countyref = "Database Connections\\" + dbaseNAME + "\\TPP_GIS.APP_TPP_GIS_ADMIN.County\\TPP_GIS.APP_TPP_GIS_ADMIN.County"
arcpy.AddMessage("Connection Established!")






    # arcpy.CreateTable_management(Output, answer + "_" + cntyQUERY + "_AvailableRouteIDs" + suffix + ".dbf")
    # final = Output + "\\" + answer + "_" + cntyQUERY + "_AvailableRouteIDs" + suffix + ".dbf"
    # arcpy.AddField_management(final, "RTE_NUM", "TEXT", "", "", "5")
    # arcpy.AddField_management(final, "RTE_ID", "TEXT", "", "", "9")
    # arcpy.AddMessage("Final table created!")

    # kursor = arcpy.InsertCursor(final)
    # for k in missing:
    #     row = kursor.newRow()
    #     if len(str(cntyQUERY)) == 2:
    #         countynumber = str("0" + cntyQUERY)
    #     else:
    #         countynumber = str(cntyQUERY)
    #     if len(str(k)) == 4:
    #         RTEpart2 = "AA" + str(k)
    #     elif len(str(k)) == 3:
    #         RTEpart2 = "AA0" + str(k)
    #     elif len(str(k)) == 2:
    #         RTEpart2 = "AA00" + str(k)
    #     elif len(str(k)) == 1:
    #         RTEpart2 = "AA000" + str(k)
    #     else:
    #         RTEpart2 = "A" + str(k)
    #     row.setValue("RTE_NUM", str(k))
    #     row.setValue("RTE_ID", countynumber + RTEpart2)
    #     kursor.insertRow(row)
    # arcpy.AddMessage("Route IDs inserted!")
    # arcpy.DeleteField_management(final, "Field1")
    #
    # try:
    #     arcpy.MakeTableView_management(final, answer + "_" + cntyQUERY + "_AvailableRouteIDs" + suffix)
    #     arcpy.RefreshActiveView()
    # except:
    #     pass
    #
    # arcpy.AddMessage("WooHoo! Go get them route IDs!")


book = xlwt.Workbook()
now = datetime.datetime.now()
suffix = now.strftime("%Y%m%d")
countyRange = range(1,255)
for i in countyRange:

    cntyQUERY = i
    where = """ ("SUBFILE" = 2 OR "SUBFILE" = 5 OR "SUBFILE" = 4)AND "ADMIN_SYSTEM" = 3 AND "COUNTY" = """ + str(cntyQUERY)

    qursor = arcpy.SearchCursor(countyref)
    for row in qursor:
        numb = row.getValue("CNTY_NBR")
        name = row.getValue("CNTY_NM")
        if numb == int(cntyQUERY):
            answer = name
    arcpy.AddMessage("County found:" + answer + "; "+ str(cntyQUERY))

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


    sh = book.add_sheet(str(cntyQUERY)+"_"+answer)
    print "sheet created"
    counter = 0
    for k in missing[-50:]:
        if len(str(cntyQUERY)) == 2:
            countynumber = "0" + str(cntyQUERY)
        elif len(str(cntyQUERY)) == 1:
            countynumber = "00" + str(cntyQUERY)
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
        sh.write(counter, 0, countynumber + RTEpart2)
        counter += 1
    print "Sheet done, next..."


book.save("C:\\TxDOT\\CountyRoadInventory\\2014\\AVAILABLE_RTE_ID_"+suffix+".xls")



print "success!!"