#County Road Inventory Mapbooks
#Adam Breznicky. January 2014
#requires installation of ReportLab and PyPDF22
#T:\DATAMGT\MAPPING\Programs\Arc10\Arc10_Tools\Modules
#
#
#
#

#imports
import arcpy, os, string, zipfile, shutil, PyPDF2, tablib
from arcpy import mapping
from PyPDF2 import PdfFileMerger, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, Paragraph, frames, Table, TableStyle, Frame, flowables, Flowable, PageTemplate
import datetime

now = datetime.datetime.now()
month = now.strftime("%B")
suffixDate = now.strftime("%Y%m%d")

arcpy.AddMessage(str(now))
#
#
#Variables:
#
#



#INPUT VARIABLES:
#variables listed and commented out for optional use as an arcgis tool
# cycle = arcpy.GetParameterAsText(0)
# dataYear = arcpy.GetParameterAsText(1)
# dbaseNAME = arcpy.GetParameterAsText(2)
# output = arcpy.GetParameterAsText(3)
cycle = "North"
dataYear = "2014"
dbaseNAME = "Connection to Comanche.sde"
output = "C:\\TxDOT\\County Road Inventory Mapbooks\\official\\QC_North_20140226"
# for maximum performance efficiency and this script to run: copy the 'Resources' folder
# from the T drive from here: T:\DATAMGT\MAPPING\Mapping Products\County Road Inventory Mapbooks
#input the location of the 'Resources' folder on your local machine by populating this path variable
resourcesFolder = "C:\\TxDOT\\County Road Inventory Mapbooks"

#DEPENDENT VARIABLES
#if not os.path.exists(output + os.sep + dataYear):
#    os.makedirs(output + os.sep + dataYear)
outputDir = output + os.sep + dataYear

#create working geodatabase
#arcpy.CreateFileGDB_management(outputDir, "Working_Data.gdb")
workspace = outputDir + os.sep + "Working_Data.gdb"



#SHAPEFILE/FC VARIABLES
if cycle == "North":
    CountyLayer = resourcesFolder + "\\Resources\\South and North County Shapefiles\\NorthCounties.shp"
elif cycle == "South":
    CountyLayer = resourcesFolder + "\\Resources\\South and North County Shapefiles\\SouthCounties.shp"
else:
    arcpy.AddError("You must use ether 'North' or 'South' for your cycle option")

#inventory2 = workspace + os.sep + "Roadway_Events_Dissolved"
#projectedRoads = workspace + os.sep + "Roadway_Events_Projected"
dissRoads = workspace + os.sep + "RoadLog_Dissolved"

#DIRECTORY VARIABLES
#CoversFolder = outputDir + os.sep + "Covers"
#LegendFolder = outputDir + os.sep + "Legend"
#IndexFolder = outputDir + os.sep + "GridIndexes"
#ShapefileFolder = outputDir + os.sep + "Shapefiles"
#MapPagesFolder = outputDir + os.sep + "MapPages"
#MapBooksFolder = outputDir + os.sep + "Combined_PDF"
RoadLogFolder = outputDir + os.sep + "RoadLog"
PDFLogFolder = RoadLogFolder + os.sep + "PDF_alpha"
#completedPackets = outputDir + os.sep + "_Completed_Packets"
#descriptiveDirectory = completedPackets + os.sep + "_Descriptive_PDFs"
#
#dataGDB = outputDir + os.sep + "Data_Copy.gdb"
#GridLayer = dataGDB + os.sep + "County_Grids_22K"
#subfiles = dataGDB + os.sep + "SUBFILES"
#txdotRoadways = dataGDB + os.sep + "TXDOT_Roadways"
#prevYear = str(int(dataYear) - 1)
#pubRDS = dataGDB + os.sep + "TXDOT_RTE_RDBD_LN_" + prevYear + "_Q4"

#compile global county name and number lists
lowerNames = []
upperNames = []
countyNumbers = []
cursor = arcpy.SearchCursor(CountyLayer)
for row in cursor:
    lowerNames.append(str(row.CNTY_NM))
    upperNames.append(str(row.CNTY_NM).upper())
    countyNumbers.append(str(row.CNTY_NBR).replace('.0', "")) # adjusted to fix float problem
del cursor
arcpy.AddMessage("County names and numbers lists compiled.")
#create global county total mileage dictionary for use with report functions
countyTotals = {}


#
#
#
#Define the functions of the process
#
#
#

