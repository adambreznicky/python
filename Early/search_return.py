import arcpy
countyref = "Database Connections\\"+dbaseNAME+"\\TPP_GIS.MCHAMB1.County\\TPP_GIS.MCHAMB1.County"
cntyQUERY = raw.input("county number?")
cntyQUERY	
qursor = arcpy.SearchCursor(countyref)

for row in qursor:
	numb = row.getValue("CNTY_NBR")
	name = row.getValue("CNTY_NM")
	if numb  cntyQUERY
		return name
		else row.next()
	