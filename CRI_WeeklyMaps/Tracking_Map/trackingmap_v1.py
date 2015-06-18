import arcpy, os, shutil
import datetime
now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
#curYear = str("2012")
curDate = curMonth + "_" + curDay + "_" + curYear

home = "C:\\TxDOT\\CountyRoadInventory\\TRACKING\\"

arcpy.AddMessage("Generating Tracking Map...")


#
#Make Directories
#
if os.path.exists(home + os.sep + curYear):
	os.makedirs(home + os.sep + curYear + os.sep + curDate)
else:
	os.makedirs(home + os.sep + curYear)
	os.makedirs(home + os.sep + curYear + os.sep + curDate)
house = home + os.sep + curYear + os.sep + curDate
#
#north county:
if int(curYear)%2==0:
	statusMap = arcpy.mapping.MapDocument("C:\\TxDOT\\CountyRoadInventory\\TRACKING\\CRI_TRACKING.mxd")
	dataFrame = arcpy.mapping.ListDataFrames(statusMap)[0]
	newextent = dataFrame.extent
	newextent.XMin, newextent.YMin = 582786.47000423, 826927.373313854
	newextent.XMax, newextent.YMax = 1687689.94133357, 1600359.80324447
	dataFrame.extent = newextent

	# Local variables:
	owssvr_ = "C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\owssvr$"

	# Process: Table to Table
	arcpy.TableToTable_conversion(owssvr_, house, "queriedtable.dbf", "", "ID \"ID\" true true false 8 Double 6 15 ,First,#;Update_Yea \"Update_Yea\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\owssvr$,Update Year,-1,-1;District \"District\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\owssvr$,District,-1,-1;County \"County\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\owssvr$,County,-1,-1;Status \"Status\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\owssvr$,Status,-1,-1", "")
	queriedtable = house + os.sep + "queriedtable.dbf"
	
	dict = {}
	counter = 0
	comper = 0
	
	kursor = arcpy.SearchCursor(queriedtable, """"Update_Yea" = '""" + curYear + """'""")
	for row in kursor:
		county = row.getValue("County")
		stat = row.getValue("Status")
		counter += 1
		if stat == "Electronic Update (GIS)" or stat == "Electronic Update (Road Logs)":
			dict[county] = "Electronic Update"
			comper += 1
		elif stat == "Paper Update":
			dict[county] = stat
			comper += 1
		else:
			dict[county] = stat
	del kursor
	
	cursor = arcpy.UpdateCursor("C:\\TxDOT\\CountyRoadInventory\\TRACKING\\Shapefiles\\NorthCounties.shp")
	for row in cursor:
		row.setValue("status", "No Response")
		cursor.updateRow(row)
		cnty = row.getValue("CNTY_NM")
		if cnty in dict.keys():
			row.setValue("status", dict[cnty])
		cursor.updateRow(row)
	del cursor
	
	differguy = float(comper) / float(counter) * 100
	integ = str(differguy).split(".")[0]
	deci = str(differguy).split(".")[1][:2]
	numsz = integ + "." + deci
	
	differguy2 = float(counter) / float(115) * 100
	integ2 = str(differguy2).split(".")[0]
	deci2 = str(differguy2).split(".")[1][:2]
	numsz2 = integ2 + "." + deci2
	
	
	for lyr in arcpy.mapping.ListLayers(statusMap):
		if lyr.name == "NorthCounties":
			lyr.visible = True
		if lyr.name == "SouthCounties":
			lyr.visible = False
		arcpy.AddMessage("Layers visualized.")
	for textElement in arcpy.mapping.ListLayoutElements(statusMap, "TEXT_ELEMENT"):
		if textElement.name == "topYEAR":
			textElement.text = curYear
		if textElement.name == "bottomDate":
			textElement.text = now.strftime("%B") + " " + curDay + ", " + curYear
		if textElement.name == "copyright":
			textElement.text = "Copyright " + curYear
		if textElement.name == "finalDate":
			lastYears = int(curYear) - 1
			textElement.text = str(lastYears) + "."
		if textElement.name == "responder":
			textElement.text = numsz2 + "% Have Responded"
			textElement.elementPositionX = 7.2
			textElement.elementPositionY = 5.8
		if textElement.name == "updater":
			textElement.text = numsz + "% of Responses Require Update"
			textElement.elementPositionX = 6.6
			textElement.elementPositionY = 5.5
		arcpy.AddMessage("Text elements updated.")
	legend = arcpy.mapping.ListLayoutElements(statusMap, "LEGEND_ELEMENT")[0]
	legend.elementPositionX = 7
	legend.elementPositionY = 6.2
	arcpy.AddMessage("Legend moved.")

	arcpy.RefreshActiveView()
	arcpy.mapping.ExportToPDF(statusMap, house + os.sep + "TrackingMap" + curDate + ".pdf")
	