#copy data local
def copyDataLocal():
    #create a file GDB and copy Comanche data local
    arcpy.CreateFileGDB_management(outputDir, "Data_Copy.gdb")
    arcpy.AddMessage("Database created.")

    arcpy.Copy_management(
        "Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.Map_Index_Grids\\TPP_GIS.MCHAMB1.County_Grids_22K",
        dataGDB + os.sep + "County_Grids_22K")
    arcpy.AddMessage("County Grids copied.")
    arcpy.Copy_management("Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.SUBFILES",
                          dataGDB + os.sep + "SUBFILES")
    arcpy.AddMessage("SUBFILES copied.")
    arcpy.Copy_management(
        "Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.Roadways\\TPP_GIS.MCHAMB1.TXDOT_Roadways",
        dataGDB + os.sep + "TXDOT_Roadways")
    arcpy.AddMessage("TxDOT Roadways copied.")
    arcpy.Copy_management(
        "Database Connections\\"+dbaseNAME+"\\TPP_GIS.APP_TPP_GIS_ADMIN.Outbound\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_RTE_RDBD_LN_" + prevYear + "_Q4",
        dataGDB + os.sep + "TXDOT_RTE_RDBD_LN_" + prevYear + "_Q4")
    arcpy.AddMessage("Q4 Outbound Roadways copied.")
    arcpy.Copy_management("Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.County\\TPP_GIS.MCHAMB1.County",
                          dataGDB + os.sep + "Counties")
    arcpy.AddMessage("County Boundaries copied.")
    arcpy.Copy_management("Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.City\\TPP_GIS.MCHAMB1.City",
                          dataGDB + os.sep + "Cities")
    arcpy.AddMessage("Cities copied.")
    arcpy.Copy_management(
        "Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.Roadways\\TPP_GIS.MCHAMB1.City_Streets",
        dataGDB + os.sep + "Streets")
    arcpy.AddMessage("City Streets copied.")
    arcpy.Copy_management("Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.City\\TPP_GIS.MCHAMB1.City_Points",
                          dataGDB + os.sep + "City_Points")
    arcpy.Copy_management("Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.Water\\TPP_GIS.MCHAMB1.Dams",
                          dataGDB + os.sep + "Dam")
    arcpy.Copy_management(
        "Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.Water\\TPP_GIS.MCHAMB1.Water_Bodies",
        dataGDB + os.sep + "Water_Bodies")
    arcpy.Copy_management("Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.Water\\TPP_GIS.MCHAMB1.Streams",
                          dataGDB + os.sep + "Streams")
    arcpy.AddMessage("Streams copied.")
    arcpy.Copy_management("Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.Park\\TPP_GIS.MCHAMB1.Public_Lands",
                          dataGDB + os.sep + "Public_Lands")
    arcpy.AddMessage("Public Lands copied.")
    arcpy.AddMessage("Comanche data copied local.")



#
#1
#COVER
#
#
def createCovers():
    arcpy.AddMessage("Generating Covers...")
    #make directory
    os.makedirs(outputDir + os.sep + "Covers")

    map = arcpy.mapping.MapDocument(resourcesFolder + "\\Resources\\MXD\\CRI_Covers.mxd")
    dataFrame = arcpy.mapping.ListDataFrames(map)[0]

    for i in lowerNames:
        for textElement in arcpy.mapping.ListLayoutElements(map, "TEXT_ELEMENT"):
            if textElement.name == "CountyName":
                textElement.text = i + " - " + dataYear
            if textElement.name == "Year":
                textElement.text = "Copyright " + dataYear + " TxDOT"

        arcpy.AddMessage(i + " Cover Complete.")
        arcpy.mapping.ExportToPDF(map, CoversFolder + os.sep + i)
    del map
    del dataFrame
    arcpy.AddMessage("Covers Complete.")


#
#2
#LEGEND
#
#
def createLegend():
    arcpy.AddMessage("Generating Legend...")
    #make directory
    os.makedirs(outputDir + os.sep + "Legend")

    lastYear = int(dataYear) - 1

    map = arcpy.mapping.MapDocument(resourcesFolder + "\\Resources\\MXD\\Legend.mxd")
    dataFrame = arcpy.mapping.ListDataFrames(map)[0]
    for textElement in arcpy.mapping.ListLayoutElements(map, "TEXT_ELEMENT"):
        if textElement.name == "Title":
            textElement.text = "County Road Inventory " + str(dataYear)
        if textElement.name == "Copyright":
            textElement.text = "Copyright " + str(dataYear) + " Texas Department of Transportation "
        if textElement.name == "Disclaimer1":
            textElement.text = str(lastYear) + "."

    arcpy.RefreshActiveView()
    arcpy.mapping.ExportToPDF(map, LegendFolder + os.sep + "Legend_" + str(dataYear) + ".pdf")
    del map
    del dataFrame
    arcpy.AddMessage("Legend Complete.")


#
#3
#GRID INDEX
#
#
def createGridIndex():
    arcpy.AddMessage("Updating the Grid Indexes...")
    #make directory
    os.makedirs(outputDir + os.sep + "GridIndexes")

    map = arcpy.mapping.MapDocument(resourcesFolder + "\\Resources\\MXD\\GridIndexUpdate.mxd")
    dataFrame = arcpy.mapping.ListDataFrames(map)[0]
    for lyr in arcpy.mapping.ListLayers(map):
        if lyr.name == "TPP_GIS.MCHAMB1.County_Grids_22K":
            lyr.replaceDataSource(dataGDB, "FILEGDB_WORKSPACE", "County_Grids_22K")
        if lyr.name == "TPP_GIS.MCHAMB1.County":
            lyr.replaceDataSource(dataGDB, "FILEGDB_WORKSPACE", "Counties")
        if lyr.name == "TXDOT_Roadways":
            lyr.replaceDataSource(dataGDB, "FILEGDB_WORKSPACE", "TXDOT_Roadways")
        if lyr.name == "City":
            lyr.replaceDataSource(dataGDB, "FILEGDB_WORKSPACE", "Cities")
    arcpy.RefreshActiveView()

    for i in lowerNames:
        county = i
        for lyr in arcpy.mapping.ListLayers(map):
            if lyr.name == "TPP_GIS.MCHAMB1.County_Grids_22K":
                lyr.definitionQuery = "CNTY_NM = '" + county + "'"
                arcpy.RefreshActiveView()
                extent = lyr.getSelectedExtent()
            for textElement in arcpy.mapping.ListLayoutElements(map, "TEXT_ELEMENT"):
                if textElement.name == "topYEAR":
                    textElement.text = dataYear
                if textElement.name == "nayme":
                    textElement.text = county + " County - Mapbook Index"
                if textElement.name == "bottomDate":
                    textElement.text = now.strftime("%B") + " " + now.strftime("%d") + ", " + dataYear
                if textElement.name == "copyright":
                    textElement.text = "Copyright " + dataYear
                if textElement.name == "finalDate":
                    lastYear = int(dataYear) - 1
                    textElement.text = str(lastYear) + "."

        dataFrame.extent = extent
        dataFrame.scale *= 1.05
        arcpy.RefreshActiveView()
        arcpy.mapping.ExportToPDF(map, IndexFolder + os.sep + county + " County Mapbook Index.pdf")
        arcpy.AddMessage(county + " County Mapbook Index.pdf")
    del map
    del dataFrame
    arcpy.AddMessage("Map Indexes Complete.")


