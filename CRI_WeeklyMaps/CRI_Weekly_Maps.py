__date__ = '8/12/2014'
__author__ = 'ABREZNIC'
import os, shutil, smtplib, base64, arcpy
import datetime
import mohawk

now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
#curYear = str("2012")
curDate = curMonth + "_" + curDay + "_" + curYear
runday = now.strftime("%B") + " " + curDay + ", " + curYear

# os.system('TRACKING\\trackingmap_v1.py')
# os.system('STATUS\\statusmap_v3.py')
def tracking():
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
    if int(curYear) % 2 == 0:
        statusMap = arcpy.mapping.MapDocument("C:\\TxDOT\\CountyRoadInventory\\TRACKING\\CRI_TRACKING.mxd")
        dataFrame = arcpy.mapping.ListDataFrames(statusMap)[0]
        newextent = dataFrame.extent
        newextent.XMin, newextent.YMin = 582786.47000423, 826927.373313854
        newextent.XMax, newextent.YMax = 1687689.94133357, 1600359.80324447
        dataFrame.extent = newextent

        # Local variables:
        owssvr_ = "C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification"

        # Process: Table to Table
        arcpy.TableToTable_conversion(owssvr_, house, "queriedtable.dbf", "",
                                      "ID \"ID\" true true false 8 Double 6 15 ,First,#;Update_Yea \"Update_Yea\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Update Year,-1,-1;District \"District\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,District,-1,-1;County \"County\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,County,-1,-1;Status \"Status\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Status,-1,-1",
                                      "")
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

        differguy2 = float(counter) / float(139) * 100
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
                textElement.text = numsz2 + "% Have Responded (" + str(counter) + " of 139)"
                textElement.elementPositionX = 7.2
                textElement.elementPositionY = 5.8
            if textElement.name == "updater":
                textElement.text = numsz + "% of Responses Require Update (" + str(comper) + " of " + str(counter) + ")"
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
    elif int(curYear) % 2 != 0:
        statusMap = arcpy.mapping.MapDocument("C:\\TxDOT\\CountyRoadInventory\\TRACKING\\CRI_TRACKING.mxd")
        dataFrame = arcpy.mapping.ListDataFrames(statusMap)[0]
        newextent = dataFrame.extent
        newextent.XMin, newextent.YMin = 364911.216382526, 350798.309516114
        newextent.XMax, newextent.YMax = 1628319.75219708, 1235184.28458639
        dataFrame.extent = newextent

        # Local variables:
        owssvr_ = "C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification"

        # Process: Table to Table
        arcpy.TableToTable_conversion(owssvr_, house, "queriedtable.dbf", "",
                                      "ID \"ID\" true true false 8 Double 6 15 ,First,#;Update_Yea \"Update_Yea\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Update Year,-1,-1;District \"District\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,District,-1,-1;County \"County\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,County,-1,-1;Status \"Status\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Status,-1,-1",
                                      "")
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
                textElement.text = numsz2 + "% Have Responded (" + str(counter) + " of 115)"
                textElement.elementPositionX = 1.04
                textElement.elementPositionY = 1.46
            if textElement.name == "updater":
                textElement.text = numsz + "% of Responses Require Update (" + str(comper) + " of " + str(counter) + ")"
                textElement.elementPositionX = 1.04
                textElement.elementPositionY = 1.14
            arcpy.AddMessage("Text elements updated.")
        legend = arcpy.mapping.ListLayoutElements(statusMap, "LEGEND_ELEMENT")[0]
        legend.elementPositionX = 1.04
        legend.elementPositionY = 1.88
        arcpy.AddMessage("Legend moved.")

        arcpy.RefreshActiveView()
        arcpy.mapping.ExportToPDF(statusMap, house + os.sep + "TrackingMap" + curDate + ".pdf")

    arcpy.AddMessage("Tracking Map Complete.")

