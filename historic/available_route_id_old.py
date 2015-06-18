
def availableIDs():
	import arcpy
	from arcpy import env
	import datetime
	now = datetime.datetime.now()
	suffix = now.strftime("%Y%m%d")
	Output = arcpy.GetParameterAsText(0)
	dbaseNAME = arcpy.GetParameterAsText(1)
	cntyQUERY = arcpy.GetParameterAsText(2)
	if int(cntyQUERY) < 1 or int(cntyQUERY) > 254:
		arcpy.AddError("You did not enter a valid county number! Try again.")
		
	subfiles = "Database Connections\\"+dbaseNAME+"\\TPP_GIS.MCHAMB1.SUBFILES"
	countyref = "Database Connections\\"+dbaseNAME+"\\TPP_GIS.MCHAMB1.County\\TPP_GIS.MCHAMB1.County"
	arcpy.AddMessage("Connection Established!")
	
	qursor = arcpy.SearchCursor(countyref)
	for row in qursor:
		numb = row.getValue("CNTY_NBR")
		name = row.getValue("CNTY_NM")
		if numb == int(cntyQUERY):
			answer = name
	arcpy.AddMessage("County found!")
		
	werkin = Output+"\\"+"temptable2.dbf"
	where = """ "SUBFILE" = 2 AND "HIGHWAY_STATUS" = 4 AND "ADMIN_SYSTEM" = 3 AND "COUNTY" = """+cntyQUERY
	arcpy.MakeQueryTable_management(subfiles, "temptable", "ADD_VIRTUAL_KEY_FIELD", "", "", where)
	arcpy.Frequency_analysis("temptable", werkin, "RTE_ID")
	arcpy.AddField_management(werkin, "RTE_NUM", "TEXT", "", "", "5")
	
	cursor = arcpy.UpdateCursor(werkin)
	for row in cursor:
		routeeyedee = row.getValue("RTE_ID")
		routeNumber = routeeyedee[4:]
		row.setValue("RTE_NUM", routeNumber)
		cursor.updateRow(row)
	
	kursor = arcpy.UpdateCursor(werkin)
	for row in kursor:
		rootnum = row.getValue("RTE_NUM")
		rootprefix = rootnum[:1]
		rootsuffix = rootnum[1:]
		if rootprefix == "A":
			row.setValue("RTE_NUM", "0"+rootsuffix)
		else:
			pass
		kursor.updateRow(row)

	kerser = arcpy.UpdateCursor(werkin)
	for row in kerser:
		rootnum = row.getValue("RTE_NUM")
		rootprefix = rootnum[:1]
		rootsuffix = rootnum[4:]
		if rootprefix == "O":
			kerser.deleteRow(row)
		elif rootsuffix == "G":
			kerser.deleteRow(row)
		kerser.updateRow(row)
	arcpy.AddMessage("Okay, we've cleaned out the trash...")

	werkin2 = Output+"\\"+"temptable3.dbf"
	arcpy.Statistics_analysis(werkin, werkin2, [["RTE_NUM", "MIN"],["RTE_NUM", "MAX"]])
	rainge = arcpy.SearchCursor(werkin2)
	for row in rainge:
		minNum = row.getValue("MIN_RTE_NU")
		maxNum = row.getValue("MAX_RTE_NU")
		rangelist = [int(minNum)-int(maxNum)]
	arcpy.AddMessage("Range is established.")
	
	arcpy.CreateTable_management(Output, answer+"_"+cntyQUERY+"_AvailableRouteIDs"+suffix+".dbf", werkin)
	final = Output+"\\"+answer+"_"+cntyQUERY+"_AvailableRouteIDs"+suffix+".dbf"
	
	cerser = arcpy.UpdateCursor(werkin)
	for row in cerser:
		thenumber = row.getValue("RTE_NUM")
		global rangelist
		if int(thenumber) not in rangelist:
			arcpy.Append_management("RTE_NUM", final, "NO_TEST")
		else:
			pass
		cerser.updateRow(row)
		
	arcpy.AddMessage("WooHoo! Go get them route IDs!")

availableIDs()
print "success!!"