#
#4
#FORMAT DATA
#prep data for county shapefile and road log creation
#

def formatData():
    arcpy.AddMessage("Formating Data...")
    #
    arcpy.AddMessage("Database connection established. Routing roadways event layer.")


    #route subfile events onto txdot roadways and create a shapefile for creating a shapefile for each county
    tempRTEevents = "tempRTEevents"
    arcpy.MakeRouteEventLayer_lr(pubRDS, "RTE_ID", subfiles, "RTE_ID LINE BMP EMP", tempRTEevents)
    eventlayer = mapping.Layer(tempRTEevents)
    eventlayer.definitionQuery = """ "SUBFILE" = 2 AND "HIGHWAY_STATUS" = 4 AND "ADMIN_SYSTEM" = 3 AND "CONTROLSEC" NOT LIKE 'TOL%' AND "CONTROLSEC" NOT LIKE 'C%' AND "CONTROLSEC" NOT LIKE 'M%' """
    arcpy.AddMessage("Event layer created.")
    arcpy.FeatureClassToFeatureClass_conversion(eventlayer, workspace, "Roadway_Events")
    inventory = workspace + os.sep + "Roadway_Events"
    arcpy.AddMessage("Event layer saved to the workspace database.")


    #pull the full street names from txdot roadways
    arcpy.AddMessage("Starting street name update")
    #define a dictionary to use to compile the roadway names
    dictNM = {}
    #use the search cursor to collect the names and put them in the dictionary
    cursor = arcpy.SearchCursor(txdotRoadways, """RTE_CLASS = '2'""")
    for row in cursor:
        ID = row.getValue("RTE_ID")
        name = row.getValue("FULL_ST_NM")
        if ID not in dictNM.keys():
            dictNM[str(ID)] = str(name)
    del cursor
    arcpy.AddMessage("Names collected from TxDOT_Roadways")

    #create a field in the inventory roads and apply the collected names from the dictionary
    arcpy.AddField_management(inventory, "ST_NAME", "TEXT", "", "", 50)
    arcpy.AddMessage("Field created")
    cursor = arcpy.UpdateCursor(inventory)
    for row in cursor:
        ID = row.getValue("RTE_ID")
        CS = str(row.getValue("CONTROLSEC")).split("A")[-1]
        if str(ID) in dictNM.keys():
            if str(dictNM[ID]) == None or str(dictNM[ID]) == " ":
                row.setValue("ST_NAME", "County Road " + CS)
                cursor.updateRow(row)
            else:
                row.setValue("ST_NAME", str(dictNM[ID]))
                cursor.updateRow(row)
    del cursor
    arcpy.AddMessage("Street names applied.")


    #make a copy of the routed roadways in the statewide projection for the road log process later
    spatialRef = arcpy.Describe(CountyLayer).spatialReference
    arcpy.Project_management(inventory, projectedRoads, spatialRef)
    arcpy.AddMessage("Roadway events re-projected for the road log.")


    #the next 4 groups of code have been added in a recent version of this script after successful runs
    # revealed a need to dissolve rows in the shapefile for each county.
    #add a unique flag field and populate it based on the attributes its row
    arcpy.AddField_management(inventory, "unique", "TEXT", "", "", 250)
    cursor = arcpy.UpdateCursor(inventory)
    for row in cursor:
        county = row.getValue("COUNTY")
        CS = row.getValue("CONTROLSEC")
        design = row.getValue("HIGHWAY_DESIGN")
        surface = row.getValue("SURFACE_TYPE")
        lanes = row.getValue("NUMBER_OF_LANES")
        row.setValue("unique", str(county) + str(CS) + str(design) + str(surface) + str(lanes))
        cursor.updateRow(row)
    del cursor
    arcpy.AddMessage("Unique flag field created and populated.")

    #use the unique field to dissolve the roads. this removes multiple features within the final
    # county shapefiles that have all the same attributes. This problem exists because of subfiles records
    # with the same attributes amongst the fields used here but different attributes in fields not used
    #inventory2 = workspace + os.sep + "Roadway_Events_Dissolved"
    arcpy.Dissolve_management(inventory, inventory2, ["unique"], [["LEN_OF_SECTION","SUM"],["ST_NAME","FIRST"],["CONTROLSEC","FIRST"],["HIGHWAY_DESIGN","FIRST"],["SURFACE_TYPE","FIRST"],["COUNTY", "FIRST"],["NUMBER_OF_LANES","FIRST"]], "SINGLE_PART")
    arcpy.AddMessage("The routed events have been 'uniquely' dissolved.")

    #add new fields to ensure the shapefiles have proper field names since esri won't let you just change a field name
    arcpy.AddField_management(inventory2, "ROUTE", "TEXT", "", "", 10)
    arcpy.AddField_management(inventory2, "ST_NAME", "TEXT", "", "", 50)
    arcpy.AddField_management(inventory2, "LENGTH", "DOUBLE")
    arcpy.AddField_management(inventory2, "SURFACE", "LONG")
    arcpy.AddField_management(inventory2, "DESIGN", "LONG")
    arcpy.AddField_management(inventory2, "LANES", "LONG")
    arcpy.AddField_management(inventory2, "COMMENTS", "TEXT", "", "", 100)
    arcpy.AddField_management(inventory2, "COUNTY", "LONG")
    arcpy.AddMessage("Replacement fields have been created.")

    #populate the new fields with the data from the dissolved fields with the ugly names
    cursor = arcpy.UpdateCursor(inventory2)
    for row in cursor:
        CS = row.getValue("FIRST_CONTROLSEC")
        sumlen = row.getValue("SUM_LEN_OF_SECTION")
        surface = row.getValue("FIRST_SURFACE_TYPE")
        design = row.getValue("FIRST_HIGHWAY_DESIGN")
        lanes = row.getValue("FIRST_NUMBER_OF_LANES")
        name = row.getValue("FIRST_ST_NAME")
        county = row.getValue("FIRST_COUNTY")
        row.setValue("ROUTE", CS)
        row.setValue("LENGTH", sumlen)
        row.setValue("SURFACE", surface)
        row.setValue("DESIGN", design)
        row.setValue("LANES", lanes)
        row.setValue("ST_NAME", name)
        row.setValue("COUNTY", county)
        cursor.updateRow(row)
    del cursor
    arcpy.AddMessage("New Fields have been populated.")


    #continue with the formatting data process. remove unwanted fields.
    deleteFields = ["unique", "SUM_LEN_OF_SECTION", "FIRST_ST_NAME", "FIRST_CONTROLSEC", "FIRST_HIGHWAY_DESIGN", "FIRST_SURFACE_TYPE", "FIRST_COUNTY", "FIRST_NUMBER_OF_LANES"]
    arcpy.DeleteField_management(inventory2, deleteFields)
    arcpy.AddMessage("Fields reconfigured to match data dictionary.")


    arcpy.AddMessage("Data Formatted.")





