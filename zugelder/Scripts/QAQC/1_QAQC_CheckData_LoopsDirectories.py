#QAQC Script written by TPP-Mapping for the Regional Data Collection SOP on July 19, 2011
#Contact: Michael Chamberlain 512.486.5086, Michael.Chamberlain@TxDOT.gov
#Version 1.4 Last edited by James Graham, TPP September 16, 2011
#Version 1.5 Last edited by Michael Chamberlain July 13, 2012.  Added ability to loop through folders.

import arcgisscripting
import os
import datetime
import sys
import traceback

try:

    print "Begin: " + str(datetime.datetime.now().time())

    gp = arcgisscripting.create(9.3)
    #gp.AddToolbox("D:/Program Files/ArcGIS/ArcToolbox/Toolboxes/Data Management Tools.tbx")
    ws = "C:\\DataCollection\\PostCollectionQAQC"
    epth = "C:\\DataCollection\\PostCollectionQAQC"    
    currentDay = datetime.datetime.now().day
    currentMonth = datetime.datetime.now().month
    currentYear = datetime.datetime.now().year
    fileName = str(currentMonth) + "-" + str(currentDay) + "-" + str(currentYear)
    errorLogCounter = 0
    
    def compareLists(theList,theValue):
        RTE_CLASS_LIST = ["On System","County Road","FC Street","Local Street","Toll Road"]
        RTE_TYPE_LIST = ["AG","BG","KG","LG","MG","PG","RG","SG","TG","XG","YG"]
        RTE_PRFX_LIST = ["AA","BF","BI","BS","BU","FC","FM","FS","IH","LS","PA","PR","RE","RM","RR","RS","SH","SL","SS","UA","UP","US"]
        DATA_TYPE_LIST = ["Centerline","County Monuments","Intersections","Line Elements","Markers","Point Elements","Termini Points"]

        if theList=="RTE_CLASS_LIST":
            if theValue in RTE_CLASS_LIST:
                return 1

        if theList=="RTE_TYPE_LIST":
            if theValue in RTE_TYPE_LIST:
                return 1

        if theList=="RTE_PRFX_LIST":
            if theValue in RTE_PRFX_LIST:
                return 1

        if theList=="DATA_TYPE_LIST":
            if theValue in DATA_TYPE_LIST:
                return 1

    def getFCData(theFC,theDataItem):
        if theDataItem == "Centerline":
            centerlinesDataChecks(theFC)

        if theDataItem == "County Monuments":
            monumentsDataChecks(theFC)

        if theDataItem == "Intersections":
            intersectionsDataChecks(theFC)

        if theDataItem == "Line Elements":
            lineElementsDataChecks(theFC)

        if theDataItem == "Markers":
            markersDataChecks(theFC)

        if theDataItem == "Point Elements":
            pointElementsDataChecks(theFC)

        if theDataItem == "Termini Points":
            terminiPointsDataChecks(theFC)

    def centerlinesDataChecks(theFC):
        global ws
        rows = gp.SearchCursor(ws + "\\" + theFC)
        row = rows.Next()
        while row:
            #RTE_CLASS domain check
            if compareLists("RTE_CLASS_LIST",row.RTE_CLASS):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS is not within the RTE_CLASS domain.",theFC)

            #RTE_TYPE domain check
            if compareLists("RTE_TYPE_LIST",row.RTE_TYPE):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_TYPE is not within the RTE_TYPE domain.",theFC)

            #RTE_PRFX domain check
            if compareLists("RTE_PRFX_LIST",row.RTE_PRFX):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_PRFX is not within the RTE_PRFX domain.",theFC)        
            
            #RTE_CLASS and RTE_PRFX Checks
            if row.RTE_CLASS == "County Road" and row.RTE_PRFX != "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_PRFX != "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of LS.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_PRFX != "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_PRFX of LS.",theFC)            

            #RTE_CLASS and RTE_TYPE Checks
            if row.RTE_CLASS == "County Road" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_TYPE of KG.",theFC)            

            #RTE_NBR Checks
            if len(row.RTE_NBR) < 4:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR must be at least 4 characters long.  Example 0001 or 0010 or 0100 or 1000.",theFC)

            #RTR_NBR Checks - Extended
            if row.RTE_NBR.isdigit():
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR contains non numeric characters.  Valid entries are 0001 or 0010 or 0100 or 1000.",theFC)

            #PNT_MTHD Checks
            if row.PNT_MTHD == "Direct" or row.PNT_MTHD == "Offset":
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", PNT_MTHD must be Direct or Offset.",theFC)

            #DMI_DSTNCE Checks
            if row.PNT_MTHD == "Offset":
                if row.DMI_DSTNCE > 0:
                    pass
                else:
                    writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", DMI_DSTNCE must be greater than 0 if PNT_MTHD is Offset.",theFC)            
            
            row=rows.Next()

        if 'row' in dir():
            del row
        if 'rows' in dir():
            del rows    

    def monumentsDataChecks(theFC):
        global ws
        rows = gp.SearchCursor(ws + "\\" + theFC)
        row = rows.Next()    
        while row:
            #RTE_CLASS domain check
            if compareLists("RTE_CLASS_LIST",row.RTE_CLASS):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS is not within the RTE_CLASS domain.",theFC)

            #RTE_TYPE domain check
            if compareLists("RTE_TYPE_LIST",row.RTE_TYPE):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_TYPE is not within the RTE_TYPE domain.",theFC)

            #RTE_PRFX domain check
            if compareLists("RTE_PRFX_LIST",row.RTE_PRFX):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_PRFX is not within the RTE_PRFX domain.",theFC)
            
            #RTE_CLASS and RTE_PRFX Checks
            if row.RTE_CLASS == "County Road" and row.RTE_PRFX != "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_PRFX != "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of LS.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_PRFX != "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_PRFX of LS.",theFC)            

            #RTE_CLASS and RTE_TYPE Checks
            if row.RTE_CLASS == "County Road" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_TYPE of KG.",theFC)            

            #RTE_NBR Checks
            if len(row.RTE_NBR) < 4:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR must be at least 4 characters long.  Example 0001 or 0010 or 0100 or 1000.",theFC)

            #RTR_NBR Checks - Extended
            if row.RTE_NBR.isdigit():
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR contains non numeric characters.  Valid entries are 0001 or 0010 or 0100 or 1000.",theFC)        

            #PNT_MTHD Checks
            if row.PNT_MTHD == "Direct" or row.PNT_MTHD == "Offset":
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", PNT_MTHD must be Direct or Offset.",theFC)

            #DMI_DSTNCE Checks
            if row.PNT_MTHD == "Offset":
                if row.DMI_DSTNCE > 0:
                    pass
                else:
                    writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", DMI_DSTNCE must be greater than 0 if PNT_MTHD is Offset.",theFC)
            
            row=rows.Next()

        if 'row' in dir():
            del row
        if 'rows' in dir():
            del rows    

    def intersectionsDataChecks(theFC):
        global ws
        rows = gp.SearchCursor(ws + "\\" + theFC)
        row = rows.Next()    
        while row:
            #RTE_CLASS domain check
            if compareLists("RTE_CLASS_LIST",row.RTE_CLASS):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS is not within the RTE_CLASS domain.",theFC)

            #RTE_TYPE domain check
            if compareLists("RTE_TYPE_LIST",row.RTE_TYPE):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_TYPE is not within the RTE_TYPE domain.",theFC)

            #RTE_PRFX domain check
            if compareLists("RTE_PRFX_LIST",row.RTE_PRFX):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_PRFX is not within the RTE_PRFX domain.",theFC)
            
            #RTE_CLASS and RTE_PRFX Checks
            if row.RTE_CLASS == "County Road" and row.RTE_PRFX != "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_PRFX != "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of LS.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_PRFX != "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_PRFX of LS.",theFC)            

            #RTE_CLASS and RTE_TYPE Checks
            if row.RTE_CLASS == "County Road" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_TYPE of KG.",theFC)            

            #RTE_NBR Checks
            if len(row.RTE_NBR) < 4:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR must be at least 4 characters long.  Example 0001 or 0010 or 0100 or 1000.",theFC)

            #RTR_NBR Checks - Extended
            if row.RTE_NBR.isdigit():
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR contains non numeric characters.  Valid entries are 0001 or 0010 or 0100 or 1000.",theFC)        

            #PNT_MTHD Checks
            if row.PNT_MTHD == "Direct" or row.PNT_MTHD == "Offset":
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", PNT_MTHD must be Direct or Offset.",theFC)

            #DMI_DSTNCE Checks
            if row.PNT_MTHD == "Offset":
                if row.DMI_DSTNCE > 0:
                    pass
                else:
                    writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", DMI_DSTNCE must be greater than 0 if PNT_MTHD is Offset.",theFC)
            
            row=rows.Next()

        if 'row' in dir():
            del row
        if 'rows' in dir():
            del rows    

    def lineElementsDataChecks(theFC):
        global ws
        rows = gp.SearchCursor(ws + "\\" + theFC)
        row = rows.Next()    
        while row:
            #RTE_CLASS domain check
            if compareLists("RTE_CLASS_LIST",row.RTE_CLASS):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS is not within the RTE_CLASS domain.",theFC)

            #RTE_TYPE domain check
            if compareLists("RTE_TYPE_LIST",row.RTE_TYPE):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_TYPE is not within the RTE_TYPE domain.",theFC)

            #RTE_PRFX domain check
            if compareLists("RTE_PRFX_LIST",row.RTE_PRFX):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_PRFX is not within the RTE_PRFX domain.",theFC)
            
            #RTE_CLASS and RTE_PRFX Checks
            if row.RTE_CLASS == "County Road" and row.RTE_PRFX != "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_PRFX != "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of LS.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_PRFX != "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_PRFX of LS.",theFC)            

            #RTE_CLASS and RTE_TYPE Checks
            if row.RTE_CLASS == "County Road" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_TYPE of KG.",theFC)            

            #RTE_NBR Checks
            if len(row.RTE_NBR) < 4:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR must be at least 4 characters long.  Example 0001 or 0010 or 0100 or 1000.",theFC)

            #RTR_NBR Checks - Extended
            if row.RTE_NBR.isdigit():
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR contains non numeric characters.  Valid entries are 0001 or 0010 or 0100 or 1000.",theFC)        

            #PNT_MTHD Checks
            if row.PNT_MTHD == "Direct" or row.PNT_MTHD == "Offset":
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", PNT_MTHD must be Direct or Offset.",theFC)

            #DMI_DSTNCE Checks
            if row.PNT_MTHD == "Offset":
                if row.DMI_DSTNCE > 0:
                    pass
                else:
                    writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", DMI_DSTNCE must be greater than 0 if PNT_MTHD is Offset.",theFC)

            row=rows.Next()

        if 'row' in dir():
            del row
        if 'rows' in dir():
            del rows    

    def markersDataChecks(theFC):
        global ws
        rows = gp.SearchCursor(ws + "\\" + theFC)
        row = rows.Next()    
        while row:
            #RTE_CLASS domain check
            if compareLists("RTE_CLASS_LIST",row.RTE_CLASS):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS is not within the RTE_CLASS domain.",theFC)

            #RTE_TYPE domain check
            if compareLists("RTE_TYPE_LIST",row.RTE_TYPE):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_TYPE is not within the RTE_TYPE domain.",theFC)

            #RTE_PRFX domain check
            if compareLists("RTE_PRFX_LIST",row.RTE_PRFX):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_PRFX is not within the RTE_PRFX domain.",theFC)
            
            #RTE_CLASS and RTE_PRFX Checks
            if row.RTE_CLASS == "County Road" and row.RTE_PRFX != "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_PRFX != "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of LS.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_PRFX != "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_PRFX of LS.",theFC)            

            #RTE_CLASS and RTE_TYPE Checks
            if row.RTE_CLASS == "County Road" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_TYPE of KG.",theFC)            

            #RTE_NBR Checks
            if len(row.RTE_NBR) < 4:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR must be at least 4 characters long.  Example 0001 or 0010 or 0100 or 1000.",theFC)

            #RTR_NBR Checks - Extended
            if row.RTE_NBR.isdigit():
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR contains non numeric characters.  Valid entries are 0001 or 0010 or 0100 or 1000.",theFC)        

            #MRKR_NBR Checks
            if len(row.MRKR_NBR) < 3:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", MRKR_NBR must be at least 3 characters long.  Example 001 or 010 or 100.",theFC)

            #MRKR_NBR Checks - Extended
            if row.MRKR_NBR[0:3].isdigit():
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", MRKR_NBR contains non numeric characters in the first three places.  Valid entries are 001 or 010 or 100.",theFC)        

            #PNT_MTHD Checks
            if row.PNT_MTHD == "Direct" or row.PNT_MTHD == "Offset":
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", PNT_MTHD must be Direct or Offset.",theFC)

            #DMI_DSTNCE Checks
            if row.PNT_MTHD == "Offset":
                if row.DMI_DSTNCE > 0:
                    pass
                else:
                    writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", DMI_DSTNCE must be greater than 0 if PNT_MTHD is Offset.",theFC)
            
            row=rows.Next()

        if 'row' in dir():
            del row
        if 'rows' in dir():
            del rows    

    def pointElementsDataChecks(theFC):
        global ws
        rows = gp.SearchCursor(ws + "\\" + theFC)
        row = rows.Next()    
        while row:
            #RTE_CLASS domain check
            if compareLists("RTE_CLASS_LIST",row.RTE_CLASS):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS is not within the RTE_CLASS domain.",theFC)

            #RTE_TYPE domain check
            if compareLists("RTE_TYPE_LIST",row.RTE_TYPE):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_TYPE is not within the RTE_TYPE domain.",theFC)

            #RTE_PRFX domain check
            if compareLists("RTE_PRFX_LIST",row.RTE_PRFX):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_PRFX is not within the RTE_PRFX domain.",theFC)
                
            #RTE_CLASS and RTE_PRFX Checks
            if row.RTE_CLASS == "County Road" and row.RTE_PRFX != "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_PRFX != "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of LS.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_PRFX != "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_PRFX of LS.",theFC)            

            #RTE_CLASS and RTE_TYPE Checks
            if row.RTE_CLASS == "County Road" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_TYPE of KG.",theFC)            

            #RTE_NBR Checks
            if len(row.RTE_NBR) < 4:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR must be at least 4 characters long.  Example 0001 or 0010 or 0100 or 1000.",theFC)

            #RTR_NBR Checks - Extended
            if row.RTE_NBR.isdigit():
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR contains non numeric characters.  Valid entries are 0001 or 0010 or 0100 or 1000.",theFC)        

            #PNT_MTHD Checks
            if row.PNT_MTHD == "Direct" or row.PNT_MTHD == "Offset":
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", PNT_MTHD must be Direct or Offset.",theFC)

            #DMI_DSTNCE Checks
            if row.PNT_MTHD == "Offset":
                if row.DMI_DSTNCE > 0:
                    pass
                else:
                    writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", DMI_DSTNCE must be greater than 0 if PNT_MTHD is Offset.",theFC)
            
            row=rows.Next()

        if 'row' in dir():
            del row
        if 'rows' in dir():
            del rows    

    def terminiPointsDataChecks(theFC):
        global ws
        rows = gp.SearchCursor(ws + "\\" + theFC)
        row = rows.Next()    
        while row:
            #RTE_CLASS domain check
            if compareLists("RTE_CLASS_LIST",row.RTE_CLASS):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS is not within the RTE_CLASS domain.",theFC)

            #RTE_TYPE domain check
            if compareLists("RTE_TYPE_LIST",row.RTE_TYPE):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_TYPE is not within the RTE_TYPE domain.",theFC)

            #RTE_PRFX domain check
            if compareLists("RTE_PRFX_LIST",row.RTE_PRFX):
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_PRFX is not within the RTE_PRFX domain.",theFC)
            
            #RTE_CLASS and RTE_PRFX Checks
            if row.RTE_CLASS == "County Road" and row.RTE_PRFX != "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_PRFX != "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "AA":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of AA.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "FC":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of FC.",theFC)
            if row.RTE_CLASS == "On System" and row.RTE_PRFX == "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of On System cannot have a RTE_PRFX of LS.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_PRFX != "LS":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_PRFX of LS.",theFC)            

            #RTE_CLASS and RTE_TYPE Checks
            if row.RTE_CLASS == "County Road" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of County Road must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "FC Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of FC Street must have a RTE_TYPE of KG.",theFC)
            if row.RTE_CLASS == "Local Street" and row.RTE_TYPE != "KG":
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_CLASS of Local Street must have a RTE_TYPE of KG.",theFC)            

            #RTE_NBR Checks
            if len(row.RTE_NBR) < 4:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR must be at least 4 characters long.  Example 0001 or 0010 or 0100 or 1000.",theFC)

            #RTR_NBR Checks - Extended
            if row.RTE_NBR.isdigit():
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", RTE_NBR contains non numeric characters.  Valid entries are 0001 or 0010 or 0100 or 1000.",theFC)        

            #PNT_TYPE Checks
            if row.PNT_TYPE == "Begin" or row.PNT_TYPE == "End":
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", PNT_TYPE must be Begin or End.",theFC)

            #PNT_MTHD Checks
            if row.PNT_MTHD == "Direct" or row.PNT_MTHD == "Offset":
                pass
            else:
                writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", PNT_MTHD must be Direct or Offset.",theFC)

            #DMI_DSTNCE Checks
            if row.PNT_MTHD == "Offset":
                if row.DMI_DSTNCE > 0:
                    pass
                else:
                    writeErrorLog("Data Check","Error! FID=" + str(row.FID) + ", DMI_DSTNCE must be greater than 0 if PNT_MTHD is Offset.",theFC)
            
            row=rows.Next()
            
        if 'row' in dir():
            del row
        if 'rows' in dir():
            del rows

    def getFCStructure(theFC,theDataItem):
        global ws
        fields = gp.ListFields(ws + "\\" + theFC)

        #Data Types: Centerline, County Monuments, Intersections, Line Elements, Markers, Point Elements, Termini Points
        centerlinesNameString = "RTE_CLASS,RTE_TYPE,RTE_PRFX,RTE_NBR,RTE_SFX,CROSS_SECT,PNT_MTHD,DMI_DSTNCE,CMNT,FROM_DT,DATA_TYPE"
        monumentsNameString = "RTE_CLASS,RTE_TYPE,RTE_PRFX,RTE_NBR,RTE_SFX,PNT_MTHD,PNT_TYPE,DMI_DSTNCE,CMNT,FROM_DT,DATA_TYPE"
        intersectionsNameString = "RTE_CLASS,RTE_TYPE,RTE_PRFX,RTE_NBR,RTE_SFX,GRADE_TYPE,INTSECT_1,INTSECT_2,INTSECT_3,INTSECT_4,PNT_MTHD,DMI_DSTNCE,CMNT,FROM_DT,DATA_TYPE"
        lineElementsNameString = "RTE_CLASS,RTE_TYPE,RTE_PRFX,RTE_NBR,RTE_SFX,ATTR_TYPE,END_ATTR_V,BEGIN_ATTR,PNT_MTHD,DMI_DSTNCE,CMNT,FROM_DT,DATA_TYPE,TIME_STAMP"
        markersNameString = "RTE_CLASS,RTE_TYPE,RTE_PRFX,RTE_NBR,RTE_SFX,MRKR_NBR,PNT_MTHD,DMI_DSTNCE,CMNT,FROM_DT,DATA_TYPE"
        pointElementsNameString = "RTE_CLASS,RTE_TYPE,RTE_PRFX,RTE_NBR,RTE_SFX,ATTR_TYPE,ATTR_VALUE,PNT_MTHD,DMI_DSTNCE,CMNT,FROM_DT,DATA_TYPE"
        terminiPointsNameString = "RTE_CLASS,RTE_TYPE,RTE_PRFX,RTE_NBR,RTE_SFX,PNT_TYPE,PNT_MTHD,DMI_DSTNCE,CMNT,FROM_DT,DATA_TYPE"

        fieldNameString=""    
        for field in fields:
            fieldNameString = fieldNameString + "," + field.name 
            #Add a check for field types - print field.type

        fieldNameString = fieldNameString[11:len(fieldNameString)]

        if theDataItem=="Markers":
            if fieldNameString != markersNameString:
                writeErrorLog("Fields Check","Error! Field names do not match the Data Collection SOP data model.  Check that you are using the most current version of TPP_Features.ddf.",theFC)
            else:
                writeErrorLog("Fields Check","No field errors found.",theFC)

        if theDataItem=="Centerline":
            if fieldNameString != centerlinesNameString:
                writeErrorLog("Fields Check","Error! Field names do not match the Data Collection SOP data model.  Check that you are using the most current version of TPP_Features.ddf.",theFC)
            else:
                writeErrorLog("Fields Check","No field errors found.",theFC)

        if theDataItem=="County Monuments":
            if fieldNameString != monumentsNameString:
                writeErrorLog("Fields Check","Error! Field names do not match the Data Collection SOP data model.  Check that you are using the most current version of TPP_Features.ddf.",theFC)
            else:
                writeErrorLog("Fields Check","No field errors in found.",theFC)

        if theDataItem=="Intersections":
            if fieldNameString != intersectionsNameString:
                writeErrorLog("Fields Check","Error! Field names do not match the Data Collection SOP data model.  Check that you are using the most current version of TPP_Features.ddf.",theFC)
            else:
                writeErrorLog("Fields Check","No field errors in found.",theFC)

        if theDataItem=="Point Elements":
            if fieldNameString != pointElementsNameString:
                writeErrorLog("Fields Check","Error! Field names do not match the Data Collection SOP data model.  Check that you are using the most current version of TPP_Features.ddf.",theFC)
            else:
                writeErrorLog("Fields Check","No field errors in found.",theFC)

        if theDataItem=="Line Elements":
            if fieldNameString != lineElementsNameString:
                writeErrorLog("Fields Check","Error! Field names do not match the Data Collection SOP data model.  Check that you are using the most current version of TPP_Features.ddf.",theFC)
            else:
                writeErrorLog("Fields Check","No field errors in found.",theFC)

        if theDataItem=="Termini Points":
            if fieldNameString != terminiPointsNameString:
                writeErrorLog("Fields Check","Error! Field names do not match the Data Collection SOP data model.  Check that you are using the most current version of TPP_Features.ddf.",theFC)
            else:
                writeErrorLog("Fields Check","No field errors in found.",theFC)

    def getFCType(theFC):
        global ws
        rows = gp.SearchCursor(ws + "\\" + theFC)
        row = rows.Next()
        errorFound="False"
        current=""
        while row:
            #DATA_TYPE domain check
            current=row.DATA_TYPE
            
            if compareLists("DATA_TYPE_LIST",row.DATA_TYPE):
                pass            
            else:
                errorFound="True"
            
            row=rows.Next()

        if errorFound=="True":
            writeErrorLog("Feature Type Check","Error! Incorrect DATA_TYPE found.  Field and Data Checks will not run until the DATA_TYPE column is corrected.",theFC)
        else:
            writeErrorLog("Feature Type Check","No feature type errors found.",theFC)

        if 'row' in dir():
            del row
        if 'rows' in dir():
            del rows    

        if errorFound=="False":
            getFCStructure(theFC,current)
            getFCData(theFC,current)            
            
    def createErrorLog():
        #global ws
        global epth
        global fileName
        NewFile = epth + "\\" + "ErrorReport_" + str(fileName) + ".html"
        FILE1 = open(NewFile,"w")
        FILE1.write("<html><head><title>Data Collection Error Report " + str(fileName) + "</title></head><body><table align='center' border='1' cellspacing='0' cellpadding='5'><tr><th colspan='3'>Data Collection Error Report " + str(fileName) + "</th></tr><tr style='background-color:#E8E8E8;'><th>Error Check</th><th>Error Description</th><th>Layer Name</th></tr>")
        FILE1.close()

    def finishErrorLog():
        #global ws
        global epth
        global fileName
        theFile = epth + "\\" + "ErrorReport_" + str(fileName) + ".html"
        FILE1 = open(theFile,"a")
        FILE1.write("<tr align='left'><td colspan='3'>* Fix errors in RED using ArcGIS then re-run the error checks.</td></tr></table></body></html>")
        FILE1.close()    

    def writeErrorLog(theType,theError,theFC):
        #global ws
        global epth
        global fileName
        global errorLogCounter
        modValue = errorLogCounter%2
        theFile = epth + "\\" + "ErrorReport_" + str(fileName) + ".html"
        FILE1 = open(theFile,"a")
        if theError[0:6]=="Error!":
            if modValue==0:
                FILE1.write("<tr style='color:red;background-color:white;'><td>" + theType + "</td><td>" + theError + "</td><td>" + theFC + "</td></tr>")
            else:
                FILE1.write("<tr style='color:red;background-color:#E8E8E8;'><td>" + theType + "</td><td>" + theError + "</td><td>" + theFC + "</td></tr>")
        else:
            if modValue==0:
                FILE1.write("<tr style='background-color:white;'><td>" + theType + "</td><td>" + theError + "</td><td>" + theFC + "</td></tr>")
            else:
                FILE1.write("<tr style='background-color:#E8E8E8;'><td>" + theType + "</td><td>" + theError + "</td><td>" + theFC + "</td></tr>")            
        FILE1.close()
        errorLogCounter+=1

    def listSHPs():
        global ws
        counter=0
        for file in os.listdir(ws):    
            if file.endswith(".shp"):
                print "Checking " + file
                counter+=1
                getFCType(file)

                print "Defining Projection for " + file
                defineProjection(file)

        if counter < 1:
            print "No .shp files were found in " + ws + "."
            raw_input("Press enter to continue...")

    def defineProjection(file):
        global ws
        global gp
        gp.DefineProjection_management(ws + "\\" + file, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")

    def checkDirectories():
        global ws
        global epth
        checkCDrive = "False"
        checkDDrive = "False"
        checkEDrive = "False"
        
        if os.path.exists("C:\\DataCollection\\PostCollectionQAQC"):
            checkCDrive = "True"
            ws = "C:\\DataCollection\\PostCollectionQAQC"        
        if os.path.exists("D:\\DataCollection\\PostCollectionQAQC"):
            checkDDrive = "True"
            ws = "D:\\DataCollection\\PostCollectionQAQC"        
        if os.path.exists("E:\\DataCollection\\PostCollectionQAQC"):
            checkEDrive = "True"
            ws = "E:\\DataCollection\\PostCollectionQAQC"

        if checkCDrive == "False" and checkDDrive == "False" and checkEDrive == "False":
            print "Data Collection Directory not found.  See section 2.2.1 of Data Collection SOP."
            raw_input("Press enter to continue...")        
        else:
            createErrorLog()

            for dirPath, dirNames, fileNames in os.walk(ws):
                for file in fileNames:
                    counter=0                    
                    #listSHPs()
                    if file.endswith(".shp"):
                        ws=dirPath
                        print "Checking " + file
                        counter+=1
                        getFCType(file)

                        print "Defining Projection for " + file
                        defineProjection(file)

                #if counter < 1:
                #print "No .shp files were found in " + ws + "."
                #raw_input("Press enter to continue...")
                
            finishErrorLog()
            os.startfile(epth + "\\" + "ErrorReport_" + str(fileName) + ".html")

    checkDirectories();
    print "End: " + str(datetime.datetime.now().time())

except:
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a 
    #   message string
    #
    pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value)

    # Return python error messages for use with a script tool
    #
    gp.AddError(pymsg)

    # Print Python error messages for use in Python/PythonWin
    #
    print pymsg + "\n\n\n********\n*********\n*********\n*********\n*********\n\nPlease make a screenshot of this error message\nPress and hold the 'ALT' button, then press 'Print Screen'\nCopy this into a Word Document and email to: \nTPP:  Michael.Chamberlain@TxDOT.gov"
    os.system("PAUSE")
    
    

