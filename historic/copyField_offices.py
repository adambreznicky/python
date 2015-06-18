import arcpy
source = "C:\\TxDOT\\Shapefiles\\District_Offices.shp"
outputcopy = "T:\\DATAMGT\\MAPPING\\Personal Folders\\Adam\\District_Offices.shp"
def copyPhone():
	arcpy.JoinField_management(outputcopy, "Address", source, "Address", ["Phone"])
	return "complete"
copyPhone()