#
#5
#SHAPEFILES
#
#

#this function was copied from previous the years' map book script. 
def createShapefiles():
    arcpy.AddMessage("Creating Shapefiles...")
    #make directory
    os.makedirs(outputDir + os.sep + "Shapefiles")
    #reference the dissolved roadway events feature class from the workspace
    #inventory2 = workspace + os.sep + "Roadway_Events_Dissolved"


    #iterate through the county names list and create a shapefile for each one
    countRange = range(0,len(upperNames))
    arcpy.AddMessage("Found %s counties..." % len(upperNames))
    for i in countRange:
        COUNTY_NAME = upperNames[i]
        shapeFileName = COUNTY_NAME + "_INVENTORY_" + dataYear +".shp"
        shapeFilePath = ShapefileFolder + os.sep + shapeFileName
        shapeFileDefQ = "\"COUNTY\" = "+ str(countyNumbers[i])
        arcpy.Select_analysis(inventory2, shapeFilePath, shapeFileDefQ)
        arcpy.AddMessage("%s definition query: %s" % (shapeFileName, shapeFileDefQ))
        arcpy.AddMessage("%s of %s Exporting County %s" % (i+1 , len(countRange),shapeFileName))

    arcpy.AddMessage("Shapefiles Complete.")








#
#6
#MAP PAGES
#
#

def createMapPages():
    arcpy.AddMessage("Generating Map Pages...")
    #make directory
    os.makedirs(outputDir + os.sep + "MapPages")


    map = arcpy.mapping.MapDocument(resourcesFolder + "\\Resources\\MXD\\CountyRoadInventoryMaps.mxd")
    dataFrame = arcpy.mapping.ListDataFrames(map)[0]
    for lyr in arcpy.mapping.ListLayers(map):
        if lyr.name == "Centerline":
            lyr.replaceDataSource(dataGDB, "FILEGDB_WORKSPACE", "TXDOT_Roadways")
        if lyr.name == "CountyRoadsRouted":
            lyr.replaceDataSource(workspace, "FILEGDB_WORKSPACE", "Roadway_Events")
            lyr.visible = True
            arcpy.AddMessage("Routed Roadways layer replaced.")
        if lyr.name == "Streets":
            lyr.replaceDataSource(dataGDB, "FILEGDB_WORKSPACE", "Streets")
        if lyr.name == "TPP_GIS.MCHAMB1.County":
            lyr.replaceDataSource(dataGDB, "FILEGDB_WORKSPACE", "Counties")
        if lyr.name == "TPP_GIS.MCHAMB1.City_Points":
            lyr.replaceDataSource(dataGDB, "FILEGDB_WORKSPACE", "City_Points")
        if lyr.name == "Dam":
            lyr.replaceDataSource(dataGDB, "FILEGDB_WORKSPACE", "Dam")
        if lyr.name == "TPP_GIS.MCHAMB1.Water_Bodies":
            lyr.replaceDataSource(dataGDB, "FILEGDB_WORKSPACE", "Water_Bodies")
        if lyr.name == "TPP_GIS.MCHAMB1.Streams":
            lyr.replaceDataSource(dataGDB, "FILEGDB_WORKSPACE", "Streams")
        if lyr.name == "TPP_GIS.MCHAMB1.Public_Lands":
            lyr.replaceDataSource(dataGDB, "FILEGDB_WORKSPACE", "Public_Lands")

    for textElement in arcpy.mapping.ListLayoutElements(map, "TEXT_ELEMENT"):
        if textElement.name == "Year":
            textElement.text = dataYear
    arcpy.RefreshActiveView()



    cursor = arcpy.SearchCursor(GridLayer, "CYCLE = '" + cycle + "' ", "", "CNTY_NM; MAP_ID; WEST; NORTH; EAST; SOUTH; SHAPE", "CNTY_NM A")
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
        arcpy.mapping.ExportToPDF(map, MapPagesFolder + os.sep + row.CNTY_NM + " " + MapID + ".pdf")
        arcpy.AddMessage(MapPagesFolder + os.sep + row.CNTY_NM + " " + MapID + ".pdf")
    del cursor
    del map
    del dataFrame
    arcpy.AddMessage("Map Pages Complete.")






