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

    now = datetime.datetime.now()
    suffix = now.strftime("%Y%m%d")
    Output = arcpy.GetParameterAsText(0)
    dbaseNAME = arcpy.GetParameterAsText(1)
    cntyQUERY = arcpy.GetParameterAsText(2)
    if int(cntyQUERY) < 1 or int(cntyQUERY) > 254:
        arcpy.AddError("You did not enter a valid county number! Try again.")

    subfiles = "Database Connections\\" + dbaseNAME + "\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
    countyref = "Database Connections\\" + dbaseNAME + "\\TPP_GIS.APP_TPP_GIS_ADMIN.County\\TPP_GIS.APP_TPP_GIS_ADMIN.County"
    arcpy.AddMessage("Connection Established!")

    qursor = arcpy.SearchCursor(countyref)
    for row in qursor:
        numb = row.getValue("CNTY_NBR")
        name = row.getValue("CNTY_NM")
        if numb == int(cntyQUERY):
            answer = name
    arcpy.AddMessage("County found!")

    final = Output + "\\" + answer + "_" + cntyQUERY + "_RoadMileage" + suffix + ".dbf"
    where = """ "SUBFILE" = 2 AND "HIGHWAY_STATUS" = 4 AND "ADMIN_SYSTEM" = 3 AND "COUNTY" = """ + cntyQUERY
    arcpy.MakeQueryTable_management(subfiles, "temptable", "ADD_VIRTUAL_KEY_FIELD", "", "", where)
    arcpy.Statistics_analysis("temptable", final, [["LEN_OF_SECTION", "SUM"]], "RTE_ID")
    arcpy.AddField_management(final, "RTE_Miles", "DOUBLE")

    cursor = arcpy.UpdateCursor(final)
    for row in cursor:
        routeMILES = row.getValue("SUM_LEN_OF")
        row.setValue("RTE_Miles", routeMILES)
        cursor.updateRow(row)

    arcpy.DeleteField_management(final, ["SUM_LEN_OF"])
    arcpy.AddMessage("WooHoo! Go get them mileages!")


totalcountymiles()	





