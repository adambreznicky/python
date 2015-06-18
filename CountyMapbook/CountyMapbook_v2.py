__file__ = 'CountyMapbook_v1'
__date__ = '6/18/2014'
__author__ = 'ABREZNIC'
import os, arcpy,datetime
from arcpy import env
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, Paragraph, frames, Table, TableStyle, Frame, flowables, Flowable, PageTemplate


#date
now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + "_" + curMonth + "_" + curDay

#variables
cofolder = "C:\\TxDOT\\CountyMapbook"
workspace = cofolder + "\\" + curYear
database = workspace + "\\Working.gdb"
comanche = "Connection to Comanche.sde"

histmarkers = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Texas_Historical_Commission\\TPP_GIS.APP_TPP_GIS_ADMIN.Historical_Markers"
campgrounds = ""
restareas = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Travel\\TPP_GIS.APP_TPP_GIS_ADMIN.REST_AREA_PNT"
parks = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Park\\TPP_GIS.APP_TPP_GIS_ADMIN.Public_Lands_2014"
cemeteries = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Cemetery\\TPP_GIS.APP_TPP_GIS_ADMIN.Cemetery"
cemeteriesPT = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Cemetery\\TPP_GIS.APP_TPP_GIS_ADMIN.Cemetery_Points"
roads = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
counties = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.County\\TPP_GIS.APP_TPP_GIS_ADMIN.County"
airports = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Airport\\TPP_GIS.APP_TPP_GIS_ADMIN.Airport"
airportsPT = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Airport\\TPP_GIS.APP_TPP_GIS_ADMIN.Airport_Points"
prisons = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Base_Map_Layers\\TPP_GIS.APP_TPP_GIS_ADMIN.Prisons"
military = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Base_Map_Layers\\TPP_GIS.APP_TPP_GIS_ADMIN.Military"
schools = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Base_Map_Layers\\TPP_GIS.APP_TPP_GIS_ADMIN.Education"
cities = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.City\\TPP_GIS.APP_TPP_GIS_ADMIN.City"
citiesPT = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.City\\TPP_GIS.APP_TPP_GIS_ADMIN.City_Points"
lakes = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Water\\TPP_GIS.APP_TPP_GIS_ADMIN.Water_Bodies"
railroads = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Railroad\\TPP_GIS.APP_TPP_GIS_ADMIN.Railroads"
rivers = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Water\\TPP_GIS.APP_TPP_GIS_ADMIN.Streams"
grid = "Database Connections\\" + comanche + "\\TPP_GIS.MCHAMB1.Map_Index_Grids\\TPP_GIS.MCHAMB1.State_Grid_120K"

