import arcpy
from arcpy import env
import os
import glob
import shutil


inputfolder = arcpy.GetParameterAsText(0)+"\\"
inputfiles = glob.glob(inputfolder+"\\*.txt")
WGScoord = "Coordinate Systems\\Geographic Coordinate Systems\\World\\WGS 1984.prj"
TXcoord = "Coordinate Systems\\Projected Coordinate Systems\\State Systems\\NAD 1983 Texas Statewide Mapping System (Meters).prj"
for file in inputfiles:
	setup = file.split("\\")[-1]
	filename = str(setup.split(".")[0])
	arcpy.CreateFileGDB_management(inputfolder, filename)
	newpath = inputfolder+filename+".gdb"
	outpoints = newpath+"\\WGSPoints_"+filename
	outpoints2 = newpath+"\\TSSPoints_"+filename
	arcpy.MakeXYEventLayer_management(file, "Longitude", "Latitude", filename, WGScoord)
	arcpy.AddMessage("Event points constructed.")
	arcpy.CopyFeatures_management(filename, outpoints)
	arcpy.AddMessage("Feature Class points constructed.")
	arcpy.AddField_management(outpoints, "attributes", "TEXT", "", "", "500")
	cursor = arcpy.UpdateCursor(outpoints)
	for row in cursor:
		atts = str(row.Filename)+","+str(row.ST_NM)+","+str(row.Surface)+","+str(row.Design)+","+str(row.Lanes)+","+str(row.Comment)
		row.setValue("attributes", atts)
		cursor.updateRow(row)
	arcpy.Project_management(outpoints, outpoints2, TXcoord, "NAD_1983_To_WGS_1984_5")
	arcpy.AddMessage("Feature Class points reprojected.")
	outlines = newpath+"\\Lines_"+filename
	arcpy.PointsToLine_management(outpoints2, outlines, "attributes", "", "NO_CLOSE")
	arcpy.AddMessage("Feature Class lines constructed.")
	arcpy.AddField_management(outlines, "RTE_ID", "TEXT", "", "", "10")
	arcpy.AddField_management(outlines, "RTE_NM", "TEXT", "", "", "9")
	arcpy.AddField_management(outlines, "FULL_ST_NM", "TEXT", "", "", "30")
	arcpy.AddField_management(outlines, "SURFACE", "TEXT", "", "", "5")
	arcpy.AddField_management(outlines, "RTE_DIR", "TEXT", "", "", "8")
	arcpy.AddField_management(outlines, "LANES", "TEXT", "", "", "5")
	arcpy.AddField_management(outlines, "CMNT", "TEXT", "", "", "100")
	arcpy.AddField_management(outlines, "LENGTH", "DOUBLE")
	arcpy.CalculateField_management(outlines, "LENGTH", "!shape.length@MILES!","PYTHON")
	arcpy.DeleteField_management(outlines, "Id")
	arcpy.AddMessage("New fields created.")
	kursor = arcpy.UpdateCursor(outlines)
	for row in kursor:
		atty = row.getValue("attributes")
		attyList = atty.split(",")
		for item in attyList:
			routeID = str(attyList[0]).strip()
			fullstreet = str(attyList[1]).strip()
			surf = str(attyList[2]).strip()
			desig = str(attyList[3]).strip()
			lanez = str(attyList[4]).strip()
			commentz = str(attyList[5]).strip()
			row.setValue("RTE_ID",routeID)
			row.setValue("RTE_NM",routeID)
			row.setValue("FULL_ST_NM",fullstreet)
			row.setValue("SURFACE",surf)
			row.setValue("RTE_DIR",desig)
			row.setValue("LANES",lanez)
			row.setValue("CMNT",commentz)
			kursor.updateRow(row)
		arcpy.AddMessage("Fields updated.")
	arcpy.AddMessage("Creating table for SUBFILES...")
	arcpy.TableToTable_conversion(outlines,newpath+"\\","SUBFILES_"+filename,"","RTE_ID \"RTE_ID\" true true false 10 Text 0 0 ,First,#,"+outlines+",RTE_ID,-1,-1;RTE_NM \"RTE_NM\" true true false 9 Text 0 0 ,First,#,"+outlines+",RTE_NM,-1,-1;STREET_NAME \"STREET_NAME\" true true false 30 Text 0 0 ,First,#,"+outlines+",FULL_ST_NM,-1,-1;COMMENT \"COMMENT\" true true false 100 Text 0 0 ,First,#,"+outlines+",CMNT,-1,-1;SURFACE_TYPE \"SURFACE_TYPE\" true true false 50 Short 0 0 ,First,#,"+outlines+",SURFACE,-1,-1;HIGHWAY_DESIGN \"HIGHWAY_DESIGN\" true true false 50 Short 0 0 ,First,#,"+outlines+",RTE_DIR,-1,-1;NUMBER_OF_LANES \"NUMBER_OF_LANES\" true true false 50 Short 0 0 ,First,#,"+outlines+",LANES,-1,-1;LEN_OF_SECTION \"LEN_OF_SECTION\" true true false 50 Double 0 0 ,First,#,"+outlines+",LENGTH,-1,-1")
	outsubfiles = newpath+"\\SUBFILES_"+filename
	arcpy.AddField_management(outsubfiles, "SUBFILE", "SHORT")
	arcpy.AddField_management(outsubfiles, "DISTRICT", "SHORT")
	arcpy.AddField_management(outsubfiles, "COUNTY", "SHORT")
	arcpy.AddField_management(outsubfiles, "CONTROLSEC", "TEXT", "", "", "8")
	arcpy.AddField_management(outsubfiles, "HIGHWAY_STATUS", "SHORT")
	arcpy.AddField_management(outsubfiles, "SURFACE_WIDTH", "SHORT")
	arcpy.AddField_management(outsubfiles, "BASE_TYPE", "SHORT")
	arcpy.AddField_management(outsubfiles, "ROADBED_WIDTH", "SHORT")
	arcpy.AddField_management(outsubfiles, "ROW", "SHORT")
	arcpy.AddField_management(outsubfiles, "ADMIN_SYSTEM", "SHORT")
	arcpy.AddField_management(outsubfiles, "TOLL", "LONG")
	arcpy.AddField_management(outsubfiles, "BLANK", "TEXT", "", "", "3")
	arcpy.AddMessage("Populating...")
	arcpy.DeleteField_management(outsubfiles, "OID")
	qursor = arcpy.UpdateCursor(outsubfiles)
	for row in qursor:
		retrieveit = row.getValue("RTE_ID")
		routeIDparts = retrieveit.split("A")
		for item in routeIDparts:
			theCOUNTY = routeIDparts[0]
			try:
				routeIDparts[2]
				thecontrolsec = str("AA"+routeIDparts[-1])
			except:
				thecontrolsec = str("A"+routeIDparts[-1])
			row.setValue("COUNTY",theCOUNTY)
			row.setValue("SUBFILE",2)
			row.setValue("CONTROLSEC",thecontrolsec)
			row.setValue("HIGHWAY_STATUS",4)
			row.setValue("ADMIN_SYSTEM",3)
			row.setValue("TOLL",0)
			row.setValue("BLANK","0")
			surfvalue = row.getValue("SURFACE_TYPE")
			if surfvalue == 10:
				row.setValue("ROW",30)
				row.setValue("ROADBED_WIDTH",16)
				row.setValue("BASE_TYPE",0)
				row.setValue("SURFACE_WIDTH",16)
			elif surfvalue == 32:
				row.setValue("ROW",30)
				row.setValue("ROADBED_WIDTH",18)
				row.setValue("BASE_TYPE",0)
				row.setValue("SURFACE_WIDTH",16)
			elif surfvalue == 51:
				row.setValue("ROW",40)
				row.setValue("ROADBED_WIDTH",20)
				row.setValue("BASE_TYPE",2)
				row.setValue("SURFACE_WIDTH",18)
			elif surfvalue == 55:
				row.setValue("ROW",40)
				row.setValue("ROADBED_WIDTH",22)
				row.setValue("BASE_TYPE",4)
				row.setValue("SURFACE_WIDTH",20)
			elif surfvalue == 61:
				row.setValue("ROW",40)
				row.setValue("ROADBED_WIDTH",24)
				row.setValue("BASE_TYPE",1)
				row.setValue("SURFACE_WIDTH",24)
			else:
				row.setValue("ROW",30)
				row.setValue("ROADBED_WIDTH",18)
				row.setValue("BASE_TYPE",0)
				row.setValue("SURFACE_WIDTH",16)
			
			Abilene = [30,115,177,168,209,128,77,17,208,217,105,132,221]
			Amarillo = [6,191,59,188,91,33,180,118,104,171,107,197,99,148,179,211,56]
			Atlanta = [183,103,155,230,32,34,225,19,172]
			Austin = [28,106,11,87,16,144,227,150,157,27,246]
			Beaumont = [36,181,146,101,229,122,176,124]
			Brownwood = [141,206,160,167,25,42,47,68,215]
			Bryan = [26,94,21,236,154,166,198,145,82,239]
			Childress = [63,138,135,79,173,51,100,38,97,23,44,65,242]
			CorpusChristi = [178,126,205,4,196,13,149,89,129,137]
			Dallas = [175,71,130,199,57,61,43]
			ElPaso = [189,22,123,55,116,72]
			FortWorth = [213,73,112,220,184,182,249,120,127]
			Houston = [85,20,102,237,170,80]
			Laredo = [67,240,142,64,159,254,136,233]
			Lubbock = [84,58,251,223,153,86,111,40,152,54,78,9,96,140,185,35,219]
			Lufkin = [204,228,3,114,202,203,174,210,187]
			Odessa = [222,186,52,238,231,195,151,165,69,248,2,156]
			Paris = [190,113,81,117,60,75,139,92,194]
			Pharr = [31,245,109,214,24,66,253,125]
			SanAngelo = [193,70,218,134,53,164,207,119,48,192,226,200,41,216,88]
			SanAntonio = [162,83,7,247,232,163,15,95,10,46,131,133]
			Tyler = [1,37,108,93,212,234,250,201]
			Waco = [74,50,147,98,18,110,161,14]
			WichitaFalls = [252,224,12,5,49,39,243,244,169]
			Yoakum = [235,158,62,143,241,90,45,8,76,121,29]
			
			if int(theCOUNTY) in Abilene:
				row.setValue("DISTRICT",8)
			elif int(theCOUNTY) in Amarillo:
				row.setValue("DISTRICT",4)
			elif int(theCOUNTY) in Atlanta:
				row.setValue("DISTRICT",19)
			elif int(theCOUNTY) in Austin:
				row.setValue("DISTRICT",14)
			elif int(theCOUNTY) in Beaumont:
				row.setValue("DISTRICT",20)
			elif int(theCOUNTY) in Brownwood:
				row.setValue("DISTRICT",23)
			elif int(theCOUNTY) in Bryan:
				row.setValue("DISTRICT",17)
			elif int(theCOUNTY) in Childress:
				row.setValue("DISTRICT",25)
			elif int(theCOUNTY) in CorpusChristi:
				row.setValue("DISTRICT",16)
			elif int(theCOUNTY) in Dallas:
				row.setValue("DISTRICT",18)
			elif int(theCOUNTY) in ElPaso:
				row.setValue("DISTRICT",24)
			elif int(theCOUNTY) in FortWorth:
				row.setValue("DISTRICT",2)
			elif int(theCOUNTY) in Houston:
				row.setValue("DISTRICT",12)
			elif int(theCOUNTY) in Laredo:
				row.setValue("DISTRICT",22)
			elif int(theCOUNTY) in Lubbock:
				row.setValue("DISTRICT",5)
			elif int(theCOUNTY) in Lufkin:
				row.setValue("DISTRICT",11)
			elif int(theCOUNTY) in Odessa:
				row.setValue("DISTRICT",6)
			elif int(theCOUNTY) in Paris:
				row.setValue("DISTRICT",1)
			elif int(theCOUNTY) in Pharr:
				row.setValue("DISTRICT",21)
			elif int(theCOUNTY) in SanAngelo:
				row.setValue("DISTRICT",7)
			elif int(theCOUNTY) in SanAntonio:
				row.setValue("DISTRICT",15)
			elif int(theCOUNTY) in Tyler:
				row.setValue("DISTRICT",10)
			elif int(theCOUNTY) in Waco:
				row.setValue("DISTRICT",9)
			elif int(theCOUNTY) in WichitaFalls:
				row.setValue("DISTRICT",3)
			elif int(theCOUNTY) in Yoakum:
				row.setValue("DISTRICT",13)
			qursor.updateRow(row)
	arcpy.AddMessage("Organizing...")
	newcontainer = inputfolder+"Original_TXT"
	if not os.path.exists(newcontainer):
		os.makedirs(newcontainer)
	shutil.move(file,newcontainer+"\\")
	arcpy.AddMessage("Well, this file's done. Let's see if there's another one...")
arcpy.AddMessage("Nope, All Files Complete!")