#
#7
#COMBINE MAPBOOKS
#
#

def combineMapbooks():
    arcpy.AddMessage("Compiling Mapbooks for each county...")
    #make directory
    os.makedirs(outputDir + os.sep + "Combined_PDF")

    #compile a dictionary of the number of pages for each county
    pageDICT = {}
    cursor = arcpy.SearchCursor(CountyLayer)
    for row in cursor:
        currentCNTY = row.getValue("CNTY_U")
        numPages = row.getValue("Max_Pages")
        pageDICT[str(currentCNTY)] = str(numPages)
    del cursor
    arcpy.AddMessage("Number-of-pages dictionary compiled.")

    #iterate through the counties within the dictionary and compile all the page
    # numbers up until its maximum number of pages from the dictionary value
    for eachCO in pageDICT.keys():
        #announce the current county being compiled and the number of pages being compiled for that county
        arcpy.AddMessage(str(eachCO) + " has " + str(pageDICT[eachCO]) + " pages.")
        theGoal = pageDICT[eachCO]

        #use the PyPDF2 module to merge the PDFs
        merger = PdfFileMerger()
        theCover = CoversFolder + os.sep + str(eachCO) + ".pdf"
        theIndex = IndexFolder + os.sep + str(eachCO) + " County Mapbook Index.pdf"
        theLegend = LegendFolder + os.sep + "Legend_" + dataYear + ".pdf"
        merger.append(PdfFileReader(file(theCover, 'rb')))
        merger.append(PdfFileReader(file(theIndex, 'rb')))
        merger.append(PdfFileReader(file(theLegend, 'rb')))
        x = 1
        while x <= int(theGoal):
            currentpage = x
            pagevalue = str(currentpage)
            thePage = MapPagesFolder + os.sep + str(eachCO) + " " + pagevalue + ".pdf"
            merger.append(PdfFileReader(file(thePage, 'rb')))
            arcpy.AddMessage(str(eachCO) + " page " + pagevalue + " of " + str(theGoal))
            x += 1
        theOutput = open(MapBooksFolder + os.sep + str(eachCO)  + "_MAPBOOK_" + dataYear + ".pdf", "wb")
        merger.write(theOutput)
        theOutput.close()
        arcpy.AddMessage(str(eachCO) + " complete.")

    arcpy.AddMessage("Mapbooks Compiled.")







#
#8
#Road Logs/Report data prep
#
#
#

#C:\TxDOT\Scripts\CountyRoadInventoryMapBook\ROAD_LOG_INSTRUCTION\New folder\FINAL_How to create the County Road Update Summary_1.doc
#replicated the process described in the process above.
#
#Report prep: here we go...
#

