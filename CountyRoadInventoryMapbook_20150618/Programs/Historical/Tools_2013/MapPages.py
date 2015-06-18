import arcpy, os
map = arcpy.mapping.MapDocument("current")
dataFrame = arcpy.mapping.ListDataFrames(map)[0]

GridLayer = arcpy.GetParameterAsText(0)
DataYear = arcpy.GetParameterAsText(1)
outPut = arcpy.GetParameterAsText(2)
cursor = arcpy.SearchCursor(GridLayer)



for textElement in arcpy.mapping.ListLayoutElements(map, "TEXT_ELEMENT"):
	if textElement.name == "Year":
		textElement.text = DataYear

for row in cursor:
    dataFrame.extent = row.shape.extent
    MapID = str(row.Map_ID)
	
    for textElement in arcpy.mapping.ListLayoutElements(map, "TEXT_ELEMENT"):
       if textElement.name == "PageNumber":
           textElement.text = " Page-" + MapID
       if textElement.name == "CountyName":
           textElement.text = row.CNTY_NM + " County"
       if textElement.name == "East":
           textElement.text =  row.East
           if row.East == 0:
               textElement.text = " "
       if textElement.name == "West":
           textElement.text =  row.West
           if row.West == 0:
               textElement.text = " "
       if textElement.name == "North":
           textElement.text =  row.North
           if row.North == 0:
               textElement.text = " "
       if textElement.name == "South":
           textElement.text =  row.South
           if row.South == 0:
               textElement.text = " "
    arcpy.RefreshActiveView()
    arcpy.mapping.ExportToPDF(map, outPut + os.sep + row.CNTY_NM + " " + MapID + ".pdf")
    arcpy.AddMessage(outPut + os.sep + row.CNTY_NM + " " + MapID + ".pdf")
