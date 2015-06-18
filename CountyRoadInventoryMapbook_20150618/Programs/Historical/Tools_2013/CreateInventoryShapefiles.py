import arcpy, os
# With Toolbox
inventoryShapefile = arcpy.GetParameterAsText(0)
countyShapeFile = arcpy.GetParameterAsText(1)
dataYear = arcpy.GetParameterAsText(2)
outputDir = arcpy.GetParameterAsText(3)

# Without Toolbox
#inventoryShapefile = r'T:\DATAMGT\MAPPING\Mapping Products\County Road Update Mapbooks\2012\Scripts\fileReference\2012_CRI.shp'
#countyShapeFile = r'T:\DATAMGT\MAPPING\Mapping Products\County Road Update Mapbooks\2012\Scripts\fileReference\South_Counties.shp'
#outputDir = r'T:\DATAMGT\MAPPING\Mapping Products\County Road Update Mapbooks\2012\Inventory Shapefiles'

names = []
numbers = []

cursor = arcpy.SearchCursor(countyShapeFile)
for row in cursor:
    names.append(str(row.CNTY_NM).upper())
    numbers.append(str(row.CNTY_NUM).replace('.0',"")) # adjusted to fix float problem

countRange = range(0,len(names))
arcpy.AddMessage("Found %s counties..." % len(names))
arcpy.AddMessage("Now creating %s shapeFiles..." % len(countRange))
for i in countRange:
	COUNTY_NAME = names[i]
	shapeFileName = "%s_INVENTORY_" + dataYear +".shp" % COUNTY_NAME
	shapeFilePath = outputDir + os.sep + shapeFileName
	shapeFileDefQ = "\"CNTY_NBR\" ='"+ str(numbers[i]+"'")
	
	arcpy.AddMessage("%s definition query: %s" % (shapeFileName, shapeFileDefQ))
	arcpy.AddMessage("%s of %s Exporting County %s" % (i+1 , len(countRange),shapeFileName))
	arcpy.Select_analysis(inventoryShapefile, shapeFilePath, shapeFileDefQ)

print "Export Complete"
arcpy.AddMessage("Export Complete")