def status():
    home = "C:\\TxDOT\\CountyRoadInventory\\STATUS\\"

    arcpy.AddMessage("Generating Status Map...")


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
    if int(curYear) % 2 == 0:
        statusMap = arcpy.mapping.MapDocument("C:\\TxDOT\\CountyRoadInventory\\STATUS\\CRI_STATUS.mxd")
        dataFrame = arcpy.mapping.ListDataFrames(statusMap)[0]
        newextent = dataFrame.extent
        newextent.XMin, newextent.YMin = 582786.47000423, 826927.373313854
        newextent.XMax, newextent.YMax = 1687689.94133357, 1600359.80324447
        dataFrame.extent = newextent

        # Local variables:
        owssvr_ = "C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification"

        # Process: Table to Table
        arcpy.TableToTable_conversion(owssvr_, house, "queriedtable.dbf", "",
                                      "Update_Yea \"Update_Yea\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Update Year,-1,-1;County \"County\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,County,-1,-1;Needs_Upda \"Needs_Upda\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Needs Update,-1,-1;Inital_Mar \"Inital_Mar\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Inital Markup Complete,-1,-1;Needs_Fiel \"Needs_Fiel\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Needs Field Verification,-1,-1;Data_Colle \"Data_Colle\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Data Collected,-1,-1;Comanche_U \"Comanche_U\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Comanche Updated,-1,-1",
                                      "")

        queriedtable = house + os.sep + "queriedtable.dbf"

        dict = {}
        counter = 0
        comper = 0

        kursor = arcpy.SearchCursor(queriedtable, """"Update_Yea" = '""" + curYear + """'""")
        for row in kursor:
            county = row.getValue("County")
            NU = row.getValue("Needs_Upda")
            NF = row.getValue("Needs_Fiel")
            DC = row.getValue("Data_Colle")
            CU = row.getValue("Comanche_U")
            if CU == -1:
                dict[county] = "Markup Complete"
                counter += 1
                comper += 1
            elif DC == -1:
                dict[county] = "Field Inventory Complete"
                counter += 1
            elif NF == -1:
                dict[county] = "Pending Field Work"
                counter += 1
            elif NU == -1:
                dict[county] = "Markup Required"
                counter += 1
        del kursor

        cursor = arcpy.UpdateCursor("C:\\TxDOT\\CountyRoadInventory\\STATUS\\Shapefiles\\NorthCounties.shp")
        for row in cursor:
            row.setValue("mrk_status", "")
            cursor.updateRow(row)
            cnty = row.getValue("CNTY_NM")
            if cnty in dict.keys():
                row.setValue("mrk_status", dict[cnty])
            cursor.updateRow(row)
        del cursor
        if counter == 0:
            counter += 1

        differguy = float(comper) / float(counter) * 100
        integ = str(differguy).split(".")[0]
        deci = str(differguy).split(".")[1][:2]
        numsz = integ + "." + deci

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
            if textElement.name == "complete":
                textElement.text = numsz + "% Complete (" + str(comper) + " of " + str(counter) + ")"
                textElement.elementPositionX = 7.6
                textElement.elementPositionY = 5.9
            arcpy.AddMessage("Text elements updated.")
        legend = arcpy.mapping.ListLayoutElements(statusMap, "LEGEND_ELEMENT")[0]
        legend.elementPositionX = 7.4
        legend.elementPositionY = 6.4
        arcpy.AddMessage("Legend moved.")

        arcpy.RefreshActiveView()
        arcpy.mapping.ExportToPDF(statusMap, house + os.sep + "StatusMap" + curDate + ".pdf")
    #
    # south county
    elif int(curYear) % 2 != 0:
        statusMap = arcpy.mapping.MapDocument("C:\\TxDOT\\CountyRoadInventory\\STATUS\\CRI_STATUS.mxd")
        dataFrame = arcpy.mapping.ListDataFrames(statusMap)[0]
        newextent = dataFrame.extent
        newextent.XMin, newextent.YMin = 364911.216382526, 350798.309516114
        newextent.XMax, newextent.YMax = 1628319.75219708, 1235184.28458639
        dataFrame.extent = newextent

        # Local variables:
        owssvr_ = "C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification"

        # Process: Table to Table
        arcpy.TableToTable_conversion(owssvr_, house, "queriedtable.dbf", "",
                                      "Update_Yea \"Update_Yea\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Update Year,-1,-1;County \"County\" true true false 255 Text 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,County,-1,-1;Needs_Upda \"Needs_Upda\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Needs Update,-1,-1;Inital_Mar \"Inital_Mar\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Inital Markup Complete,-1,-1;Needs_Fiel \"Needs_Fiel\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Needs Field Verification,-1,-1;Data_Colle \"Data_Colle\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Data Collected,-1,-1;Comanche_U \"Comanche_U\" true true false 2 Short 0 0 ,First,#,C:\\TxDOT\\CountyRoadInventory\\Book1.xlsx\\County_Road_Certification,Comanche Updated,-1,-1",
                                      "")

        queriedtable = house + os.sep + "queriedtable.dbf"

        dict = {}
        counter = 0
        comper = 0

        kursor = arcpy.SearchCursor(queriedtable, """"Update_Yea" = '""" + curYear + """'""")
        for row in kursor:
            county = row.getValue("County")
            NU = row.getValue("Needs_Upda")
            NF = row.getValue("Needs_Fiel")
            DC = row.getValue("Data_Colle")
            CU = row.getValue("Comanche_U")
            if CU == -1:
                dict[county] = "Markup Complete"
                counter += 1
                comper += 1
            elif DC == -1:
                dict[county] = "Field Inventory Complete"
                counter += 1
            elif NF == -1:
                dict[county] = "Pending Field Work"
                counter += 1
            elif NU == -1:
                dict[county] = "Markup Required"
                counter += 1
        del kursor

        cursor = arcpy.UpdateCursor("C:\\TxDOT\\CountyRoadInventory\\STATUS\\Shapefiles\\SouthCounties.shp")
        for row in cursor:
            row.setValue("mrk_status", "")
            cursor.updateRow(row)
            cnty = row.getValue("CNTY_NM")
            if cnty in dict.keys():
                row.setValue("mrk_status", dict[cnty])
            cursor.updateRow(row)
        del cursor
        if counter == 0:
            counter += 1

        differguy = float(comper) / float(counter) * 100
        integ = str(differguy).split(".")[0]
        deci = str(differguy).split(".")[1][:2]
        numsz = integ + "." + deci

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
            if textElement.name == "complete":
                textElement.text = numsz + "% Complete (" + str(comper) + " of " + str(counter) + ")"
                textElement.elementPositionX = 1.41
                textElement.elementPositionY = 1.46
            arcpy.AddMessage("Text elements updated.")
        legend = arcpy.mapping.ListLayoutElements(statusMap, "LEGEND_ELEMENT")[0]
        legend.elementPositionX = 1.25
        legend.elementPositionY = 1.9
        arcpy.AddMessage("Legend moved.")

        arcpy.RefreshActiveView()
        arcpy.mapping.ExportToPDF(statusMap, house + os.sep + "StatusMap" + curDate + ".pdf")

    arcpy.AddMessage("Status Map Complete.")

