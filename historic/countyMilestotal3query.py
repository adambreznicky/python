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
	env.workspace = "C:\\TxDOT\\test"
	now = datetime.datetime.now()
	suffix = now.strftime("%Y%m%d")
	final = "CntyRoadMileage"+suffix+".dbf"
	subfiles = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.MCHAMB1.SUBFILES" 
	where = """ "SUBFILE" = 2 AND "HIGHWAY_STATUS" = 4 AND "ADMIN_SYSTEM" = 3 """
	##Output_Location = arcpy.GetParameterAsText(0)
	arcpy.MakeQueryTable_management(subfiles, "temptable", "ADD_VIRTUAL_KEY_FIELD", "", "", where)
	arcpy.Statistics_analysis("temptable", final, [["LEN_OF_SECTION", "SUM"]], "COUNTY")
	arcpy.JoinField_management(final, "COUNTY", "C:\\TxDOT\\Shapefiles\\Counties.shp", "CNTY_NBR", ["CNTY_NM"])
	arcpy.AddField_management(final, "TotalMiles", "DOUBLE")
	arcpy.CalculateField_management(final, "TotalMiles", "!SUM_LEN_OF!", "PYTHON_9.3")
	arcpy.DeleteField_management(final, ["SUM_LEN_OF"])
	arcpy.AddField_management(final, "CountyNum", "LONG")
	arcpy.CalculateField_management(final, "CountyNum", "!COUNTY!", "PYTHON_9.3")
	arcpy.DeleteField_management(final, ["COUNTY"])
	print "success!"
	raw_input("Press any key to continue")
totalcountymiles()


