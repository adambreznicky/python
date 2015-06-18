import sys, string, os, arcgisscripting, datetime
gp = arcgisscripting.create()
ws = "C:\\TxDOT\\Scripts\\zugelder\\PostCollectionQAQC"

print "Begin: " + str(datetime.datetime.now().time())
def appendData(theFC):
    global ws
    global gp
    
    TPP_GIS_MCHAMB1_Centerline = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.MCHAMB1.Regional_Data_Collection\\TPP_GIS.MCHAMB1.Centerline"
    TPP_GIS_MCHAMB1_Intersections = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.MCHAMB1.Regional_Data_Collection\\TPP_GIS.MCHAMB1.Intersections"
    TPP_GIS_MCHAMB1_Line_Elements = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.MCHAMB1.Regional_Data_Collection\\TPP_GIS.MCHAMB1.Line_Elements"
    TPP_GIS_MCHAMB1_Markers = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.MCHAMB1.Regional_Data_Collection\\TPP_GIS.MCHAMB1.Markers"
    TPP_GIS_MCHAMB1_Monuments = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.MCHAMB1.Regional_Data_Collection\\TPP_GIS.MCHAMB1.Monuments"
    TPP_GIS_MCHAMB1_Point_Elements = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.MCHAMB1.Regional_Data_Collection\\TPP_GIS.MCHAMB1.Point_Elements"
    TPP_GIS_MCHAMB1_Termini = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.MCHAMB1.Regional_Data_Collection\\TPP_GIS.MCHAMB1.Termini"

    #TPP_GIS_MCHAMB1_Centerline = "E:\\DataCollection\\_GRG\RDC.gdb\\Centerline"
    #TPP_GIS_MCHAMB1_Intersections = "E:\\DataCollection\\_GRG\RDC.gdb\\Intersections"
    #TPP_GIS_MCHAMB1_Line_Elements = "E:\\DataCollection\\_GRG\RDC.gdb\\Line_Elements"
    #TPP_GIS_MCHAMB1_Markers = "E:\\DataCollection\\_GRG\RDC.gdb\\Markers"
    #TPP_GIS_MCHAMB1_Monuments = "E:\\DataCollection\\_GRG\RDC.gdb\\Monuments"
    #TPP_GIS_MCHAMB1_Point_Elements = "E:\\DataCollection\\_GRG\RDC.gdb\\Point_Elements"
    #TPP_GIS_MCHAMB1_Termini = "E:\\DataCollection\\_GRG\RDC.gdb\\Termini"    

    rows = gp.SearchCursor(ws + "\\" + theFC)
    row = rows.Next()

    appendPath=""
    dataType=""
    while row:
        dataType=row.DATA_TYPE
        row=rows.Next()
        
    if 'row' in dir():
        del row
    if 'rows' in dir():
        del rows        

    if dataType=="Centerline":
        appendPath = TPP_GIS_MCHAMB1_Centerline

    if dataType=="County Monuments":
        appendPath = TPP_GIS_MCHAMB1_Monuments

    if dataType=="Intersections":
        appendPath = TPP_GIS_MCHAMB1_Intersections

    if dataType=="Line Elements":
        appendPath = TPP_GIS_MCHAMB1_Line_Elements

    if dataType=="Markers":
        appendPath = TPP_GIS_MCHAMB1_Markers

    if dataType=="Point Elements":
        appendPath = TPP_GIS_MCHAMB1_Point_Elements

    if dataType=="Termini Points":
        appendPath = TPP_GIS_MCHAMB1_Termini

    gp.Append_management(ws + "\\" + theFC, appendPath, "TEST", "", "")


def listSHPs():
    global ws
    counter=0
    for file in os.listdir(ws):    
        if file.endswith(".shp"):
            print "Appending " + file
            counter+=1
            appendData(file)

    if counter < 1:
        print "No .shp files were found in " + ws + "."
        raw_input("Press enter to continue...")

def checkDirectories():
    global ws
    checkCDrive = "False"
    checkDDrive = "False"
    checkEDrive = "False"
    
    if os.path.exists("C:\\TxDOT\\Scripts\\zugelder\\PostCollectionQAQC"):
        checkCDrive = "True"
        ws = "C:\\TxDOT\\Scripts\\zugelder\\PostCollectionQAQC"
    if os.path.exists("C:\\TxDOT\\Scripts\\zugelder\\PostCollectionQAQC"):
        checkDDrive = "True"
        ws = "C:\\TxDOT\\Scripts\\zugelder\\PostCollectionQAQC"
    if os.path.exists("C:\\TxDOT\\Scripts\\zugelder\\PostCollectionQAQC"):
        checkEDrive = "True"
        ws = "C:\\TxDOT\\Scripts\\zugelder\\PostCollectionQAQC"

    if checkCDrive == "False" and checkDDrive == "False" and checkEDrive == "False":
        print "Data Collection Directory not found.  See section 2.2.1 of Data Collection SOP."
        raw_input("Press enter to continue...")        
    else:
        for dirPath, dirNames, fileNames in os.walk(ws):
            for file in fileNames:
                if file.endswith(".shp"):
                    ws=dirPath
                    print "Appending " + file
                    #counter+=1
                    appendData(file)
                    #listSHPs()

checkDirectories();
print "End: " + str(datetime.datetime.now().time())
