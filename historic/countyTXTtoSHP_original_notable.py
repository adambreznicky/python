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
	newpath = inputfolder+filename
	if not os.path.exists(newpath):
		os.makedirs(newpath)
	outpoints = newpath+"\\"+filename+"_WGSPoints.shp"
	outpoints2 = newpath+"\\"+filename+"_TSSPoints.shp"
	arcpy.MakeXYEventLayer_management(file, "Longitude", "Latitude", filename, WGScoord)
	arcpy.AddMessage("Event points constructed.")
	arcpy.CopyFeatures_management(filename, outpoints)
	arcpy.AddMessage("Shapefile points constructed.")
	arcpy.AddField_management(outpoints, "attributes", "TEXT", "", "", "500")
	cursor = arcpy.UpdateCursor(outpoints)
	for row in cursor:
		atts = str(row.Filename)+","+str(row.ST_NM)+","+str(row.Surface)+","+str(row.Design)+","+str(row.Lanes)+","+str(row.Comment)
		row.setValue("attributes", atts)
		cursor.updateRow(row)
	arcpy.Project_management(outpoints, outpoints2, TXcoord, "NAD_1983_To_WGS_1984_5")
	arcpy.AddMessage("Shapefile points reprojected.")
	outlines = newpath+"\\"+filename+"_Lines.shp"
	arcpy.PointsToLine_management(outpoints2, outlines, "attributes", "", "NO_CLOSE")
	arcpy.AddMessage("Shapefile lines constructed.")
	arcpy.AddField_management(outlines, "RTE_ID", "TEXT", "", "", "10")
	arcpy.AddField_management(outlines, "RTE_NM", "TEXT", "", "", "9")
	arcpy.AddField_management(outlines, "FULL_ST_NM", "TEXT", "", "", "75")
	arcpy.AddField_management(outlines, "SURFACE", "TEXT", "", "", "5")
	arcpy.AddField_management(outlines, "RTE_DIR", "TEXT", "", "", "8")
	arcpy.AddField_management(outlines, "LANES", "TEXT", "", "", "5")
	arcpy.AddField_management(outlines, "CMNT", "TEXT", "", "", "100")
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
	shutil.move(file,newpath+"\\")
	
	newCTYpath = inputfolder+filename.split("A")[0]
	if not os.path.exists(newCTYpath):
		os.makedirs(newCTYpath)
	shutil.move(newpath,newCTYpath+"\\")
	arcpy.AddMessage("Organizing...")
	arcpy.AddMessage("Well, this file's done. Let's see if there's another one...")
arcpy.AddMessage("Nope, All Files Complete!")