def formatRoadLog():
    arcpy.AddMessage("Generating Road Log...")
    #make directory
    os.makedirs(outputDir + os.sep + "RoadLog")
    #projectedRoads = workspace + os.sep + "Roadway_Events_Projected"

    #intersect the county boundaries, county grids, and routed roads
    logRoads = workspace + os.sep + "RoadLog_Intersect"
    arcpy.Intersect_analysis([projectedRoads,CountyLayer,GridLayer], logRoads)
    arcpy.AddMessage("Intersect Complete.")

    #clean up the intersect of grids which overlap neighbor counties.
    # recalculate the new segment lengths since the intersect broken the linework at the county and grid boundaries.
    cursor = arcpy.UpdateCursor(logRoads)
    desc = arcpy.Describe(logRoads)
    shapefieldname = desc.ShapeFieldName
    for row in cursor:
        #recalculate the length for the cut up linework
        feat = row.getValue(shapefieldname)
        row.setValue("LEN_OF_SECTION", feat.length*.000621371)
        cursor.updateRow(row)
        #remove overlapping neighbor grids
        #get the linework county number:
        frst = row.getValue("COUNTY")
        #get the county boundary county number:
        scnd = row.getValue("CNTY_NBR")
        #get the grid layer county value:
        thrd = row.getValue("CNTY_NM_12")
        #get the county boundary county name:
        frth = row.getValue("CNTY_NM")
        #deletes the row if the linework county doesn't match the county boundary number
        if int(frst) != int(scnd):
            cursor.deleteRow(row)
        #deletes the row if the grid county is overlapping the county boundary
        if thrd != frth:
            cursor.deleteRow(row)
    del cursor
    arcpy.AddMessage("Intersected roadways have been cleaned up.")

    #
    #this section is the VB script replacement
    arcpy.AddMessage("Compiling page numbers")
    #sort table properly and collect the numbers via a cursor
    cursor = arcpy.SearchCursor(logRoads,"","","RTE_ID; MAP_ID","RTE_ID A; MAP_ID A")
    current = ""
    previous = ""
    counter = 0
    endAll = int(arcpy.GetCount_management(logRoads).getOutput(0))
    beAll = endAll - 1
    thesePages = []
    dictionary = {}
    #use the searchCursor to compile all the page numbers for each route ID into a list, and then
    # use that list as the value with the route ID as the key in the dictionary
    for row in cursor:
        current = row.getValue("RTE_ID")
        if counter == 0:
            previous = current
            thesePages.append("," + str(row.getValue("MAP_ID")).replace('.0',""))
            counter += 1
        elif previous == current and counter != 0 and counter != beAll:
            if "," + str(row.getValue("MAP_ID")).replace('.0',"") not in thesePages:
                thesePages.append("," + str(row.getValue("MAP_ID")).replace('.0',""))
                counter += 1
            else:
                counter += 1
        elif previous == current and counter == beAll:
            if "," + str(row.getValue("MAP_ID")).replace('.0',"") not in thesePages:
                thesePages.append("," + str(row.getValue("MAP_ID")).replace('.0',""))
            thesePages[0] = str(thesePages[0]).replace(",", "")

            concatPGS = ''.join(thesePages)
            dictionary[str(previous)] = concatPGS
            counter += 1
        elif previous != current and counter == beAll:
            thesePages[0] = str(thesePages[0]).replace(",", "")

            concatPGS = ''.join(thesePages)
            dictionary[str(previous)] = concatPGS
            thesePages = []
            previous = current
            dictionary[str(previous)] = str(row.getValue("MAP_ID")).replace('.0',"")
            counter += 1
        else:
            thesePages[0] = str(thesePages[0]).replace(",", "")

            concatPGS = ''.join(thesePages)
            dictionary[str(previous)] = concatPGS
            thesePages = []
            previous = current
            thesePages.append("," + str(row.getValue("MAP_ID")).replace('.0',""))
            counter += 1
    del cursor
    arcpy.AddMessage("The page numbers have been compiled into the dictionary.")


    #summarize the attributes in to remove multiple subfiles with the same attributes of the fields used in the report
    arcpy.AddField_management(logRoads, "unique", "TEXT", "", "", 250)
    cursor = arcpy.UpdateCursor(logRoads)
    for row in cursor:
        NAM = row.getValue("CNTY_NM")
        CS = row.getValue("CONTROLSEC")
        HD = row.getValue("HIGHWAY_DESIGN")
        ST = row.getValue("SURFACE_TYPE")
        NL = row.getValue("NUMBER_OF_LANES")
        row.setValue("unique", str(NAM) + str(CS) + str(HD) + str(ST) + str(NL))
        cursor.updateRow(row)
    del cursor
    arcpy.AddMessage("Unique flag identifier has been created and populated.")

    #Dissolve the road log lines and apply the page numbers
    arcpy.Dissolve_management(logRoads, dissRoads, ["unique"], [["LEN_OF_SECTION","SUM"],["RTE_ID","FIRST"],["ST_NAME","FIRST"],["CNTY_NM","FIRST"],["CONTROLSEC","FIRST"],["HIGHWAY_DESIGN","FIRST"],["SURFACE_TYPE","FIRST"],["NUMBER_OF_LANES","FIRST"]])
    arcpy.AddMessage("Road Log Linework dissolved.")

    #add the page numbers to the summarized routes so that we have all the road log data ready for the report
    arcpy.AddField_management(dissRoads, "MAP_ID", "TEXT", "", "", 150)
    cursor = arcpy.UpdateCursor(dissRoads)
    for row in cursor:
        rteID = row.getValue("FIRST_RTE_ID")
        if rteID in dictionary.keys():
            row.setValue("MAP_ID", str(dictionary[rteID]))
        else:
            arcpy.AddError(str(rteID) + " has no page numbers in the dictionary!")
        cursor.updateRow(row)
    del cursor
    arcpy.AddMessage("Page numbers applied into the new MAP_ID field.")


    arcpy.AddMessage("Road Log Completed.")







#
#
#9
#Report generation
#
#
#