def preparation():
    print "Creating database..."
    if not os.path.exists(workspace):
        os.makedirs(workspace)
    else:
        try:
            arcpy.Delete_management(database)
        except:
            pass
        for file in os.listdir(workspace):
            thefile = os.path.join(workspace, file)
            os.remove(thefile)
    arcpy.CreateFileGDB_management(workspace, "Working.gdb")
    print "Copying historical markers..."
    arcpy.Select_analysis(histmarkers, database + "\\histmarkers", "markernum IS NOT NULL and indexname IS NOT NULL")
    arcpy.AddField_management(database + "\\histmarkers", "label", "TEXT", "", "", 200)
    cursor = arcpy.UpdateCursor(database + "\\histmarkers")
    for row in cursor:
        row.setValue("label", str(row.markernum) + " - " + row.indexname)
        cursor.updateRow(row)
    del cursor
    del row
    print "Copying campgrounds..."

    print "Copying rest areas..."
    arcpy.Copy_management(restareas, database + "\\restareas")
    arcpy.AddField_management(database + "\\restareas", "label", "TEXT", "", "", 200)
    cursor = arcpy.UpdateCursor(database + "\\restareas")
    for row in cursor:
        if row.RA_TYPE_NM == "Picnic":
            row.setValue("label", "Picnic Area")
        elif row.RA_TYPE_NM == "Rest":
            row.setValue("label", "Rest Area")
        elif row.RA_TYPE_NM == "Rest_EX":
            row.setValue("label", "Rest Area (EX)")
        elif row.RA_TYPE_NM == "TIC":
            row.setValue("label", "Travel Information Center")
        else:
            cursor.deleteRow(row)
        cursor.updateRow(row)
    del cursor
    del row
    print "Copying parks..."
    arcpy.Select_analysis(parks, database + "\\parks", "(GOVT_JURIS = '3' OR GOVT_JURIS = '4') AND LAND_NM IS NOT NULL AND LAND_NM <> ''")
    print "Copying cemeteries..."
    arcpy.Select_analysis(cemeteries, database + "\\cemeteries", "CEMETERY_NM IS NOT NULL AND CEMETERY_NM <> ''")
    arcpy.Select_analysis(cemeteriesPT, database + "\\cemeteries_point", "CEMETERY_NM IS NOT NULL AND CEMETERY_NM <> ''")
    print "Copying highways..."
    arcpy.Select_analysis(roads, database + "\\highways", "(( RTE_CLASS = '1' OR RTE_CLASS = '6' ) AND RDBD_TYPE = 'KG' AND RTE_OPEN = 1 ) OR (RTE_NM = 'SL0008' AND RDBD_TYPE = 'KG' AND RTE_OPEN = 1 )")
    print "Copying counties..."
    arcpy.Copy_management(counties, database + "\\counties")
    print "Copying airports..."
    arcpy.Select_analysis(airports, database + "\\airports", "ARPRT_NM <> '' AND ARPRT_NM IS NOT NULL")
    arcpy.Select_analysis(airportsPT, database + "\\airports_point", "DISPLAY = 'Yes'")
    print "Copying county roads..."
    arcpy.Select_analysis(roads, database + "\\countyroads", "RTE_CLASS = '2' AND RTE_OPEN = 1 AND RDBD_TYPE = 'KG'")
    print "Copying prisons..."
    arcpy.Copy_management(prisons, database + "\\prisons")
    print "Copying military..."
    arcpy.Copy_management(military, database + "\\military")
    print "Copying schools..."
    arcpy.Copy_management(schools, database + "\\schools")
    print "Copying cities..."
    arcpy.Copy_management(cities, database + "\\cities")
    arcpy.Select_analysis(citiesPT, database + "\\cities_point", "INC = 'N'")
    print "Copying lakes..."
    arcpy.Select_analysis(lakes, database + "\\lakes", "BODY_NM IS NOT NULL AND BODY_NM <>  '' AND BODY_TYPE = '1'")
    print "Copying railroads..."
    arcpy.Select_analysis(railroads, database + "\\railroads", "RR_TYPE = 'M' AND RR_STAT = 'A'")
    print "Copying rivers..."
    arcpy.Select_analysis(rivers, database + "\\rivers", "STRM_TYPE = '1'")
    print "Copying federal roads..."
    arcpy.Select_analysis(roads, database + "\\federalroads", "RTE_CLASS = '7' AND RTE_OPEN = 1 AND RDBD_TYPE = 'KG' AND FULL_ST_NM <> '' AND FULL_ST_NM IS NOT NULL")
    print "Copying grid..."
    arcpy.Copy_management(grid, database + "\\grid")
    #
    print "Renumbering grid..."
    cursor = arcpy.UpdateCursor(database + "\\grid")
    for row in cursor:
        row.setValue("ID", row.ID - 66)
        row.setValue("STATE_ID", row.STATE_ID - 66)
        if row.NORTH != 0:
            row.setValue("NORTH", row.NORTH - 66)
        if row.SOUTH != 0:
            row.setValue("SOUTH", row.SOUTH - 66)
        if row.EAST != 0:
            row.setValue("EAST", row.EAST - 66)
        if row.WEST != 0:
            row.setValue("WEST", row.WEST - 66)
        cursor.updateRow(row)
    del cursor
    del row
    print "Creating union..."
    arcpy.Union_analysis([database + "\\grid", database + "\\counties"], database + "\\union")
    cursor = arcpy.UpdateCursor(database + "\\union")
    for row in cursor:
        if row.CNTY_NM == "" or row.CNTY_NM is None or row.ID == 0:
            cursor.deleteRow(row)
    del cursor
    del row

