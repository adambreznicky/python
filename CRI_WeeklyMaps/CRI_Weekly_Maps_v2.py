__date__ = '8/12/2014'
__author__ = 'ABREZNIC'
import os, shutil, arcpy
import datetime

# set variables
weekly_maps_folder = "C:\\TxDOT\\CountyRoadInventory\\_Progress Maps"
exported_cri_sharepoint_excel_name = "County Road Certification.xlsx"

# global variables/date variables
now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
curDate = curMonth + "_" + curDay + "_" + curYear
runday = now.strftime("%B") + " " + curDay + ", " + curYear
house = weekly_maps_folder + os.sep + curYear + os.sep + curDate
arcpy.env.workspace = "in_memory"
sharepoint_table = {}


def build_sharepoint_dict():
    exported_table = weekly_maps_folder + os.sep + exported_cri_sharepoint_excel_name
    print "converting excel sheet"
    arcpy.ExcelToTable_conversion(exported_table, "table")

    print "iterating"
    cursor = arcpy.da.SearchCursor("table", ["County", "Update_Yea", "Status", "Needs_Upda", "Inital_Mar", "Needs_Fiel", "Data_Colle", "Comanche_U"])
    for row in cursor:
        if row[1] == curYear:
            sharepoint_table[row[0]] = row
    del cursor
    del row


def make_directories():
    if os.path.exists(weekly_maps_folder + os.sep + curYear):
        if os.path.exists(weekly_maps_folder + os.sep + curYear + os.sep + curDate):
            shutil.rmtree(weekly_maps_folder + os.sep + curYear + os.sep + curDate)
        else:
            os.makedirs(weekly_maps_folder + os.sep + curYear + os.sep + curDate)
    else:
        os.makedirs(weekly_maps_folder + os.sep + curYear)
        os.makedirs(weekly_maps_folder + os.sep + curYear + os.sep + curDate)


def tracking():
    arcpy.AddMessage("Generating Tracking Map...")
    statusMap = arcpy.mapping.MapDocument(weekly_maps_folder + "\\CRI_TRACKING.mxd")
    dataFrame = arcpy.mapping.ListDataFrames(statusMap)[0]
    newextent = dataFrame.extent

    dict = {}
    counter = 0
    comper = 0

    for record in sharepoint_table.keys():
        county = record
        stat = sharepoint_table[record][2]
        counter += 1
        if stat == "Electronic Update (GIS)" or stat == "Electronic Update (Road Logs)":
            dict[county] = "Electronic Update"
            comper += 1
        elif stat == "Paper Update":
            dict[county] = stat
            comper += 1
        else:
            dict[county] = stat

    #north county:
    if int(curYear) % 2 == 0:
        newextent.XMin, newextent.YMin = 582786.47000423, 826927.373313854
        newextent.XMax, newextent.YMax = 1687689.94133357, 1600359.80324447
        dataFrame.extent = newextent

        cursor = arcpy.da.UpdateCursor(weekly_maps_folder + "\\Tracking_Shapefiles\\NorthCounties.shp", ["status", "CNTY_NM"])
        for row in cursor:
            row[0] = "No Response"
            cursor.updateRow(row)
            cnty = row[1]
            if cnty in dict.keys():
                row[0] = dict[cnty]
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
                textElement.elementPositionX = 6.3
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
        newextent.XMin, newextent.YMin = 364911.216382526, 350798.309516114
        newextent.XMax, newextent.YMax = 1628319.75219708, 1235184.28458639
        dataFrame.extent = newextent

        cursor = arcpy.da.UpdateCursor(weekly_maps_folder + "\\Tracking_Shapefiles\SouthCounties.shp", ["status", "CNTY_NM"])
        for row in cursor:
            row[0] = "No Response"
            cursor.updateRow(row)
            cnty = row[1]
            if cnty in dict.keys():
                row[0] = dict[cnty]
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
    arcpy.AddMessage("Generating Status Map...")
    statusMap = arcpy.mapping.MapDocument(weekly_maps_folder + "\\CRI_STATUS.mxd")
    dataFrame = arcpy.mapping.ListDataFrames(statusMap)[0]
    newextent = dataFrame.extent

    dict = {}
    counter = 0
    comper = 0

    for record in sharepoint_table.keys():
        county = record
        NU = sharepoint_table[record][3]
        NF = sharepoint_table[record][5]
        DC = sharepoint_table[record][6]
        CU = sharepoint_table[record][7]
        if CU == 1:
            dict[county] = "Markup Complete"
            counter += 1
            comper += 1
        elif DC == 1:
            dict[county] = "Field Inventory Complete"
            counter += 1
        elif NF == 1:
            dict[county] = "Pending Field Work"
            counter += 1
        elif NU == 1:
            dict[county] = "Markup Required"
            counter += 1

    #north county:
    if int(curYear) % 2 == 0:
        newextent.XMin, newextent.YMin = 582786.47000423, 826927.373313854
        newextent.XMax, newextent.YMax = 1687689.94133357, 1600359.80324447
        dataFrame.extent = newextent

        cursor = arcpy.da.UpdateCursor(weekly_maps_folder + "\\Status_Shapefiles\\NorthCounties.shp", ["mrk_status", "CNTY_NM"])
        for row in cursor:
            row[0] = ""
            cursor.updateRow(row)
            cnty = row[1]
            if cnty in dict.keys():
                row[0] = dict[cnty]
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
        newextent.XMin, newextent.YMin = 364911.216382526, 350798.309516114
        newextent.XMax, newextent.YMax = 1628319.75219708, 1235184.28458639
        dataFrame.extent = newextent

        cursor = arcpy.da.UpdateCursor(weekly_maps_folder + "\\Status_Shapefiles\\SouthCounties.shp", ["mrk_status", "CNTY_NM"])
        for row in cursor:
            row[0] = ""
            cursor.updateRow(row)
            cnty = row[1]
            if cnty in dict.keys():
                row[0] = dict[cnty]
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
    cri = "T:\\DATAMGT\\MAPPING\\Data Collection\\Core Projects\\CountyRoad"
    if os.path.exists(cri + os.sep + curYear):
        if os.path.exists(cri + os.sep + curYear + os.sep + "_Progress Maps"):
            if os.path.exists(cri + os.sep + curYear + os.sep + "_Progress Maps" + os.sep + curDate):
                shutil.rmtree(weekly_maps_folder + os.sep + curYear + os.sep + curDate)
            os.makedirs(cri + os.sep + curYear + os.sep + "_Progress Maps" + os.sep + curDate)
        else:
            os.makedirs(cri + os.sep + curYear + os.sep + "_Progress Maps")
            os.makedirs(cri + os.sep + curYear + os.sep + "_Progress Maps" + os.sep + curDate)
    else:
        os.makedirs(cri + os.sep + curYear)
        os.makedirs(cri + os.sep + curYear + os.sep + "_Progress Maps")
        os.makedirs(cri + os.sep + curYear + os.sep + "_Progress Maps" + os.sep + curDate)
    tdrive = "T:\\DATAMGT\\MAPPING\\Data Collection\\Core Projects\\CountyRoad\\" + curYear + os.sep + "_Progress Maps" + os.sep + curDate
    shutil.copy(weekly_maps_folder + os.sep + curYear + os.sep + curDate + os.sep + "TrackingMap" + curDate + ".pdf", tdrive)
    shutil.copy(weekly_maps_folder + os.sep + curYear + os.sep + curDate + os.sep + "StatusMap" + curDate + ".pdf", tdrive)
    print "Maps copied to T-drive."


make_directories()
build_sharepoint_dict()
tracking()
status()
tcopy()

print "that's all folks!"
