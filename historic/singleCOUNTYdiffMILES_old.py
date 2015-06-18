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
	prelimMILES = arcpy.GetParameterAsText(2)
	subfiles = "Database Connections\\"+dbaseNAME+"\\TPP_GIS.MCHAMB1.SUBFILES"
	countyref = "Database Connections\\"+dbaseNAME+"\\TPP_GIS.MCHAMB1.County\\TPP_GIS.MCHAMB1.County"
	
	kursor = arcpy.SearchCursor(prelimMILES)
	for row in kursor:
		whichcounty = row.getValue("RTE_ID")
		THEcnty = whichcounty[:3]
		
	where = """ "SUBFILE" = 2 AND "HIGHWAY_STATUS" = 4 AND "ADMIN_SYSTEM" = 3 AND "COUNTY" = """+THEcnty
	final = Output+"\\Cnty"+THEcnty+"DiffMileage"+suffix+".dbf"
	
	arcpy.MakeQueryTable_management(subfiles, "temptable", "ADD_VIRTUAL_KEY_FIELD", "", "", where)
	arcpy.Statistics_analysis("temptable", final, [["LEN_OF_SECTION", "SUM"]], "RTE_ID")
	arcpy.JoinField_management(final, "RTE_ID", prelimMILES, "RTE_ID", "RTE_Miles")
	arcpy.AddField_management(final, "Updated_Mi", "DOUBLE")
	arcpy.AddField_management(final, "Mi_Diff", "DOUBLE")
	
	cursor = arcpy.UpdateCursor(final)
	for row in cursor:
		newMILES = row.getValue("SUM_LEN_OF")
		oldMILES = row.getValue("RTE_Miles")
		difference = newMILES - oldMILES
		row.setValue("Updated_Mi", newMILES)
		row.setValue("Mi_Diff", difference)
		cursor.updateRow(row)
			
	arcpy.DeleteField_management(final, ["SUM_LEN_OF"])
	
totalcountymiles()	
print "success!"