def tcopy():
    tdrive = "T:\\DATAMGT\\MAPPING\\Data Collection\\Core Projects\\CountyRoad\\" + curYear + "\\_Progress Maps"
    os.makedirs(tdrive + os.sep + curDate)
    bucket = tdrive + os.sep + curDate
    shutil.copy("C:\\TxDOT\\CountyRoadInventory\\TRACKING\\" + curYear + os.sep + curDate + os.sep + "TrackingMap" + curDate + ".pdf", bucket)
    shutil.copy("C:\\TxDOT\\CountyRoadInventory\\STATUS\\" + curYear + os.sep + curDate + os.sep + "StatusMap" + curDate + ".pdf", bucket)
    print "Maps copied to T-drive."

def email():
    tdrive = "T:\\DATAMGT\\MAPPING\\Data Collection\\Core Projects\\CountyRoad\\" + curYear + "\\_Progress Maps"
    bucket = tdrive + os.sep + curDate
    FROM = 'adam.breznicky@txdot.gov'
    TO = ['Michael.Zugelder@txdot.gov']
    SUBJECT = "CRI Progress Maps Updated " + runday
    TEXT = "The County Road Inventory project maps have been updated and posted on the T-Drive.\nYou can find a copy of the progress maps here:\n\n" \
           + bucket + "\n\nLove, Adam"
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
                """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    username = "adam.breznicky@txdot.gov"
    password = mohawk.hangnail(username)
    # server = smtplib.SMTP('owa.txdot.gov', 25)
    server = smtplib.SMTP('owa.txdot.gov', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.sendmail(FROM, TO, message)
    server.close()
    print "Email delivered."

tracking()
status()
# tcopy()
# email()

print "that's all folks!"