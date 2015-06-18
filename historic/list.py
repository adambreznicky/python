import arcpy
subfiles = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.MCHAMB1.SUBFILES"
cursor = arcpy.SearchCursor(subfiles)
for row in cursor:
	type = row.getValue("SUBFILE")
	print type