def createRoadLogReport():
    arcpy.AddMessage("Starting PDF generation...")
    #make directory
    os.makedirs(RoadLogFolder + os.sep + "PDF_alpha")


    #iterate through the list of county names to create a report for each county
    for Y in lowerNames:
        #import the dimensions for the report and create variable to determine the
        # maximum measurements for that page size
        from reportlab.lib.pagesizes import letter
        width, height = letter
        #create a variable for the 'flowable' data drawing area on the report. this variable draws
        # the location where the road summary data is inserted into the report template
        f = frames.Frame(.5*inch,inch, width-inch, 8.65*inch)
        #create the document
        doc = BaseDocTemplate(PDFLogFolder + os.sep + str(Y).upper() + "_ROAD_SUMMARY_" + str(dataYear) + ".pdf", pagesize=letter)
        #drawn the canvas/template of the report
        def thecanvas(c, doc):
            from reportlab.lib.pagesizes import letter
            width, height = letter
            #the template/canvas is object oriented. this is a list of all the objects, where they are
            # to be drawn, and all the defining information which draws them
            #the objects are listed from the top of the page down to the bottom
            c.setFont("Helvetica-Bold",18)
            c.drawCentredString(width/2,height - .5*inch, str(Y))
            c.setFont("Helvetica",14)
            c.drawCentredString(width/2,height - .75*inch, "COUNTY ROAD SUMMARY")
            c.setFont("Times-Roman",12)
            c.drawCentredString(width/2,height - .93*inch, "Texas Department of Transportation")
            c.setFont("Times-Roman",8)
            c.drawCentredString(width/2,height - 1.07*inch, "Transportation Planning and Programming Division")
            c.setFont("Times-Bold",9)
            c.drawString(.57*inch,9.7*inch, "ROUTE")
            c.drawString(1.55*inch,9.7*inch, "ROAD NAME")
            c.drawString(3.25*inch,9.7*inch, "LENGTH")
            c.drawString(3.95*inch,9.7*inch, "DESIGN")
            c.drawString(4.7*inch,9.7*inch, "SURFACE")
            c.drawString(5.48*inch,9.7*inch, "LANES")
            c.drawString(6.25*inch,9.7*inch, "PAGE(S)")
            c.line(.5*inch,9.65*inch,width-.5*inch,9.65*inch)
            #the frame which contains the table and data will be here
            c.line(.5*inch,inch,width-.5*inch,inch)
            c.setFont("Times-Bold",8)
            c.drawString(.5*inch,.88*inch, month + " " + str(dataYear))
            c.drawString(2.5*inch,.85*inch, "Key:")
            c.drawString(3*inch,.85*inch, "Design:")
            c.drawString(3*inch,.7*inch, "1 = One Way")
            c.drawString(3*inch,.55*inch, "2 = Two Way")
            c.drawString(3*inch,.4*inch, "3 = Boulevard (Blvd)")
            c.drawString(4.5*inch,.85*inch, "Surface Type:")
            c.drawString(4.5*inch,.7*inch, "10 = Natural")
            c.drawString(4.5*inch,.55*inch, "32 = All Weather")
            c.drawString(5.8*inch,.7*inch, "51 = Paved")
            c.drawString(5.8*inch,.55*inch, "61 = Concrete")
            pageNUM = c.getPageNumber()
            c.drawRightString(width-.5*inch,.88*inch, "Page " + str(pageNUM))
        #apply the canvas/template and the frame for the flowable road data to the document
        doc.addPageTemplates([PageTemplate(frames=[f],onPage=thecanvas)])
        #search the formatted road log feature class via a cursor. query the feature class for the county being
        # reported, sort, create a list of the attributes from each row, and apply the list to a list of all the data rows
        cursor = arcpy.SearchCursor(dissRoads, "FIRST_CNTY_NM = '" + Y + "'", "", "", "FIRST_ST_NAME A; SUM_LEN_OF_SECTION D; FIRST_HIGHWAY_DESIGN D; FIRST_SURFACE_TYPE D; FIRST_NUMBER_OF_LANES D; FIRST_CONTROLSEC A")
        finalCount = -1
        for row in cursor:
            finalCount += 1
        del cursor
        cursor = arcpy.SearchCursor(dissRoads, "FIRST_CNTY_NM = '" + Y + "'", "", "", "FIRST_ST_NAME A; SUM_LEN_OF_SECTION D; FIRST_HIGHWAY_DESIGN D; FIRST_SURFACE_TYPE D; FIRST_NUMBER_OF_LANES D; FIRST_CONTROLSEC A")
        elements = []
        data = []
        counter = 1
        pageSum = 0
        countySum = 0
        totalCount = 0
        for row in cursor:
            if counter < 42 and totalCount != finalCount:
                CS = str(row.getValue("FIRST_CONTROLSEC"))
                SN = str(row.getValue("FIRST_ST_NAME"))
                rounded = round(row.getValue("SUM_LEN_OF_SECTION"), 3)
                LN = str(rounded)
                pageSum += rounded
                countySum += rounded
                HD = str(row.getValue("FIRST_HIGHWAY_DESIGN"))
                ST = str(row.getValue("FIRST_SURFACE_TYPE"))
                LA = str(row.getValue("FIRST_NUMBER_OF_LANES"))
                PG = str(row.getValue("MAP_ID"))
                eachLine = [CS, SN, LN, HD, ST, LA, PG]
                data.append(eachLine)
                counter += 1
                totalCount += 1
            elif counter == 42 and totalCount != finalCount:
                eachLine = ["", "     PAGE TOTAL MILES:", str(pageSum), "", "", "", ""]
                data.append(eachLine)
                counter = 1
                pageSum = 0
                CS = str(row.getValue("FIRST_CONTROLSEC"))
                SN = str(row.getValue("FIRST_ST_NAME"))
                rounded = round(row.getValue("SUM_LEN_OF_SECTION"), 3)
                LN = str(rounded)
                pageSum += rounded
                countySum += rounded
                HD = str(row.getValue("FIRST_HIGHWAY_DESIGN"))
                ST = str(row.getValue("FIRST_SURFACE_TYPE"))
                LA = str(row.getValue("FIRST_NUMBER_OF_LANES"))
                PG = str(row.getValue("MAP_ID"))
                eachLine = [CS, SN, LN, HD, ST, LA, PG]
                data.append(eachLine)
                counter += 1
                totalCount += 1
            elif totalCount == finalCount:
                CS = str(row.getValue("FIRST_CONTROLSEC"))
                SN = str(row.getValue("FIRST_ST_NAME"))
                rounded = round(row.getValue("SUM_LEN_OF_SECTION"), 3)
                LN = str(rounded)
                pageSum += rounded
                countySum += rounded
                HD = str(row.getValue("FIRST_HIGHWAY_DESIGN"))
                ST = str(row.getValue("FIRST_SURFACE_TYPE"))
                LA = str(row.getValue("FIRST_NUMBER_OF_LANES"))
                PG = str(row.getValue("MAP_ID"))
                eachLine = [CS, SN, LN, HD, ST, LA, PG]
                data.append(eachLine)
                eachLine = ["", "       PAGE TOTAL MILES:", str(pageSum), "", "", "", ""]
                data.append(eachLine)
                eachLine = ["", "       COUNTY TOTAL MILES:", str(countySum), "", "", "", ""]
                data.append(eachLine)
                #add the county total to the countyTotal dictionary for an xls output at end
                countyTotals[str(Y)] = countySum
        #draw the table, apply the data list, and format/stylize it
        t = Table(data, colWidths=[inch,1.75*inch,.8*inch,.75*inch,.75*inch,.65*inch,1.8*inch],rowHeights=[.2*inch]*len(data))
        t.setStyle(TableStyle([('FONTSIZE',(0,0),(6,(len(data)-1)),8),('ALIGN',(0,0),(6,(len(data)-1)),'LEFT'),]))
        #add the data object (in this case: the populated table of roads) to a list of 'flowable' objects
        elements.append(t)
        #use the 'flowable' objects list and build the document
        doc.build(elements)
        del cursor
        arcpy.AddMessage(str(Y) + " completed.")


    arcpy.AddMessage("PDF generation complete.")






