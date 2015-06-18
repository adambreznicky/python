# Python 2.6.5 (r265:79096, Mar 19 2010, 21:48:26) [MSC v.1500 32 bit (Intel)] on win32
## Type "copyright", "credits" or "license()" for more information.

  #  ****************************************************************
  #  Personal firewall software may warn about the connection IDLE
   # makes to its subprocess using this computer's internal loopback
  #  interface.  This connection is not visible on any external
  #  interface and no data is sent to or received from the Internet.
   # ****************************************************************
    
# IDLE 2.6.5      
def totalcountymiles():
	import arcpy
	import datetime
	now = datetime.datetime.now()
	suffix = now.strftime("%Y%m%d")
	final = "CntyRoadMileage"+suffix+".dbf"
	inLayer = "C:\TxDOT\Scratch\TxDOT_Roadways_Events.shp"
	where = """ "SUBFILE" = 2 AND "HIGHWAY_ST" = 4 AND "ADMIN_SYST" = 3 """
	##Output_Location = arcpy.GetParameterAsText(0)
	arcpy.Select_analysis(inLayer, "C:\TxDOT\cntymilesTEMP1.shp", where)
	arcpy.Dissolve_management("C:\TxDOT\cntymilesTEMP1.shp", "C:\TxDOT\cntymilesTEMP2.shp", "COUNTY", [["LEN_OF_SEC", "SUM"]])
	arcpy.Delete_management("C:\TxDOT\cntymilesTEMP1.shp")
	arcpy.TableToTable_conversion("C:\TxDOT\cntymilesTEMP2.shp", "C:\TxDOT\Scratch", final)
	arcpy.Delete_management("C:\TxDOT\cntymilesTEMP2.shp")
	arcpy.JoinField_management(final, "COUNTY", "C:\TxDOT\Shapefiles\Counties.shp", "CNTY_NBR", ["CNTY_NM"])
	arcpy.AddField_management(final, "TotalMiles", "DOUBLE")
	arcpy.CalculateField_management(final, "TotalMiles", "!SUM_LEN_OF!", "PYTHON_9.3")
	arcpy.DeleteField_management(final, ["SUM_LEN_OF"])
	arcpy.AddField_management(final, "CountyNum", "LONG")
	arcpy.CalculateField_management(final, "CountyNum", "!COUNTY!", "PYTHON_9.3")
	arcpy.DeleteField_management(final, ["COUNTY"])
	print "success!"
totalcountymiles()


