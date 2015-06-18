# Python 2.6.5 (r265:79096, Mar 19 2010, 21:48:26) [MSC v.1500 32 bit (Intel)] on win32
## Type "copyright", "credits" or "license()" for more information.

#  ****************************************************************
#  Personal firewall software may warn about the connection IDLE
# makes to its subprocess using this computer's internal loopback
#  interface.  This connection is not visible on any external
#  interface and no data is sent to or received from the Internet.
# ****************************************************************
#import sys, os

#sys.path[0]
#print sys.path
#raw_input("Press any key to continue")


# IDLE 2.6.5   

def totalcountymiles():
    import arcpy
    from arcpy import env
    import datetime
    import os

    now = datetime.datetime.now()
    suffix = now.strftime("%Y%m%d")
    year = now.strftime("%Y")

    dbaseNAME = arcpy.GetParameterAsText(0)
    prelimMILES = arcpy.GetParameterAsText(1)
    directory = os.path.dirname(prelimMILES)
    filename = os.path.basename(prelimMILES)
    filenamePARTS = filename.split("_")
    for item in filenamePARTS:
        name = str(filenamePARTS[0])
        THEcnty = str(filenamePARTS[1])

    subfiles = "Database Connections\\" + dbaseNAME + "\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
    arcpy.AddMessage("Connection Established!")

    where = """ "SUBFILE" = 2 AND "HIGHWAY_STATUS" = 4 AND "ADMIN_SYSTEM" = 3 AND "COUNTY" = """ + THEcnty
    final = directory + "\\" + name + "_" + THEcnty + "_DiffMileage" + suffix + ".dbf"

    arcpy.MakeQueryTable_management(subfiles, "temptable", "ADD_VIRTUAL_KEY_FIELD", "", "", where)
    arcpy.Statistics_analysis("temptable", final, [["LEN_OF_SECTION", "SUM"]], "RTE_ID")
    arcpy.AddMessage("Adding fields...")
    # arcpy.JoinField_management(final, "RTE_ID", prelimMILES, "RTE_ID", "RTE_Miles")
    arcpy.AddField_management(final, "RTE_Miles", "DOUBLE")
    arcpy.AddField_management(final, "Updated_Mi", "DOUBLE")
    arcpy.AddField_management(final, "Mi_Diff", "DOUBLE")
    arcpy.AddField_management(final, "Status", "TEXT", "", "", "15")
    dict = {}
    arcpy.AddMessage("Getting old mileages...")
    ker = arcpy.SearchCursor(prelimMILES)
    for row in ker:
        rteID = row.getValue("RTE_ID")
        mi = row.getValue("RTE_Miles")
        if rteID not in dict.keys():
            dict[rteID] = mi
    del ker
    arcpy.AddMessage("Calculating differences...")
    cursor = arcpy.UpdateCursor(final)
    delRD = []
    editNum = 0
    addNum = 0
    removeNum = 0
    totalSum = 0
    for row in cursor:
        route = row.getValue("RTE_ID")
        newMILES = row.getValue("SUM_LEN_OF")
        row.setValue("Updated_Mi", newMILES)
        if route in dict.keys():
            row.setValue("RTE_Miles", dict[route])
            cursor.updateRow(row)
        if route not in delRD:
            delRD.append(route)
        oldMILES = row.getValue("RTE_MILES")
        difference = newMILES - oldMILES
        row.setValue("Mi_Diff", difference)
        totalSum += difference
        if difference > 0 and oldMILES != 0:
            row.setValue("Status", "extended")
            editNum += 1
        elif difference < 0:
            row.setValue("Status", "shortened")
            editNum += 1
        elif difference > 0 and oldMILES == 0:
            row.setValue("Status", "new road")
            addNum += 1
        elif difference == 0:
            row.setValue("Status", "no change")
        cursor.updateRow(row)
    del cursor
    arcpy.AddMessage("Getting deleted roads...")

    insrt = arcpy.InsertCursor(final)
    newr = insrt.newRow()
    for item in dict.keys():
        if item not in delRD:
            newr.setValue("RTE_ID", item)
            newr.setValue("RTE_Miles", dict[item])
            newr.setValue("Updated_Mi", 0)
            miLoss = dict[item] * -1
            newr.setValue("Mi_Diff", miLoss)
            totalSum += miLoss
            newr.setValue("Status", "deleted")
            removeNum += 1
            insrt.insertRow(newr)
    del insrt

    arcpy.DeleteField_management(final, ["SUM_LEN_OF"])



    arcpy.AddMessage("Success. Use these statistics for the Mileage Tracking Table:")
    if len(str(THEcnty)) == 3:
        arcpy.AddMessage(str(THEcnty) + "AAXXXX")
    elif len(str(THEcnty)) == 2:
        ini = "0" + str(THEcnty)
        arcpy.AddMessage(ini + "AAXXXX")
    else:
        ini = "00" + str(THEcnty)
        arcpy.AddMessage(ini + "AAXXXX")

    if totalSum < 0:
        arcpy.AddMessage("Mileage Removed: " + str(abs(totalSum)))
    elif totalSum > 0:
        arcpy.AddMessage("Mileage Added: " + str(abs(totalSum)))
    else:
        arcpy.AddMessage("No mileage difference")

    arcpy.AddMessage(
        "CRI " + year + ". " + str(addNum) + "  new. " + str(removeNum) + " removed. " + str(editNum) + " edited. ")


totalcountymiles()
#print "success!"



