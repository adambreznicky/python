import arcpy, os
map = arcpy.mapping.MapDocument("current")
dataFrame = arcpy.mapping.ListDataFrames(map)[0]
#--------Enter BELOW either NorthCounties or SouthCounties depending which year it is----

CountyLayer = arcpy.GetParameterAsText(0)
cursor = arcpy.SearchCursor(CountyLayer)

dataYear = arcpy.GetParameterAsText(1)
OutPut = arcpy.GetParameterAsText(2)

for row in cursor:
    for textElement in arcpy.mapping.ListLayoutElements(map, "TEXT_ELEMENT"):
        if textElement.name == "CountyName":
            textElement.text = row.CNTY_NM + " - " + dataYear
        if textElement.name == "Year":
            textElement.text = "Copyright " + dataYear + " TxDOT"

    print row.CNTY_NM
    arcpy.mapping.ExportToPDF(map, OutPut + os.sep + row.CNTY_NM)