def intersects():
    env.workspace = database
    print "Creating field dictionary..."
    dict = {}
    dict["histmarkers"] = "label"
    #dict["campgrounds"] = ""
    dict["restareas"] = "label"
    dict["parks"] = "LAND_NM"
    dict["cemeteries"] = "CEMETERY_NM"
    dict["cemeteries_point"] = "CEMETERY_NM"
    dict["highways"] = "FULL_ST_NM"
    dict["counties"] = "CNTY_NM"
    dict["airports"] = "ARPRT_NM"
    dict["airports_point"] = "ARPRT_NM"
    dict["countyroads"] = "FULL_ST_NM"
    dict["prisons"] = "PRISON_NM"
    dict["military"] = "BASE_NM"
    dict["schools"] = "SCHOOL_NM"
    dict["cities"] = "CITY_NM"
    dict["cities_point"] = "CITY_NM"
    dict["lakes"] = "BODY_NM"
    dict["railroads"] = "RR_NM"
    dict["rivers"] = "STRM_NM"
    dict["federalroads"] = "FULL_ST_NM"

    print "Performing intersects..."
    fcList = arcpy.ListFeatureClasses()
    for fc in fcList:
        if fc != "union" and fc != "grid":
            print str(fc)
            arcpy.Intersect_analysis(["union", fc], fc + "__INTERSECT")
    del fcList
    del fc
    print "Summarizing..."
    fcList = arcpy.ListFeatureClasses()
    for fc in fcList:
        if fc.split("__")[-1] == "INTERSECT":
            dictname = fc.split("__")[0]
            print dictname
            field = dict[dictname]
            arcpy.AddField_management(fc, "UNIQUE", "TEXT", "", "", 250)
            cursor = arcpy.UpdateCursor(fc)
            for row in cursor:
                value = row.getValue(field)
                if value is None:
                    value = ""
                row.setValue("UNIQUE", str(row.ID) + row.CNTY_NM + value)
                cursor.updateRow(row)
            del cursor
            del row
            arcpy.Statistics_analysis(fc, dictname + "_SUMMARIZED", [["ID", "MIN"], ["CNTY_NM", "FIRST"], [dict[dictname], "FIRST"]], ["UNIQUE"])
    print "Merging with point tables..."
    arcpy.Merge_management(["cemeteries_SUMMARIZED", "cemeteries_point_SUMMARIZED"], "cemeteries_all_SUMMARIZED")
    arcpy.Merge_management(["airports_SUMMARIZED", "airports_point_SUMMARIZED"], "airports_all_SUMMARIZED")
    arcpy.Merge_management(["cities_SUMMARIZED", "cities_point_SUMMARIZED"], "cities_all_SUMMARIZED")
    print "Renaming tables..."
    arcpy.Rename_management("cemeteries_SUMMARIZED", "cemeteries_SUMpreMERGE")
    arcpy.Rename_management("cemeteries_point_SUMMARIZED", "cemeteries_point_SUMpreMERGE")
    arcpy.Rename_management("airports_SUMMARIZED", "airports_SUMpreMERGE")
    arcpy.Rename_management("airports_point_SUMMARIZED", "airports_point_SUMpreMERGE")
    arcpy.Rename_management("cities_SUMMARIZED", "cities_SUMpreMERGE")
    arcpy.Rename_management("cities_point_SUMMARIZED", "cities_point_SUMpreMERGE")

