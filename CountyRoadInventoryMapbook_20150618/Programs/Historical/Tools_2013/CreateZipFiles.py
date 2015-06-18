import zipfile, arcpy

# Report Year
theYear = arcpy.GetParameterAsText(0)

# File Directories
baseDirectory 	= arcpy.GetParameterAsText(1) ## This must be the base directory for CRI up to the current cycle year
outputPath 				= baseDirectory + "_Completed Packets\\"
thePDFsDirectory 		= baseDirectory + "_Completed Packets\\_PDF\\"
theRoadLogsDirectory 	= baseDirectory + "Road Logs\\PDF\\"
theMapBookDirectory 	= baseDirectory + "Combined PDF\\PDF\\"
theShapefileDirectory 	= baseDirectory + "Inventory Shapefiles\\"

countyShapeFile = arcpy.GetParameterAsText(2) ##Shapefile for correct Cycle in (T:\DATAMGT\MAPPING\Mapping Products\County Road Update Mapbooks\Common Mapping Items\South and North County Shapefiles)

theFileExtension = [".dbf",".prj",".sbn",".sbx",".shp",".shx"]

print "Looking for row: CNTY_NM in %s..." % countyShapeFile
countyNames = []
cursor = arcpy.SearchCursor(countyShapeFile)
for row in cursor:
    countyNames.append(str(row.CNTY_NM).upper())
    print "Found - %s" % (row.CNTY_NM)

countRange = len(countyNames)
print "Found %s counties..." % countRange
print "Now creating %s zipFiles..." % countRange

i = 1
for theCounty in countyNames:
    
    theOutputZip = outputPath + theCounty + "_" + theYear + ".zip"
    zippedFile = zipfile.ZipFile(theOutputZip,"a", zipfile.ZIP_DEFLATED)

    print "%s of %s - Zipping files for %s..." % (i,countRange,theCounty)

    # Add the County Road Criteria PDF to the Zip File...
    zippedFile.write(thePDFsDirectory + "COUNTY_ROAD_CRITERIA.pdf","COUNTY_ROAD_CRITERIA.pdf")
    
    # Add the Instructions PDF to the Zip File...
    zippedFile.write(thePDFsDirectory + "INSTRUCTIONS.pdf","INSTRUCTIONS.pdf")

    # Add the ReadME PDF to the Zip File...
    zippedFile.write(thePDFsDirectory + "README_1ST.pdf","README_1ST.pdf")

    # Add the Road Summary PDF to the Zip File...
    roadLogsFile = theCounty + "_ROAD_SUMMARY_" + theYear + ".pdf"
    zippedFile.write(theRoadLogsDirectory + roadLogsFile,roadLogsFile)
    
    # Add the Mapbook Page to the Zip file
    countyMapbookFile = theCounty + "_MAPBOOK_" + theYear + ".pdf"
    zippedFile.write(theMapBookDirectory + countyMapbookFile,countyMapbookFile)

    # Make a list of Geometry File Names...
    theGeometryFiles = []
    for extentionType in theFileExtension:
        theGeometryFiles.append(theCounty +"_INVENTORY_" + theYear + extentionType)

    # Add the Geometry to the Zip file...
    for eachFile in theGeometryFiles:
        theTargetFile = theShapefileDirectory + eachFile
        zippedFile.write(theTargetFile,eachFile)
    print "%s complete..." % theOutputZip

    # Close the Zip file...
    zippedFile.close()
    i += 1
    
print "Files Zipped to %s" % outputPath
