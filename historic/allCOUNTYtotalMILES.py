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
import os
import shutil
working = "C:\\TxDOT\\processing_DONOTTOUCH"
os.mkdir(working)
   
def totalcountymiles():
	import arcpy
	from arcpy import env
	import datetime
	env.workspace = working
	now = datetime.datetime.now()
	suffix = now.strftime("%Y%m%d")
	Output = arcpy.GetParameterAsText(0)
	dbaseNAME = arcpy.GetParameterAsText(1)
	final = Output+"\\CntyRoadMileage"+suffix+".dbf"
	subfiles = "Database Connections\\"+dbaseNAME+"\\TPP_GIS.MCHAMB1.SUBFILES"
	countyref = "Database Connections\\"+dbaseNAME+"\\TPP_GIS.MCHAMB1.County\\TPP_GIS.MCHAMB1.County"
	where = """ "SUBFILE" = 2 AND "HIGHWAY_STATUS" = 4 AND "ADMIN_SYSTEM" = 3 """
	arcpy.MakeQueryTable_management(subfiles, "temptable", "ADD_VIRTUAL_KEY_FIELD", "", "", where)
	arcpy.Statistics_analysis("temptable", final, [["LEN_OF_SECTION", "SUM"]], "COUNTY")
	arcpy.JoinField_management(final, "COUNTY", countyref, "CNTY_NBR", ["CNTY_NM"])
	arcpy.AddField_management(final, "TotalMiles", "DOUBLE")
	arcpy.AddField_management(final, "Number", "LONG")

	cursor = arcpy.UpdateCursor(final)
	for row in cursor:
		cntyNUM = row.getValue("COUNTY")
		cntyMILES = row.getValue("SUM_LEN_OF")
		row.setValue("Number", cntyNUM)
		row.setValue("TotalMiles", cntyMILES)
		cursor.updateRow(row)
			
	arcpy.DeleteField_management(final, ["SUM_LEN_OF"])
	arcpy.DeleteField_management(final, ["COUNTY"])
	
totalcountymiles()
shutil.rmtree(working)	
print "success!"