#
# south county	
elif int(curYear)%2!=0:
	statusMap = arcpy.mapping.MapDocument("C:\\TxDOT\\CountyRoadInventory\\TRACKING\\CRI_TRACKING.mxd")
	dataFrame = arcpy.mapping.ListDataFrames(statusMap)[0]
	newextent = dataFrame.extent
	newextent.XMin, newextent.YMin = 364911.216382526, 350798.309516114
	newextent.XMax, newextent.YMax = 1628319.75219708, 1235184.28458639
	dataFrame.extent = newextent

	# Local variables:
	owssvr_ = "C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\owssvr$"

	# Process: Table to Table
	arcpy.TableToTable_conversion(owssvr_, house, "queriedtable.dbf", "", "ID \"ID\" true true false 8 Double 6 15 ,First,#;Update_Yea \"Update_Yea\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\owssvr$,Update Year,-1,-1;District \"District\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\owssvr$,District,-1,-1;County \"County\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\owssvr$,County,-1,-1;Status \"Status\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\owssvr$,Status,-1,-1", "")
	queriedtable = house + os.sep + "queriedtable.dbf"
	
	dict = {}
	counter = 0
	comper = 0
	
	kursor = arcpy.SearchCursor(queriedtable, """"Update_Yea" = '""" + curYear + """'""")
	for row in kursor:
		county = row.getValue("County")
		stat = row.getValue("Status")
		counter += 1
		if stat == "Electronic Update (GIS)" or stat == "Electronic Update (Road Logs)":
			dict[county] = "Electronic Update"
			comper += 1
		elif stat == "Paper Update":
			dict[county] = stat
			comper += 1
		else:
			dict[county] = stat
	del kursor
	
	cursor = arcpy.UpdateCursor("C:\\TxDOT\\CountyRoadInventory\\TRACKING\\Shapefiles\\SouthCounties.shp")
	for row in cursor:
		row.setValue("status", "No Response")
		cursor.updateRow(row)
		cnty = row.getValue("CNTY_NM")
		if cnty in dict.keys():
			row.setValue("status", dict[cnty])
		cursor.updateRow(row)
	del cursor
	
	differguy = float(comper) / float(counter) * 100
	integ = str(differguy).split(".")[0]
	deci = str(differguy).split(".")[1][:2]
	numsz = integ + "." + deci
	
	differguy2 = float(counter) / float(115) * 100
	integ2 = str(differguy2).split(".")[0]
	deci2 = str(differguy2).split(".")[1][:2]
	numsz2 = integ2 + "." + deci2
	
	
	for lyr in arcpy.mapping.ListLayers(statusMap):
		if lyr.name == "NorthCounties":
			lyr.visible = False
		if lyr.name == "SouthCounties":
			lyr.visible = True
		arcpy.AddMessage("Layers visualized.")
	for textElement in arcpy.mapping.ListLayoutElements(statusMap, "TEXT_ELEMENT"):
		if textElement.name == "topYEAR":
			textElement.text = curYear
		if textElement.name == "bottomDate":
			textElement.text = now.strftime("%B") + " " + curDay + ", " + curYear
		if textElement.name == "copyright":
			textElement.text = "Copyright " + curYear
		if textElement.name == "finalDate":
			lastYears = int(curYear) - 1
			textElement.text = str(lastYears) + "."
		if textElement.name == "responder":
			textElement.text = numsz2 + "% Have Responded"
			textElement.elementPositionX = 1.04
			textElement.elementPositionY = 1.46
		if textElement.name == "updater":
			textElement.text = numsz + "% of Responses Require Update"
			textElement.elementPositionX = 1.04
			textElement.elementPositionY = 1.14
		arcpy.AddMessage("Text elements updated.")
	legend = arcpy.mapping.ListLayoutElements(statusMap, "LEGEND_ELEMENT")[0]
	legend.elementPositionX = 1.04
	legend.elementPositionY = 1.88
	arcpy.AddMessage("Legend moved.")

	arcpy.RefreshActiveView()
	arcpy.mapping.ExportToPDF(statusMap, house + os.sep + "TrackingMap" + curDate + ".pdf")

try:
	shutil.copyfile(house + os.sep + "TrackingMap" + curDate + ".pdf", "T:\\DATAMGT\\MAPPING\\Data Collection\\Core Projects\\CountyRoad\\" + curYear + os.sep + "_Progress Maps" + os.sep + "TrackingMap" + curDate + ".pdf")
except:
	arcpy.AddMessage("Map created locally but could not copy to the T drive. Please do this manually.")
arcpy.AddMessage("Tracking Map Complete.")