#
#10
#Put together all the documents
#ZIP it UP
#
#

def compilePackets():
    arcpy.AddMessage("Zipping up the packets for each county...")
    os.makedirs(outputDir + os.sep + "_Completed_Packets")
    os.makedirs(completedPackets + os.sep + "_Descriptive_PDFs")

    #copy the annually updated documents which accompany all packets
    shutil.copyfile(resourcesFolder + "\\Resources\\Documents\\COUNTY_ROAD_CRITERIA.pdf", descriptiveDirectory + os.sep + "COUNTY_ROAD_CRITERIA.pdf")
    shutil.copyfile(resourcesFolder + "\\Resources\\Documents\\INSTRUCTIONS.pdf", descriptiveDirectory + os.sep + "INSTRUCTIONS.pdf")
    shutil.copyfile(resourcesFolder + "\\Resources\\Documents\\README_1ST.pdf", descriptiveDirectory + os.sep + "README_1ST.pdf")
    arcpy.AddMessage("Annual descriptive documents copied.")


    #define file extensions list to collect the pieces of the shapefiles
    theFileExtension = [".dbf",".prj",".sbn",".sbx",".shp",".shx"]
    arcpy.AddMessage("County and extension lists compiled.")

    #iterate through the list of county names and compile the packet for each
    countRange = len(upperNames)
    arcpy.AddMessage("Found %s counties..." % countRange)
    i = 1
    for theCounty in upperNames:

        theOutputZip = completedPackets + os.sep + theCounty + "_" + dataYear + ".zip"
        zippedFile = zipfile.ZipFile(theOutputZip,"a", zipfile.ZIP_DEFLATED)

        arcpy.AddMessage("%s of %s - Zipping files for %s..." % (i,countRange,theCounty))

        # Add the County Road Criteria PDF to the Zip File...
        zippedFile.write(descriptiveDirectory + os.sep + "COUNTY_ROAD_CRITERIA.pdf", "COUNTY_ROAD_CRITERIA.pdf")

        # Add the Instructions PDF to the Zip File...
        zippedFile.write(descriptiveDirectory + os.sep + "INSTRUCTIONS.pdf", "INSTRUCTIONS.pdf")

        # Add the ReadME PDF to the Zip File...
        zippedFile.write(descriptiveDirectory + os.sep + "README_1ST.pdf", "README_1ST.pdf")

        # Add the Road Summary PDF to the Zip File...
        roadLogsFile = theCounty + "_ROAD_SUMMARY_" + dataYear + ".pdf"
        zippedFile.write(PDFLogFolder + os.sep + roadLogsFile,roadLogsFile)

        # Add the Mapbook Page to the Zip file
        countyMapbookFile = theCounty + "_MAPBOOK_" + dataYear + ".pdf"
        zippedFile.write(MapBooksFolder + os.sep + countyMapbookFile,countyMapbookFile)

        # Make a list of Geometry File Names...
        theGeometryFiles = []
        for extentionType in theFileExtension:
            theGeometryFiles.append(theCounty +"_INVENTORY_" + dataYear + extentionType)

        # Add the Geometry to the Zip file...
        for eachFile in theGeometryFiles:
            theTargetFile = ShapefileFolder + os.sep + eachFile
            zippedFile.write(theTargetFile,eachFile)
        arcpy.AddMessage("%s complete." % theCounty)

        # Close the Zip file...
        zippedFile.close()
        i += 1

    arcpy.AddMessage("County packets zipped up and completed.")

#
#
#
#
#
#
def xlsTotals():
    arcpy.AddMessage("Compiling mileage total xls for internal use...")
    data = tablib.Dataset(headers=["NAME", "MILES", "ROUNDED"])
    for i in countyTotals.keys():
        name = i
        miles = countyTotals[i]
        rounded = round(float(miles), 0)
        row = (name, miles, rounded)
        data.append(row)
        arcpy.AddMessage(str(i) + " County: " + str(miles) + " miles rounded to: " + str(rounded))
    newfile = open(outputDir + os.sep + "TotalMileages.xls", "wb").write(data.xls)
    arcpy.AddMessage("Mileage total xls compiled.")


#
#
#
#
#
#

arcpy.AddMessage("And away we go...")

#copyDataLocal()
#createCovers()
#createLegend()
#createGridIndex()
#formatData()
#createShapefiles()
#createMapPages()
#combineMapbooks()
#formatRoadLog()
createRoadLogReport()
#compilePackets()
#xlsTotals()


arcpy.AddMessage("Phew...finally finished.")
now2 = datetime.datetime.now()
arcpy.AddMessage("Started at: " + str(now))
arcpy.AddMessage("Ended at: " + str(now2))