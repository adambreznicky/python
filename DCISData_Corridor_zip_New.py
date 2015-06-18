import datetime
from datetime import date, timedelta
import arcpy
import os
from os import listdir
import random, string
from arcpy import env
import shutil
import glob
import zipfile
import time
import smtplib
import base64

start_time = time.time()

##currentDay = datetime.datetime.now().day
##currentMonth = datetime.datetime.now().month
##currentYear = datetime.datetime.now().year

today = datetime.datetime.now()

#Database name
old_fileName = today.strftime("%Y%m%d")
##old_fileName = str(currentMonth) + "-" + str(currentDay) + "-" + str(currentYear)
fileName = old_fileName + "DCIS_DB"
newfileName = old_fileName + "_DCIS_DB"

#Path variable
Path = "C:\\TxDOT\\Projects\\Corridor\\Data"
try:

    #--change directory name
    def changeDirectoryName(thePath):
        global Path

        myrg = random.SystemRandom()
        alphabet = string.letters[0:52] + string.digits
        newExt = str().join(myrg.choice(alphabet) for _ in range(6))

        if os.path.exists("C:\\TxDOT\\Projects\\Corridor\\Data" + old_fileName + ".gdb"):
            os.rename("C:\\TxDOT\\Projects\\Corridor\\Data" + old_fileName + ".gdb","C:\\TxDOT\\Projects\\Corridor\\Data" + old_fileName + "_" + newExt + ".gdb")

        if os.path.exists(thePath):
            os.rename(thePath,Path + "\\" + old_fileName + ".gdb")

    #--check if directory exists
    def checkDirectory(thePath):
        if not os.path.exists(thePath):
            os.makedirs(thePath)

    #--Check and Create Directories as needed
    def createDirectories():
        print "Verifying Directories..."
        checkDirectory("C:\TxDOT")
        checkDirectory("C:\TxDOT\Projects")
        checkDirectory("C:\TxDOT\Projects\Corridor")
        checkDirectory("C:\TxDOT\Projects\Corridor\Data")

    #--Create new .gdb
    def newDataBase():
        global Path
        global newfileName

        print "Creating new database..."
        arcpy.CreateFileGDB_management(Path, newfileName, "CURRENT")

    #--Import most recent DCIS data from Tarhe
    def importData():
        global Path
        global newfileName

        #Tables
        Tarhe_Project_Info = "Database Connections\\Tarhe.sde\\COMMON_DSGN.DCIS_PROJ_INFO_VW"
        Project_Info = Path + "\\" + newfileName + ".gdb\\Project_Info"

        Tarhe_Project_Cost = "Database Connections\\Tarhe.sde\\COMMON_DSGN.DCIS_PROJECT_COST_VW"
        Project_Cost = Path + "\\" + newfileName + ".gdb\\Project_Cost"

        Tarhe_Work_Program = "Database Connections\\Tarhe.sde\\COMMON_DSGN.DCIS_WORK_PROGRAM_VW"
        Work_Program = Path + "\\" + newfileName + ".gdb\\Work_Program"

        Tarhe_Project_Info_Work_Program = "Database Connections\\Tarhe.sde\\COMMON_DSGN.DCIS_PROJ_INFO_WORK_PGM_VW"
        Project_Info_Work_Program = Path + "\\" + newfileName + ".gdb\\Project_Info_Work_Program"

        print "Copying Project Info Table..."
        arcpy.Copy_management(Tarhe_Project_Info, Project_Info, "Table")

        print "Copying Project Cost Table..."
        arcpy.Copy_management(Tarhe_Project_Cost, Project_Cost, "Table")

        print "Copying Work Program Table..."
        arcpy.Copy_management(Tarhe_Work_Program, Work_Program, "Table")

        print "Copying Project Info Work Program Table..."
        arcpy.Copy_management(Tarhe_Project_Info_Work_Program, Project_Info_Work_Program, "Table")

    #--Export TxDOT Roadways for County Roads and FC Streets
    def exportOffSystem():
        print "Exporting Off System from TxDOT Roadways..."
        TPP_GIS_MCHAMB1_TXDOT_Roadways = "Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
        DCIS_DB_gdb = "C:\\TxDOT\\Projects\\Corridor\\Data\\"+ newfileName + ".gdb"

        #Use field mappings to simplify Feature Class to Feature Class export
        #fieldmappings = arcpy.FieldMappings()
        #fieldmappings.addTable(TPP_GIS_MCHAMB1_TXDOT_Roadways)

        #Feature Class to Feature Class
        arcpy.FeatureClassToFeatureClass_conversion(TPP_GIS_MCHAMB1_TXDOT_Roadways, DCIS_DB_gdb, "TxDOT_Roadways_Off_System", "RTE_CLASS = '2' OR RTE_CLASS = '3'", "RTE_NM \"Route Name\" true true false 9 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RTE_NM,-1,-1;RTE_CLASS \"Route Class\" true true false 25 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RTE_CLASS,-1,-1;RTE_DIR \"Direction\" true true false 8 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RTE_DIR,-1,-1;RTE_PRFX \"Route Prefix\" true true false 2 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RTE_PRFX,-1,-1;RTE_NBR \"Route Number\" true true false 5 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RTE_NBR,-1,-1;RTE_SFX \"Route Suffix\" true true false 1 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RTE_SFX,-1,-1;CMNT \"Comment\" true true false 100 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,CMNT,-1,-1;RDBD_TYPE \"Roadbed Type\" true true false 10 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RDBD_TYPE,-1,-1;RTE_LEN \"Route Length\" true true false 8 Double 8 38 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RTE_LEN,-1,-1;RTE_ORDER \"Route Order\" true true false 2 Short 0 5 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RTE_ORDER,-1,-1;PROPOSED \"PROPOSED\" true true false 2 Short 0 5 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,PROPOSED,-1,-1;FULL_ST_NM \"Full Street Name\" true true false 75 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,FULL_ST_NM,-1,-1;ST_PRFX \"Street Prefix\" true true false 15 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,ST_PRFX,-1,-1;ST_NM \"Street Name\" true true false 50 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,ST_NM,-1,-1;ST_SFX \"Street Suffix\" true true false 15 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,ST_SFX,-1,-1;ST_SFX_DIR \"Suffix Direction\" true true false 15 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,ST_SFX_DIR,-1,-1;CREATE_DT \"Created Date\" true true false 25 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,CREATE_DT,-1,-1;EDIT_DT \"Edited Date\" true true false 25 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,EDIT_DT,-1,-1;EDIT_NM \"Edited By\" true true false 25 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,EDIT_NM,-1,-1;RTE_ID \"Route ID\" true true false 10 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RTE_ID,-1,-1;RTE_OPEN \"RTE_OPEN\" true true false 2 Short 0 5 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RTE_OPEN,-1,-1;RTE_TOLL \"RTE_TOLL\" true true false 2 Short 0 5 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RTE_TOLL,-1,-1;RTE_CPLET \"RTE_CPLET\" true true false 2 Short 0 5 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,RTE_CPLET,-1,-1;SHAPE_len \"SHAPE_len\" false false true 0 Double 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways,SHAPE.len,-1,-1", "")

    #--Add the control section text field
    def addField(theField,thePath,theName):
        print "Adding " + theField + " field..."

        #Workspace
        env.workspace = thePath

        #Field variables
        inFeatures = theName
        fieldName1 = theField
        fieldAlias = theField
        fieldLength = 10

        #Add field
        arcpy.AddField_management(inFeatures, fieldName1, "TEXT", "", fieldLength)

    #--Add the control section text field
    def addFieldNumber(theField,thePath,theName,nbrType):
        print "Adding " + theField + " field..."

        #Workspace
        env.workspace = thePath

        #Add field
        arcpy.AddField_management(thePath + "\\" + theName, theField, nbrType, "", "", "", theField, "NULLABLE", "NON_REQUIRED", "")

    #--Calculate the field with control section
    def calculateField():
        global Path
        global newfileName

        print "Calculating CONTROL_SECTION field with Left(CONTROL_SECTION_JOB,6)"

        #Table
        Project_Info = Path + "\\" + newfileName + ".gdb\\Project_Info"

        #Calculate
        arcpy.CalculateField_management(Project_Info, "CONTROL_SECTION", "Left( [CONTROL_SECT_JOB] ,6)", "VB", "")

    #--Calculate the field for control section linework
    def calculateFieldTwo():
        global Path
        global newfileName

        print "Calculating CONTROL_SECTION field with Left(CNTRL_SEC,4) & Right(CNTRL_SEC,2)"

        #Table
        Project_Info = Path + "\\" + newfileName + ".gdb\\TxDOT_Roadways_ControlSection_Measures"

        #Calculate
        arcpy.CalculateField_management(Project_Info, "CONTROL_SECTION", "Left( [CNTRL_SEC] ,4) & Right( [CNTRL_SEC] ,2)", "VB", "")

    #--Make the control section linework from Comanche and replacing DFO measures with Milepoint measures
    def makeControlSectionLinework():
        global Path
        global newfileName

        #Variables
        TPP_GIS_MCHAMB1_TXDOT_Roadways = "Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
        TPP_GIS_MCHAMB1_RTE_CONTROL_SECTION = "Database Connections\\Comanche USER Direct.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.RTE_CONTROL_SECTION"
        dbName = Path + "\\" + newfileName + ".gdb"
        TPP_GIS_MCHAMB1_RTE_CONTROL_SECTION_Events = "TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events"
        ControlSections_Routed = Path + "\\" + newfileName + ".gdb\\ControlSections_Routed"
        TxDOT_Roadways_ControlSection_Measures = Path + "\\" + newfileName + ".gdb\\TxDOT_Roadways_ControlSection_Measures"

        print "Making the event layer..."
        arcpy.MakeRouteEventLayer_lr(TPP_GIS_MCHAMB1_TXDOT_Roadways, "RTE_ID", TPP_GIS_MCHAMB1_RTE_CONTROL_SECTION, "RIA_RTE_ID LINE GIS_FROM GIS_TO", TPP_GIS_MCHAMB1_RTE_CONTROL_SECTION_Events, "", "ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")

        print "Exporting the routed feature class..."
        arcpy.FeatureClassToFeatureClass_conversion(TPP_GIS_MCHAMB1_RTE_CONTROL_SECTION_Events, dbName, "ControlSections_Routed", "", "SUPER_FLAG \"SUPER_FLAG\" true false false 254 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,SUPER_FLAG,-1,-1;GIS_FROM \"GIS_FROM\" true false false 4 Float 3 6 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,GIS_FROM,-1,-1;GIS_TO \"GIS_TO\" true false false 4 Float 3 6 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,GIS_TO,-1,-1;TRM_FROM \"TRM_FROM\" true false false 4 Float 3 6 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,TRM_FROM,-1,-1;TRM_TO \"TRM_TO\" true false false 4 Float 3 6 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,TRM_TO,-1,-1;TRM_BMP \"TRM_BMP\" true false false 4 Float 3 6 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,TRM_BMP,-1,-1;TRM_EMP \"TRM_EMP\" true false false 4 Float 3 6 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,TRM_EMP,-1,-1;CS_FLAG \"CS_FLAG\" true false false 25 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,CS_FLAG,-1,-1;HWY_FLAG \"HWY_FLAG\" true false false 25 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,HWY_FLAG,-1,-1;RIA_RTE_ID \"RIA_RTE_ID\" true false false 25 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,RIA_RTE_ID,-1,-1;CNTRL_SEC \"CNTRL_SEC\" true false false 25 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,CNTRL_SEC,-1,-1;LRS_CMNT \"LRS_CMNT\" true false false 100 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,LRS_CMNT,-1,-1;BIN \"BIN\" true false false 2 Short 0 5 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,BIN,-1,-1;UNIQUE_ID \"UNIQUE_ID\" true false false 4 Long 0 10 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,UNIQUE_ID,-1,-1;DIST_NM \"DIST_NM\" true false false 25 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,DIST_NM,-1,-1;MPT_LEN \"MPT_LEN\" true false false 4 Float 3 6 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,MPT_LEN,-1,-1;GIS_LEN \"GIS_LEN\" true false false 4 Float 3 6 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,GIS_LEN,-1,-1;LEN_DIFF \"LEN_DIFF\" true false false 4 Float 3 6 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,LEN_DIFF,-1,-1;MEAS_GAP \"MEAS_GAP\" true false false 4 Float 3 6 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,MEAS_GAP,-1,-1;FROM_LAT \"FROM_LAT\" true true false 8 Double 10 20 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,FROM_LAT,-1,-1;FROM_LONG \"FROM_LONG\" true true false 8 Double 10 20 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,FROM_LONG,-1,-1;TO_LAT \"TO_LAT\" true true false 8 Double 10 20 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,TO_LAT,-1,-1;TO_LONG \"TO_LONG\" true true false 8 Double 10 20 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,TO_LONG,-1,-1;RDBD_TYPE \"Roadbed Type\" true true false 50 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,RDBD_TYPE,-1,-1;LOC_ERROR \"LOC_ERROR\" false true false 50 Text 0 0 ,First,#,Database Connections\\Comanche USER Direct.sde\\TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION Events,LOC_ERROR,-1,-1", "")

        print "Creating routes with control section measures..."
        arcpy.CreateRoutes_lr(ControlSections_Routed, "CNTRL_SEC", TxDOT_Roadways_ControlSection_Measures, "TWO_FIELDS", "TRM_BMP", "TRM_EMP", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    #--Append County Road and FC Streets to On System Routes with Control Section Measures.  This will allow off system projects to locate and map properly
    def appendOffSystem():
        print "Appending Off System to On System linework with control section measures..."
        TxDOT_Roadways_Off_System = "C:\\TxDOT\\Projects\\Corridor\\Data\\"+ newfileName + ".gdb\\TxDOT_Roadways_Off_System"
        TxDOT_Roadways_ControlSection_Measures__2_ = "C:\\TxDOT\\Projects\\Corridor\\Data\\"+ newfileName + ".gdb\\TxDOT_Roadways_ControlSection_Measures"

        #Append
        arcpy.Append_management("C:\\TxDOT\\Projects\\Corridor\\Data\\"+ newfileName + ".gdb\\TxDOT_Roadways_Off_System", TxDOT_Roadways_ControlSection_Measures__2_, "NO_TEST", "CNTRL_SEC \"CNTRL_SEC\" true true false 25 Text 0 0 ,First,#;Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\"+ newfileName + ".gdb\\TxDOT_Roadways_Off_System,Shape_Length,-1,-1;CONTROL_SECTION \"CONTROL_SECTION\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\"+ newfileName + ".gdb\\TxDOT_Roadways_Off_System,RTE_ID,-1,-1", "")

    #--Route the DCIS projects to the control section linework
    def routeDCISProjects():
        global Path
        global newfileName

        #Variables
        TxDOT_Roadways_ControlSection_Measures = Path + "\\" + newfileName + ".gdb\\TxDOT_Roadways_ControlSection_Measures"
        Project_Info = Path + "\\" + newfileName + ".gdb\\Project_Info"
        dbName = Path + "\\" + newfileName + ".gdb"
        Project_Info_Events = "DCIS Projects Mapped"

        print "Making the DCIS projects event layer..."
        arcpy.MakeRouteEventLayer_lr(TxDOT_Roadways_ControlSection_Measures, "CONTROL_SECTION", Project_Info, "CONTROL_SECTION LINE BEG_MILE_POINT END_MILE_POINT", Project_Info_Events, "", "ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")

        print "Exporting the DCIS event layer..."
        arcpy.FeatureClassToFeatureClass_conversion(Project_Info_Events, dbName, "DCIS_Mapped", "", "ISN \"ISN\" true false false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,ISN,-1,-1;CONTROL_SECT_JOB \"CONTROL_SECT_JOB\" true true false 9 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,CONTROL_SECT_JOB,-1,-1;DISTRICT_NUMBER \"DISTRICT_NUMBER\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,DISTRICT_NUMBER,-1,-1;DATE_LAST_REV \"DATE_LAST_REV\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,DATE_LAST_REV,-1,-1;TIME_LAST_REV \"TIME_LAST_REV\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,TIME_LAST_REV,-1,-1;COUNTY_NUMBER \"COUNTY_NUMBER\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,COUNTY_NUMBER,-1,-1;HIGHWAY_NUMBER \"HIGHWAY_NUMBER\" true true false 7 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,HIGHWAY_NUMBER,-1,-1;PROJ_LENGTH \"PROJ_LENGTH\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROJ_LENGTH,-1,-1;ELIG_FED_FUND \"ELIG_FED_FUND\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,ELIG_FED_FUND,-1,-1;PROJ_CLASS \"PROJ_CLASS\" true true false 3 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROJ_CLASS,-1,-1;MANAGER_NUMBER \"MANAGER_NUMBER\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,MANAGER_NUMBER,-1,-1;EST_CONST_COST \"EST_CONST_COST\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,EST_CONST_COST,-1,-1;DATE_EST_COST \"DATE_EST_COST\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,DATE_EST_COST,-1,-1;AUTO_LINE_NUMBER \"AUTO_LINE_NUMBER\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,AUTO_LINE_NUMBER,-1,-1;TYPE_OF_WORK \"TYPE_OF_WORK\" true true false 40 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,TYPE_OF_WORK,-1,-1;LIMITS_FROM \"LIMITS_FROM\" true true false 40 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LIMITS_FROM,-1,-1;LIMITS_TO \"LIMITS_TO\" true true false 40 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LIMITS_TO,-1,-1;LAYMAN_DESCRIPTION1 \"LAYMAN_DESCRIPTION1\" true true false 60 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LAYMAN_DESCRIPTION1,-1,-1;LAYMAN_DESCRIPTION2 \"LAYMAN_DESCRIPTION2\" true true false 60 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LAYMAN_DESCRIPTION2,-1,-1;BEG_MILE_POINT \"BEG_MILE_POINT\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,BEG_MILE_POINT,-1,-1;END_MILE_POINT \"END_MILE_POINT\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,END_MILE_POINT,-1,-1;CONTRACT_CSJ \"CONTRACT_CSJ\" true true false 9 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,CONTRACT_CSJ,-1,-1;PRIORITY_CODE \"PRIORITY_CODE\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PRIORITY_CODE,-1,-1;PDP_LET_DATE \"PDP_LET_DATE\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PDP_LET_DATE,-1,-1;DIST_LET_DATE \"DIST_LET_DATE\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,DIST_LET_DATE,-1,-1;ORIGINAL_PLANNED_LET_DATE \"ORIGINAL_PLANNED_LET_DATE\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,ORIGINAL_PLANNED_LET_DATE,-1,-1;DIST_LET_CHANGES_NBR \"DIST_LET_CHANGES_NBR\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,DIST_LET_CHANGES_NBR,-1,-1;APPRVD_LET_DATE \"APPRVD_LET_DATE\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,APPRVD_LET_DATE,-1,-1;ACTUAL_LET_DATE \"ACTUAL_LET_DATE\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,ACTUAL_LET_DATE,-1,-1;EST_ROW_COST \"EST_ROW_COST\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,EST_ROW_COST,-1,-1;DATE_EST_ROW \"DATE_EST_ROW\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,DATE_EST_ROW,-1,-1;RA_FLAG \"RA_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,RA_FLAG,-1,-1;OTHER_PART \"OTHER_PART\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,OTHER_PART,-1,-1;PROJECT_NUMBER \"PROJECT_NUMBER\" true true false 20 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROJECT_NUMBER,-1,-1;CONST_COMP \"CONST_COMP\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,CONST_COMP,-1,-1;PSE_COMP \"PSE_COMP\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PSE_COMP,-1,-1;ROW_COMP \"ROW_COMP\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,ROW_COMP,-1,-1;HIGHWAY_SYSTEM \"HIGHWAY_SYSTEM\" true true false 5 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,HIGHWAY_SYSTEM,-1,-1;REMARKS \"REMARKS\" true true false 60 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,REMARKS,-1,-1;DIST_ENG_EST \"DIST_ENG_EST\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,DIST_ENG_EST,-1,-1;MISC_COST \"MISC_COST\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,MISC_COST,-1,-1;PROJ_BID_AMOUNT \"PROJ_BID_AMOUNT\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROJ_BID_AMOUNT,-1,-1;TOT_OBG_AMOUNT \"TOT_OBG_AMOUNT\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,TOT_OBG_AMOUNT,-1,-1;EC_PERCENT \"EC_PERCENT\" true true false 4 Float 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,EC_PERCENT,-1,-1;ITEM_500_AMOUNT \"ITEM_500_AMOUNT\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,ITEM_500_AMOUNT,-1,-1;RDWY_FUNCT_CLS \"RDWY_FUNCT_CLS\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,RDWY_FUNCT_CLS,-1,-1;URBAN_RURAL \"URBAN_RURAL\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,URBAN_RURAL,-1,-1;PVMT_TYPE \"PVMT_TYPE\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PVMT_TYPE,-1,-1;EXST_MNLN_NUM \"EXST_MNLN_NUM\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,EXST_MNLN_NUM,-1,-1;EXST_MNLN_TYPE \"EXST_MNLN_TYPE\" true true false 2 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,EXST_MNLN_TYPE,-1,-1;EXST_FTG_NUM \"EXST_FTG_NUM\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,EXST_FTG_NUM,-1,-1;EXST_FTG_TYPE \"EXST_FTG_TYPE\" true true false 2 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,EXST_FTG_TYPE,-1,-1;EXST_LENGTH \"EXST_LENGTH\" true true false 4 Float 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,EXST_LENGTH,-1,-1;PROP_MNLN_NUM \"PROP_MNLN_NUM\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROP_MNLN_NUM,-1,-1;PROP_MNLN_TYPE \"PROP_MNLN_TYPE\" true true false 2 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROP_MNLN_TYPE,-1,-1;PROP_FTG_NUM \"PROP_FTG_NUM\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROP_FTG_NUM,-1,-1;PROP_FTG_TYPE \"PROP_FTG_TYPE\" true true false 2 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROP_FTG_TYPE,-1,-1;PROP_LENGTH \"PROP_LENGTH\" true true false 4 Float 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROP_LENGTH,-1,-1;EVAC_RTE \"EVAC_RTE\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,EVAC_RTE,-1,-1;LANE_MILES \"LANE_MILES\" true true false 4 Float 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LANE_MILES,-1,-1;SHLDR_MILES \"SHLDR_MILES\" true true false 4 Float 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,SHLDR_MILES,-1,-1;PRES_ADT \"PRES_ADT\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PRES_ADT,-1,-1;PROJ_ADT_YEAR \"PROJ_ADT_YEAR\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROJ_ADT_YEAR,-1,-1;PROJ_ADT \"PROJ_ADT\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROJ_ADT,-1,-1;PERCENT_TRUCKS \"PERCENT_TRUCKS\" true true false 4 Float 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PERCENT_TRUCKS,-1,-1;PROP_DSGN_SPD \"PROP_DSGN_SPD\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROP_DSGN_SPD,-1,-1;PES1_LANES \"PES1_LANES\" true true false 2 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PES1_LANES,-1,-1;PES1_SCORE \"PES1_SCORE\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PES1_SCORE,-1,-1;PES2_LANES \"PES2_LANES\" true true false 2 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PES2_LANES,-1,-1;PES2_SCORE \"PES2_SCORE\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PES2_SCORE,-1,-1;TERRAIN \"TERRAIN\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,TERRAIN,-1,-1;CITY_CODE \"CITY_CODE\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,CITY_CODE,-1,-1;DIST_PRIOR \"DIST_PRIOR\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,DIST_PRIOR,-1,-1;COMMENTS1 \"COMMENTS1\" true true false 65 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,COMMENTS1,-1,-1;COMMENTS2 \"COMMENTS2\" true true false 65 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,COMMENTS2,-1,-1;COMMENTS4 \"COMMENTS4\" true true false 65 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,COMMENTS4,-1,-1;ENGINEER_NO \"ENGINEER_NO\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,ENGINEER_NO,-1,-1;AUTHORIZATION_DATE \"AUTHORIZATION_DATE\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,AUTHORIZATION_DATE,-1,-1;LET_SCH_LOCK_FLAG \"LET_SCH_LOCK_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LET_SCH_LOCK_FLAG,-1,-1;LET_SCH_1 \"LET_SCH_1\" true true false 4 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LET_SCH_1,-1,-1;LET_SCH_2 \"LET_SCH_2\" true true false 2 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LET_SCH_2,-1,-1;LET_SCH_3 \"LET_SCH_3\" true true false 2 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LET_SCH_3,-1,-1;SPEC_BOOK_YR \"SPEC_BOOK_YR\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,SPEC_BOOK_YR,-1,-1;TRUNK_SYS_FLAG \"TRUNK_SYS_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,TRUNK_SYS_FLAG,-1,-1;BEG_REF_MARKER_NBR \"BEG_REF_MARKER_NBR\" true true false 5 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,BEG_REF_MARKER_NBR,-1,-1;BEG_REF_MARKER_DISP \"BEG_REF_MARKER_DISP\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,BEG_REF_MARKER_DISP,-1,-1;END_REF_MARKER_NBR \"END_REF_MARKER_NBR\" true true false 5 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,END_REF_MARKER_NBR,-1,-1;END_REF_MARKER_DISP \"END_REF_MARKER_DISP\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,END_REF_MARKER_DISP,-1,-1;MPO_CODE \"MPO_CODE\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,MPO_CODE,-1,-1;TIP_FY \"TIP_FY\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,TIP_FY,-1,-1;COMMENTS3 \"COMMENTS3\" true true false 65 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,COMMENTS3,-1,-1;HISTORICAL_BRIDGE_FLAG \"HISTORICAL_BRIDGE_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,HISTORICAL_BRIDGE_FLAG,-1,-1;BRIDGE_LAST_UPDATED_DATE \"BRIDGE_LAST_UPDATED_DATE\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,BRIDGE_LAST_UPDATED_DATE,-1,-1;LINE_NUMBER_CARD12 \"LINE_NUMBER_CARD12\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LINE_NUMBER_CARD12,-1,-1;KOW_BROAD_CODE \"KOW_BROAD_CODE\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,KOW_BROAD_CODE,-1,-1;SEG_ID \"SEG_ID\" true true false 2 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,SEG_ID,-1,-1;MAINT_FUNCTION_CODE \"MAINT_FUNCTION_CODE\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,MAINT_FUNCTION_CODE,-1,-1;ADDL_ROW_METRIC_MEAS \"ADDL_ROW_METRIC_MEAS\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,ADDL_ROW_METRIC_MEAS,-1,-1;EXIST_LENGTH_METRIC_MEAS \"EXIST_LENGTH_METRIC_MEAS\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,EXIST_LENGTH_METRIC_MEAS,-1,-1;PROP_LENGTH_METRIC_MEAS \"PROP_LENGTH_METRIC_MEAS\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROP_LENGTH_METRIC_MEAS,-1,-1;LANE_LENGTH_METRIC_MEAS \"LANE_LENGTH_METRIC_MEAS\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LANE_LENGTH_METRIC_MEAS,-1,-1;PROJ_LENGTH_METRIC_MEAS \"PROJ_LENGTH_METRIC_MEAS\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PROJ_LENGTH_METRIC_MEAS,-1,-1;SHLDR_LENGTH_METRIC_MEAS \"SHLDR_LENGTH_METRIC_MEAS\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,SHLDR_LENGTH_METRIC_MEAS,-1,-1;LOCAL_CONTRIBUTIONS_AMT \"LOCAL_CONTRIBUTIONS_AMT\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LOCAL_CONTRIBUTIONS_AMT,-1,-1;STIP_PROJECT_ID \"STIP_PROJECT_ID\" true true false 20 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,STIP_PROJECT_ID,-1,-1;STIP_PHASE_CODE \"STIP_PHASE_CODE\" true true false 8 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,STIP_PHASE_CODE,-1,-1;STIP_REVISION_DATE \"STIP_REVISION_DATE\" true true false 8 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,STIP_REVISION_DATE,-1,-1;STIP_IMPLEMENT_AGENCY_CMNT \"STIP_IMPLEMENT_AGENCY_CMNT\" true true false 15 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,STIP_IMPLEMENT_AGENCY_CMNT,-1,-1;STIP_REVISION_LOCK_FLAG \"STIP_REVISION_LOCK_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,STIP_REVISION_LOCK_FLAG,-1,-1;STIP_PROJECT_DESCRIPTION1 \"STIP_PROJECT_DESCRIPTION1\" true true false 65 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,STIP_PROJECT_DESCRIPTION1,-1,-1;STIP_PROJECT_DESCRIPTION2 \"STIP_PROJECT_DESCRIPTION2\" true true false 65 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,STIP_PROJECT_DESCRIPTION2,-1,-1;STIP_PROJECT_DESCRIPTION3 \"STIP_PROJECT_DESCRIPTION3\" true true false 65 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,STIP_PROJECT_DESCRIPTION3,-1,-1;STATEWIDE_CSJ \"STATEWIDE_CSJ\" true true false 9 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,STATEWIDE_CSJ,-1,-1;RESP_SECTION \"RESP_SECTION\" true true false 3 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,RESP_SECTION,-1,-1;NATIONAL_HIGHWAY_SYSTEM_FLAG \"NATIONAL_HIGHWAY_SYSTEM_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,NATIONAL_HIGHWAY_SYSTEM_FLAG,-1,-1;CONSULTANT_FLAG \"CONSULTANT_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,CONSULTANT_FLAG,-1,-1;DONATED_FLAG \"DONATED_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,DONATED_FLAG,-1,-1;COMMENTS5 \"COMMENTS5\" true true false 65 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,COMMENTS5,-1,-1;TAPERED_MATCH \"TAPERED_MATCH\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,TAPERED_MATCH,-1,-1;TOLL_CREDITS \"TOLL_CREDITS\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,TOLL_CREDITS,-1,-1;PART_WAIVED_PROJECT \"PART_WAIVED_PROJECT\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PART_WAIVED_PROJECT,-1,-1;ECON_DIS_CO_PROJECT \"ECON_DIS_CO_PROJECT\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,ECON_DIS_CO_PROJECT,-1,-1;STATE_LOA \"STATE_LOA\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,STATE_LOA,-1,-1;POPULATION_AREA \"POPULATION_AREA\" true true false 3 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,POPULATION_AREA,-1,-1;DESIGN_STANDARD \"DESIGN_STANDARD\" true true false 2 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,DESIGN_STANDARD,-1,-1;PE_FEDERAL_LOA \"PE_FEDERAL_LOA\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PE_FEDERAL_LOA,-1,-1;PE_APPN_CODE \"PE_APPN_CODE\" true true false 4 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PE_APPN_CODE,-1,-1;PE_FEDERAL_DOLLARS \"PE_FEDERAL_DOLLARS\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PE_FEDERAL_DOLLARS,-1,-1;PE_DISTRICT \"PE_DISTRICT\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PE_DISTRICT,-1,-1;MAX_FED_FUNDS \"MAX_FED_FUNDS\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,MAX_FED_FUNDS,-1,-1;TO_DISTANCE_FROM_ORIGIN \"TO_DISTANCE_FROM_ORIGIN\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,TO_DISTANCE_FROM_ORIGIN,-1,-1;FROM_DISTANCE_FROM_ORIGIN \"FROM_DISTANCE_FROM_ORIGIN\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,FROM_DISTANCE_FROM_ORIGIN,-1,-1;BRIDGE_REMARKS1 \"BRIDGE_REMARKS1\" true true false 65 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,BRIDGE_REMARKS1,-1,-1;BRIDGE_REMARKS2 \"BRIDGE_REMARKS2\" true true false 65 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,BRIDGE_REMARKS2,-1,-1;MATCH_AMOUNT_TOTAL \"MATCH_AMOUNT_TOTAL\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,MATCH_AMOUNT_TOTAL,-1,-1;TOTAL_COST_DOLLAR_PE \"TOTAL_COST_DOLLAR_PE\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,TOTAL_COST_DOLLAR_PE,-1,-1;BOND_INTEREST_PAY_AMT \"BOND_INTEREST_PAY_AMT\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,BOND_INTEREST_PAY_AMT,-1,-1;INTEREST_TYPE_CODE \"INTEREST_TYPE_CODE\" true true false 2 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,INTEREST_TYPE_CODE,-1,-1;CMCS_LET_FLAG \"CMCS_LET_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,CMCS_LET_FLAG,-1,-1;TRM_UPDATE_FLAG \"TRM_UPDATE_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,TRM_UPDATE_FLAG,-1,-1;PRESERVATION_PERCENT \"PRESERVATION_PERCENT\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PRESERVATION_PERCENT,-1,-1;MOBILITY_PERCENT \"MOBILITY_PERCENT\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,MOBILITY_PERCENT,-1,-1;ROW_CSJ \"ROW_CSJ\" true true false 9 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,ROW_CSJ,-1,-1;MEGA_PROJECT_ID \"MEGA_PROJECT_ID\" true true false 5 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,MEGA_PROJECT_ID,-1,-1;LOCK_FLAG_P02 \"LOCK_FLAG_P02\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LOCK_FLAG_P02,-1,-1;ABATEMENT_AUTH_DATE \"ABATEMENT_AUTH_DATE\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,ABATEMENT_AUTH_DATE,-1,-1;BRIDGE_INDICATOR_FLAG \"BRIDGE_INDICATOR_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,BRIDGE_INDICATOR_FLAG,-1,-1;STRAHNET_FLAG \"STRAHNET_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,STRAHNET_FLAG,-1,-1;PDP_CODE \"PDP_CODE\" true true false 5 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PDP_CODE,-1,-1;ELS_PROJECT_FLAG \"ELS_PROJECT_FLAG\" true true false 1 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,ELS_PROJECT_FLAG,-1,-1;DISTRICT_BUDGETED_AMOUNT \"DISTRICT_BUDGETED_AMOUNT\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,DISTRICT_BUDGETED_AMOUNT,-1,-1;LOCAL_GOVT_CODE \"LOCAL_GOVT_CODE\" true true false 2 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LOCAL_GOVT_CODE,-1,-1;LOCAL_GOVT_AGENCY_NAME \"LOCAL_GOVT_AGENCY_NAME\" true true false 30 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LOCAL_GOVT_AGENCY_NAME,-1,-1;LOCAL_GOVT_AGENCY_CONTACT \"LOCAL_GOVT_AGENCY_CONTACT\" true true false 30 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LOCAL_GOVT_AGENCY_CONTACT,-1,-1;LOCAL_GOVT_AGENCY_ADDRESS \"LOCAL_GOVT_AGENCY_ADDRESS\" true true false 30 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LOCAL_GOVT_AGENCY_ADDRESS,-1,-1;LOCAL_GOVT_AGENCY_CITY \"LOCAL_GOVT_AGENCY_CITY\" true true false 25 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LOCAL_GOVT_AGENCY_CITY,-1,-1;LOCAL_GOVT_AGENCY_ZIP \"LOCAL_GOVT_AGENCY_ZIP\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LOCAL_GOVT_AGENCY_ZIP,-1,-1;LOCAL_GOVT_LET_DATE \"LOCAL_GOVT_LET_DATE\" true true false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LOCAL_GOVT_LET_DATE,-1,-1;LOCAL_GOVT_AGENCY_PHONE \"LOCAL_GOVT_AGENCY_PHONE\" true true false 8 Double 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LOCAL_GOVT_AGENCY_PHONE,-1,-1;LOCAL_GOVT_AGENCY_EMAIL \"LOCAL_GOVT_AGENCY_EMAIL\" true true false 40 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LOCAL_GOVT_AGENCY_EMAIL,-1,-1;LATEST_PEDES_ELEMENT \"LATEST_PEDES_ELEMENT\" true false false 8 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LATEST_PEDES_ELEMENT,-1,-1;EABPRJ \"EABPRJ\" true false false 8 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,EABPRJ,-1,-1;PE_DATE \"PE_DATE\" true false false 4 Long 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,PE_DATE,-1,-1;CONTROL_SECTION \"CONTROL_SECTION\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,CONTROL_SECTION,-1,-1;LOC_ERROR \"LOC_ERROR\" false true false 50 Text 0 0 ,First,#,C:\\TxDOT\\Projects\\Corridor\\Data\\12-10-2013.gdb\\Project_Info Events,LOC_ERROR,-1,-1", "")

    #--Export DCIS Project with mapped length greater than 0
    def exportValidDCISProjects():
        global Path
        global newfileName

        #Variables
        DCIS_Mapped = Path + "\\" + newfileName + ".gdb\\DCIS_Mapped"
        DCIS_Mapped_Valid_Locations = Path + "\\" + newfileName + ".gdb\\DCIS_Mapped_Valid_Locations"

        print "Export all records.  Even records with shape length equal to 0..."
        #Old select function that exported records with a length -- do not use, we need all records
        #arcpy.Select_analysis(DCIS_Mapped, DCIS_Mapped_Valid_Locations, "\"Shape_Length\" >0")
        arcpy.Select_analysis(DCIS_Mapped, DCIS_Mapped_Valid_Locations, "")

    #--Calculate 0 for BMP's that are null and EMP is greater than 0
    def calculateZeroBMPs():
        projectData = "C:\\TxDOT\\Projects\\Corridor\\Data\\"+ newfileName + ".gdb\\Project_Info"

        #Loop to update each record if needed
        cursor = arcpy.UpdateCursor(projectData,"","","","")
        counter = 0
        for row in cursor:
            if not row.BEG_MILE_POINT:
                if row.END_MILE_POINT > 0:
                    row.BEG_MILE_POINT = 0

            cursor.updateRow(row)

    #--Program to import and prep data from external data sources
    print "Begin: " + str(datetime.datetime.now().time())
    changeDirectoryName("C:\\TxDOT\\Projects\\Corridor\\Data\\"+ newfileName + ".gdb")
    createDirectories()
    newDataBase()
    importData()
    exportOffSystem()

    #Add fields to the Project Info table for scoring and routing columns
    addField("CONTROL_SECTION",Path + "\\" + newfileName + ".gdb","Project_Info")

    #Make the linework compatible with DCIS projects by applying control section measures and creating a routable field.
    calculateField()
    calculateZeroBMPs()
    makeControlSectionLinework()
    addField("CONTROL_SECTION",Path + "\\" + newfileName + ".gdb","TxDOT_Roadways_ControlSection_Measures")
    calculateFieldTwo()

    #Append off system (County Roads and FC Streets) to make a full coverage network
    appendOffSystem()

    #Route the DCIS projects
    routeDCISProjects()

    #Going to use all records instead of only records with shape greater than 0
    exportValidDCISProjects()


    # Delete unwanted feature classes
    print "Deleting unwanted feature classes..."
    arcpy.Delete_management(Path + "\\" + newfileName + ".gdb\\ControlSections_Routed")
    arcpy.Delete_management(Path + "\\" + newfileName + ".gdb\\DCIS_Mapped")
    arcpy.Delete_management(Path + "\\" + newfileName + ".gdb\\TxDOT_Roadways_ControlSection_Measures")
    arcpy.Delete_management(Path + "\\" + newfileName + ".gdb\\TxDOT_Roadways_Off_System")

    # Zip .gdb for delivery to T: drive
    print "Zipping .gdb..."
    infile = "C:\\TxDOT\\Projects\\Corridor\\Data\\"+ newfileName + ".gdb"
    outfile = "C:\\TxDOT\\Projects\\Corridor\\Data\\"+ newfileName + ".zip"
    def zipFileGeodatabase(inFileGeodatabase, newZipFN):
       if not (os.path.exists(inFileGeodatabase)):
          return False

       if (os.path.exists(newZipFN)):
          os.remove(newZipFN)

       zipobj = zipfile.ZipFile(newZipFN,'w')

       for infile in glob.glob(inFileGeodatabase+"/*"):
            if not infile.endswith('.lock'):
                zipobj.write(infile, os.path.basename(inFileGeodatabase)+"/"+os.path.basename(infile), zipfile.ZIP_DEFLATED)

       zipobj.close()

       return True

    zipFileGeodatabase(infile,outfile)

    print "Sending Zip File to T: drive....."
    # Copy Zip File to Loader (T:)
    shutil.copy(outfile, r"T:\DATAMGT\MAPPING\Data Transmittals\2014\Karen Lorenzini_Corridor")



    # password = base64.b64decode('VGVubmlzMDU=')
    password = "Saturday123"

    #Set up email variables for sending email
    SUBJECT = "Delivery Notification: DCIS Mapped Locations "
    TO = ['Jeremy.Rogers@txdot.gov','Karen.Lorenzini@txdot.gov','Jason.Ferrell@txdot.gov']
    FROM = "Adam.Breznicky@txdot.gov"
    text = "T:\ DATAMGT \ MAPPING \ Data Transmittals \ 2014 \ Karen Lorenzini_Corridor"
    BODY = string.join((
            "From: %s" % FROM,
            "To: %s" % TO,
            "Subject: %s" % SUBJECT,
            "",
            text
            ),"\r\n")



    #define server email is to be sent from
    server = smtplib.SMTP ('owa.txdot.gov',25)
    server.starttls()
    server.ehlo()
    server.login('Adam.Breznicky@txdot.gov',password)

    #Send email
    server.sendmail (FROM, TO, BODY)

    server.quit()

    end_time = time.time()
    print "Elapsed time: {0}".format(time.strftime('%H:%M:%S', time.gmtime(end_time - start_time)))

except Exception:

    # password = base64.b64decode('VGVubmlzMDU=')
    password = "Saturday123"

    #Set up email variables for sending email
    SUBJECT = "Script Failure Notification!!"
    TO = ['Jeremy.Rogers@txdot.gov','Jason.Ferrell@txdot.gov']
    FROM = "Adam.Breznicky@txdot.gov"
    text = "Delivery Failure"
    BODY = string.join((
            "From: %s" % FROM,
            "To: %s" % TO,
            "Subject: %s" % SUBJECT,
            "",
            text
            ),"\r\n")


    #define server email is to be sent from
    server = smtplib.SMTP ('owa.txdot.gov',25)
    server.starttls()
    server.ehlo()
    server.login('Adam.Breznicky@txdot.gov',password)

    #Send email
    server.sendmail (FROM, TO, BODY)

    server.quit()

    end_time = time.time()
    print "Elapsed time: {0}".format(time.strftime('%H:%M:%S', time.gmtime(end_time - start_time)))