def pdf():
    print "Making directory..."
    if not os.path.exists(workspace + "\\PDF"):
        os.makedirs(workspace + "\\PDF")
    else:
        for file in os.listdir(workspace + "\\PDF"):
            thefile = os.path.join(workspace + "\\PDF", file)
            os.remove(thefile)
    #
    print "Creating field dictionary..."
    dict = {}
    dict["histmarkers"] = "label"
    #dict["campgrounds"] = ""
    dict["restareas"] = "label"
    dict["parks"] = "LAND_NM"
    dict["cemeteries"] = "CEMETERY_NM"
    dict["cemeteries_point"] = "CEMETERY_NM"
    dict["highways"] = "FULL_ST_NM"
    dict["counties"] = "CNTY_NM"
    dict["airports"] = "ARPRT_NM"
    dict["airports_point"] = "ARPRT_NM"
    dict["countyroads"] = "FULL_ST_NM"
    dict["prisons"] = "PRISON_NM"
    dict["military"] = "BASE_NM"
    dict["schools"] = "SCHOOL_NM"
    dict["cities"] = "CITY_NM"
    dict["cities_point"] = "CITY_NM"
    dict["lakes"] = "BODY_NM"
    dict["railroads"] = "RR_NM"
    dict["rivers"] = "STRM_NM"
    dict["federalroads"] = "FULL_ST_NM"
    #
    print "Creating label dictionary..."
    dict2 = {}
    dict2["histmarkers"] = ["Marker", "Historical Markers", 1]
    #dict2["campgrounds"] = [""]
    dict2["restareas"] = ["Rest Area", "Rest Areas", 1]
    dict2["parks"] = ["Park", "Parks", 1]
    dict2["cemeteries"] = ["Cemetery", "Cemeteries", 1]
    dict2["cemeteries_point"] = ["Cemetery", "Cemeteries", 1]
    dict2["highways"] = ["Highway", "Highways", 1]
    dict2["counties"] = ["County", "Counties", 1]
    dict2["airports"] = ["Airport", "Airports", 1]
    dict2["airports_point"] = ["Airport", "Airports", 1.925]
    dict2["countyroads"] = ["Street", "County Roads", 1]
    dict2["prisons"] = ["Prison", "Prisons", 1]
    dict2["military"] = ["Military Base", "Military Bases", 1]
    dict2["schools"] = ["School", "Schools", 1]
    dict2["cities"] = ["City", "Cities", 1]
    dict2["cities_point"] = ["City", "Cities", 1]
    dict2["lakes"] = ["Lake", "Lakes", 1]
    dict2["railroads"] = ["Railroad", "Railroads", 1]
    dict2["rivers"] = ["River", "Major Rivers", 1]
    dict2["federalroads"] = ["Roadway", "Federal Roads", 1]
    #
    print "Creating index PDF pages..."
    env.workspace = database
    fcList = arcpy.ListTables()
    fcList.sort()
    for fc in fcList:
        if fc.split("_")[-1] == "SUMMARIZED":
            feature = fc.split("_")[0]
            print feature
            title = dict2[feature][1]
            subtitle = dict2[feature][0]
            wide = dict2[feature][2]
            from reportlab.lib.pagesizes import ELEVENSEVENTEEN, landscape
            width, height = landscape(ELEVENSEVENTEEN)
            f = frames.Frame(.8*inch, .8*inch, wide*inch, 9.4*inch, bottomPadding=1)
            f2 = frames.Frame((.8 + 2 * wide)*inch, .8*inch, wide*inch, 9.4*inch, bottomPadding=1)
            f3 = frames.Frame((.8 + 3 * wide), .8*inch, wide*inch, 9.4*inch, bottomPadding=1)
            f4 = frames.Frame((.8 + 4 * wide), .8*inch, wide*inch, 9.4*inch, bottomPadding=1)
            f5 = frames.Frame((.8 + 5 * wide), .8*inch, wide*inch, 9.4*inch, bottomPadding=1)
            f6 = frames.Frame((.8 + 6 * wide), .8*inch, wide*inch, 9.4*inch, bottomPadding=1)
            f7 = frames.Frame((.8 + 7 * wide), .8*inch, wide*inch, 9.4*inch, bottomPadding=1)
            f8 = frames.Frame((.8 + 8 * wide), .8*inch, wide*inch, 9.4*inch, bottomPadding=1)
            doc = BaseDocTemplate(workspace + "\\PDF\\" + fc + ".pdf", pagesize=landscape(ELEVENSEVENTEEN))
            def thecanvas(c, doc):
                from reportlab.lib.pagesizes import ELEVENSEVENTEEN, landscape
                width, height = landscape(ELEVENSEVENTEEN)
                c.setFont("Helvetica-Bold", 18)
                c.setFillColorRGB(0, 0, 1)
                c.drawCentredString(width/2,height - .7*inch, title.upper())
                c.setFillColorRGB(.5, .3, .1)
                #hortizontal lines
                c.line(.75*inch, height - .75*inch, width - .75*inch, height - .75*inch)
                c.line(.75*inch, .75*inch, width - .75*inch, .75*inch)

                c.setFont("Times-Bold", 8)
                c.setFillColorRGB(0, 0, 0)
                pageNUM = c.getPageNumber()
                c.drawRightString(width-.75*inch, .6*inch, "Page " + str(pageNUM))
            doc.addPageTemplates([PageTemplate(frames=[f, f2, f3, f4, f5, f6, f7, f8], onPage=thecanvas)])
            #
            elements = []
            data = []
            dictvalue = dict[fc.split("_")[0]]
            cursor = arcpy.SearchCursor(fc, "", "", "", "FIRST_CNTY_NM A; FIRST_" + dictvalue + " A; MIN_ID A")
            starter = 0
            counto = int(arcpy.GetCount_management(fc).getOutput(0))
            total = counto-1
            previous = ""
            for row in cursor:
                current = row.FIRST_CNTY_NM
                if starter == 0:
                    line = ["", current, ""]
                    data.append(line)
                    t = Table(data, colWidths=[.1*inch, 1.725*inch, .1*inch], rowHeights=[.3*inch]*len(data), )
                    t.setStyle(TableStyle([
                        ('FONTNAME', (1, 0), (1, 0), 'Times-Bold'),
                        ('FONTSIZE', (1, 0), (1, 0), 12),
                        ('TEXTCOLOR', (1, 0), (1, 0), colors.red),
                        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                        ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
                        ('LINEBEFORE', (0, 0), (0, 0), 1, colors.saddlebrown),
                        ('LINEAFTER', (2, 0), (2, 0), 1, colors.saddlebrown),
                        ('LINEBELOW', (1, 0), (1, 0), 1, colors.saddlebrown)
                        ]))
                    elements.append(t)
                    data = []
                    line = [""]
                    data.append(line)
                    t = Table(data, colWidths=[1.925*inch], rowHeights=[.1*inch]*len(data), )
                    t.setStyle(TableStyle([
                        ('LINEBEFORE', (0, 0), (0, 0), 1, colors.saddlebrown),
                        ('LINEAFTER', (0, 0), (0, 0), 1, colors.saddlebrown)
                        ]))
                    elements.append(t)
                    data = []
                    line = [subtitle, "Page"]
                    data.append(line)
                    t = Table(data, colWidths=[1.625*inch, .3*inch], rowHeights=[.12*inch]*len(data))
                    t.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (1, (len(data)-1)), 'Times-BoldItalic'),
                        ('FONTSIZE', (0, 0), (1, (len(data)-1)), 6),
                        ('TEXTCOLOR', (0, 0), (1, (len(data)-1)), colors.darkblue),
                        ('ALIGN', (0, 0), (0, (len(data)-1)), 'LEFT'),
                        ('ALIGN', (1, 0), (1, (len(data)-1)), 'RIGHT'),
                        ('LINEBEFORE', (0, 0), (0, (len(data)-1)), 1, colors.saddlebrown),
                        ('LINEAFTER', (1, 0), (1, (len(data)-1)), 1, colors.saddlebrown),
                        ('BOTTOMPADDING', (0, 0), (1, (len(data)-1)), -1)
                        ]))
                    elements.append(t)
                    data = []
                    cellvalue = row.getValue("FIRST_" + dictvalue)
                    line = [cellvalue, int(row.MIN_ID)]
                    data.append(line)
                    previous = current
                elif current == previous and starter != total:
                    cellvalue = row.getValue("FIRST_" + dictvalue)
                    line = [cellvalue, int(row.MIN_ID)]
                    data.append(line)
                    previous = current
                elif current != previous and starter != total:
                    t = Table(data, colWidths=[1.625*inch, .3*inch], rowHeights=[.12*inch]*len(data))
                    t.setStyle(TableStyle([
                        ('FONTSIZE', (0, 0), (1, (len(data)-1)), 6),
                        ('ALIGN', (0, 0), (0, (len(data)-1)), 'LEFT'),
                        ('ALIGN', (1, 0), (1, (len(data)-1)), 'RIGHT'),
                        ('BACKGROUND', (1, 0), (1, (len(data)-1)), colors.Color(.9, .9, .9)),
                        ('LINEBEFORE', (0, 0), (0, (len(data)-1)), 1, colors.saddlebrown),
                        ('LINEAFTER', (1, 0), (1, (len(data)-1)), 1, colors.saddlebrown),
                        ('BOTTOMPADDING', (0, 0), (1, (len(data)-1)), -4)
                        ]))
                    elements.append(t)
                    previous = current
                    data = []
                    line = ["", current, ""]
                    data.append(line)
                    t = Table(data, colWidths=[.1*inch, 1.725*inch, .1*inch], rowHeights=[.3*inch]*len(data), )
                    t.setStyle(TableStyle([
                        ('FONTNAME', (1, 0), (1, 0), 'Times-Bold'),
                        ('FONTSIZE', (1, 0), (1, 0), 12),
                        ('TEXTCOLOR', (1, 0), (1, 0), colors.red),
                        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                        ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
                        ('LINEBEFORE', (0, 0), (0, 0), 1, colors.saddlebrown),
                        ('LINEAFTER', (2, 0), (2, 0), 1, colors.saddlebrown),
                        ('LINEBELOW', (1, 0), (1, 0), 1, colors.saddlebrown)
                        ]))
                    elements.append(t)
                    data = []
                    line = [""]
                    data.append(line)
                    t = Table(data, colWidths=[1.925*inch], rowHeights=[.1*inch]*len(data), )
                    t.setStyle(TableStyle([
                        ('LINEBEFORE', (0, 0), (0, 0), 1, colors.saddlebrown),
                        ('LINEAFTER', (0, 0), (0, 0), 1, colors.saddlebrown)
                        ]))
                    elements.append(t)
                    data = []
                    line = [subtitle, "Page"]
                    data.append(line)
                    t = Table(data, colWidths=[1.625*inch, .3*inch], rowHeights=[.12*inch]*len(data))
                    t.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (1, (len(data)-1)), 'Times-BoldItalic'),
                        ('FONTSIZE', (0, 0), (1, (len(data)-1)), 6),
                        ('TEXTCOLOR', (0, 0), (1, (len(data)-1)), colors.darkblue),
                        ('ALIGN', (0, 0), (0, (len(data)-1)), 'LEFT'),
                        ('ALIGN', (1, 0), (1, (len(data)-1)), 'RIGHT'),
                        ('LINEBEFORE', (0, 0), (0, (len(data)-1)), 1, colors.saddlebrown),
                        ('LINEAFTER', (1, 0), (1, (len(data)-1)), 1, colors.saddlebrown),
                        ('BOTTOMPADDING', (0, 0), (1, (len(data)-1)), -1)
                        ]))
                    elements.append(t)
                    data = []
                    cellvalue = row.getValue("FIRST_" + dictvalue)
                    line = [cellvalue, int(row.MIN_ID)]
                    data.append(line)
                elif current == previous and starter == total:
                    cellvalue = row.getValue("FIRST_" + dictvalue)
                    line = [cellvalue, int(row.MIN_ID)]
                    data.append(line)
                    t = Table(data, colWidths=[1.625*inch, .3*inch], rowHeights=[.12*inch]*len(data))
                    t.setStyle(TableStyle([
                        ('FONTSIZE', (0, 0), (1, (len(data)-1)), 6),
                        ('ALIGN', (0, 0), (0, (len(data)-1)), 'LEFT'),
                        ('ALIGN', (1, 0), (1, (len(data)-1)), 'RIGHT'),
                        ('BACKGROUND', (1, 0), (1, (len(data)-1)), colors.Color(.9, .9, .9)),
                        ('LINEBEFORE', (0, 0), (0, (len(data)-1)), 1, colors.saddlebrown),
                        ('LINEAFTER', (1, 0), (1, (len(data)-1)), 1, colors.saddlebrown),
                        ('BOTTOMPADDING', (0, 0), (1, (len(data)-1)), -4)
                        ]))
                    elements.append(t)
                elif current != previous and starter == total:
                    t = Table(data, colWidths=[1.625*inch, .3*inch], rowHeights=[.12*inch]*len(data))
                    t.setStyle(TableStyle([
                        ('FONTSIZE', (0, 0), (1, (len(data)-1)), 6),
                        ('ALIGN', (0, 0), (0, (len(data)-1)), 'LEFT'),
                        ('ALIGN', (1, 0), (1, (len(data)-1)), 'RIGHT'),
                        ('BACKGROUND', (1, 0), (1, (len(data)-1)), colors.Color(.9, .9, .9)),
                        ('LINEBEFORE', (0, 0), (0, (len(data)-1)), 1, colors.saddlebrown),
                        ('LINEAFTER', (1, 0), (1, (len(data)-1)), 1, colors.saddlebrown),
                        ('BOTTOMPADDING', (0, 0), (1, (len(data)-1)), -4)
                        ]))
                    elements.append(t)
                    previous = current
                    data = []
                    line = ["", current, ""]
                    data.append(line)
                    t = Table(data, colWidths=[.1*inch, 1.725*inch, .1*inch], rowHeights=[.3*inch]*len(data), )
                    t.setStyle(TableStyle([
                        ('FONTNAME', (1, 0), (1, 0), 'Times-Bold'),
                        ('FONTSIZE', (1, 0), (1, 0), 12),
                        ('TEXTCOLOR', (1, 0), (1, 0), colors.red),
                        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                        ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
                        ('LINEBEFORE', (0, 0), (0, 0), 1, colors.saddlebrown),
                        ('LINEAFTER', (2, 0), (2, 0), 1, colors.saddlebrown),
                        ('LINEBELOW', (1, 0), (1, 0), 1, colors.saddlebrown)
                        ]))
                    elements.append(t)
                    data = []
                    line = [""]
                    data.append(line)
                    t = Table(data, colWidths=[1.925*inch], rowHeights=[.1*inch]*len(data), )
                    t.setStyle(TableStyle([
                        ('LINEBEFORE', (0, 0), (0, 0), 1, colors.saddlebrown),
                        ('LINEAFTER', (0, 0), (0, 0), 1, colors.saddlebrown)
                        ]))
                    elements.append(t)
                    data = []
                    line = [subtitle, "Page"]
                    data.append(line)
                    t = Table(data, colWidths=[1.625*inch, .3*inch], rowHeights=[.12*inch]*len(data))
                    t.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (1, (len(data)-1)), 'Times-BoldItalic'),
                        ('FONTSIZE', (0, 0), (1, (len(data)-1)), 6),
                        ('TEXTCOLOR', (0, 0), (1, (len(data)-1)), colors.darkblue),
                        ('ALIGN', (0, 0), (0, (len(data)-1)), 'LEFT'),
                        ('ALIGN', (1, 0), (1, (len(data)-1)), 'RIGHT'),
                        ('LINEBEFORE', (0, 0), (0, (len(data)-1)), 1, colors.saddlebrown),
                        ('LINEAFTER', (1, 0), (1, (len(data)-1)), 1, colors.saddlebrown),
                        ('BOTTOMPADDING', (0, 0), (1, (len(data)-1)), -1)
                        ]))
                    elements.append(t)
                    data = []
                    cellvalue = row.getValue("FIRST_" + dictvalue)
                    line = [cellvalue, int(row.MIN_ID)]
                    data.append(line)
                    t = Table(data, colWidths=[1.625*inch, .3*inch], rowHeights=[.12*inch]*len(data))
                    t.setStyle(TableStyle([
                        ('FONTSIZE', (0, 0), (1, (len(data)-1)), 6),
                        ('ALIGN', (0, 0), (0, (len(data)-1)), 'LEFT'),
                        ('ALIGN', (1, 0), (1, (len(data)-1)), 'RIGHT'),
                        ('BACKGROUND', (1, 0), (1, (len(data)-1)), colors.Color(.9, .9, .9)),
                        ('LINEBEFORE', (0, 0), (0, (len(data)-1)), 1, colors.saddlebrown),
                        ('LINEAFTER', (1, 0), (1, (len(data)-1)), 1, colors.saddlebrown),
                        ('BOTTOMPADDING', (0, 0), (1, (len(data)-1)), -4)
                        ]))
                    elements.append(t)
                starter += 1
            doc.build(elements)
            del cursor

#preparation()
#intersects()
pdf()
print "That's all folks!"