__file__ = 'CountyMapbook_vJ2'
__date__ = '6/18/2014'
__author__ = 'ABREZNIC'
import os, arcpy,datetime
from arcpy import env

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

parks = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Park\\TPP_GIS.APP_TPP_GIS_ADMIN.Public_Lands_2014"
cemeteries = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Cemetery\\TPP_GIS.APP_TPP_GIS_ADMIN.Cemetery"
cemeteriesPT = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Cemetery\\TPP_GIS.APP_TPP_GIS_ADMIN.Cemetery_Points"
roads = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
cntyfedroads = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.Map_County_Mapbook\\TPP_GIS.APP_TPP_GIS_ADMIN.CMB_Roadways_2014"
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
grid = "T:\\DATAMGT\\MAPPING\\Mapping Products\\CountyMapbook\\Calendar year 2014\\District Grids\\State_Grid_120K.shp"
tollroads = "T:\\DATAMGT\\MAPPING\\Mapping Products\\CountyMapbook\\Calendar year 2014\\Tollroads\\Tollroads.shp"

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

    print "Copying parks..."
    arcpy.Select_analysis(parks, database + "\\parks", "(GOVT_JURIS = '3' OR GOVT_JURIS = '4' OR EDIT_NM = 'JLS') AND LAND_NM <> '' AND LAND_NM IS NOT NULL")
    print "Copying cemeteries..."
    arcpy.Select_analysis(cemeteries, database + "\\cemetery", "EDIT_NM <> 'Off'")
    arcpy.Select_analysis(cemeteriesPT, database + "\\cemetery_point", "CEMETERY_NM IS NOT NULL AND CEMETERY_NM <> ''")
    print "Copying highways..."
    arcpy.Select_analysis(roads, database + "\\highways", "(((RTE_CLASS = '1' OR RTE_CLASS = '6') AND RDBD_TYPE = 'KG') and RTE_OPEN <> 0 ) OR ((RTE_NM ='SL0008' AND RDBD_TYPE = 'KG') and RTE_OPEN <> 0)")
    print "Copying counties..."
    arcpy.Copy_management(counties, database + "\\counties")
    print "Copying airports..."
    arcpy.Select_analysis(airports, database + "\\airports", "ARPRT_NM <> '' AND ARPRT_NM IS NOT NULL")
    arcpy.Select_analysis(airportsPT, database + "\\airports_point", "DISPLAY = 'Yes'")
    print "Copying county roads..."
    arcpy.Select_analysis(cntyfedroads, database + "\\countyroads", "RTE_CLASS = '2' AND RDBD_TYPE = 'KG'")
    print "Copying prisons..."
    arcpy.Copy_management(prisons, database + "\\prison")
    print "Copying military..."
    arcpy.Copy_management(military, database + "\\military")
    print "Copying schools..."
    arcpy.Copy_management(schools, database + "\\school")
    print "Copying cities..."
    arcpy.Copy_management(cities, database + "\\cities")
    arcpy.Select_analysis(citiesPT, database + "\\cities_point", "INC = 'N'")
    print "Copying lakes..."
    arcpy.Select_analysis(lakes, database + "\\lakes", "BODY_TYPE <> 3 AND BODY_NM <> '' AND BODY_NM IS NOT NULL")
    print "Copying railroads..."
    arcpy.Select_analysis(railroads, database + "\\railroad", "RR_TYPE = 'M' AND RR_STAT = 'A'")
    print "Fixing railroad names..."
    names = {}
    cursor = arcpy.SearchCursor("T:\\DATAMGT\\MAPPING\\Railroad\\Domain.dbf")
    for row in cursor:
        curnum = row.domainTXT
        names[curnum] = row.domainNM
    del cursor
    del row
    arcpy.AddField_management(database + "\\railroad", "new_name", "TEXT", "", "", 100)
    cursor = arcpy.UpdateCursor(database + "\\railroad")
    for row in cursor:
        curname = str(row.RR_NM)
        if curname in names.keys():
            row.setValue("new_name", names[curname])
        else:
            row.setValue("new_name", row.RR_NM)
        cursor.updateRow(row)
    del cursor
    del row
    print "Copying rivers..."
    arcpy.Select_analysis(rivers, database + "\\rivers", "STRM_TYPE = '1' AND STRM_NM <> '' AND STRM_NM IS NOT NULL")
    print "Copying federal roads..."
    arcpy.Select_analysis(cntyfedroads, database + "\\federal", "RTE_CLASS = '7' AND RDBD_TYPE = 'KG' AND FULL_ST_NM <> ''")
    print "Copying tollroads..."
    arcpy.FeatureClassToFeatureClass_conversion(tollroads, database, "tollroads")
    print "Copying grid..."
    arcpy.FeatureClassToFeatureClass_conversion(grid, database, "grid")
    # arcpy.Copy_management(grid, database + "\\grid")
    # #
    # print "Renumbering grid..."
    # cursor = arcpy.UpdateCursor(database + "\\grid")
    # for row in cursor:
    #     row.setValue("ID", row.ID - 66)
    #     row.setValue("STATE_ID", row.STATE_ID - 66)
    #     if row.NORTH != 0:
    #         row.setValue("NORTH", row.NORTH - 66)
    #     if row.SOUTH != 0:
    #         row.setValue("SOUTH", row.SOUTH - 66)
    #     if row.EAST != 0:
    #         row.setValue("EAST", row.EAST - 66)
    #     if row.WEST != 0:
    #         row.setValue("WEST", row.WEST - 66)
    #     cursor.updateRow(row)
    # del cursor
    # del row
    print "Creating union..."
    arcpy.Union_analysis([database + "\\grid", database + "\\counties"], database + "\\union")
    cursor = arcpy.UpdateCursor(database + "\\union")
    for row in cursor:
        if row.CNTY_NM == "" or row.CNTY_NM is None or row.STATE_ID == 0:
            cursor.deleteRow(row)
    del cursor
    del row

def intersects():
    env.workspace = database
    print "Creating field dictionary..."
    dict = {}
    dict["parks"] = "LAND_NM"
    dict["cemetery"] = "CEMETERY_NM"
    dict["cemetery_point"] = "CEMETERY_NM"
    dict["highways"] = "FULL_ST_NM"
    dict["counties"] = "CNTY_NM"
    dict["airports"] = "ARPRT_NM"
    dict["airports_point"] = "ARPRT_NM"
    dict["countyroads"] = "FULL_ST_NM"
    dict["prison"] = "PRISON_NM"
    dict["military"] = "BASE_NM"
    dict["school"] = "SCHOOL_NM"
    dict["cities"] = "CITY_NM"
    dict["cities_point"] = "CITY_NM"
    dict["lakes"] = "BODY_NM"
    dict["railroad"] = "new_name"
    dict["rivers"] = "STRM_NM"
    dict["federal"] = "FULL_ST_NM"
    dict["tollroads"] = "ALT_NAME"

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
                row.setValue("UNIQUE", str(row.STATE_ID) + row.CNTY_NM + value)
                cursor.updateRow(row)
            del cursor
            del row
            arcpy.Statistics_analysis(fc, dictname + "_SUMMARIZED", [["STATE_ID", "MIN"], ["CNTY_NM", "FIRST"], [dict[dictname], "FIRST"]], ["UNIQUE"])
    print "Merging with point tables..."
    arcpy.Merge_management(["cemetery_SUMMARIZED", "cemetery_point_SUMMARIZED"], "cemetery_all_SUMMARIZED")
    arcpy.Merge_management(["airports_SUMMARIZED", "airports_point_SUMMARIZED"], "airports_all_SUMMARIZED")
    arcpy.Merge_management(["cities_SUMMARIZED", "cities_point_SUMMARIZED"], "cities_all_SUMMARIZED")
    print "Renaming tables..."
    arcpy.Rename_management("cemetery_SUMMARIZED", "cemetery_SUMpreMERGE")
    arcpy.Rename_management("cemetery_point_SUMMARIZED", "cemetery_point_SUMpreMERGE")
    arcpy.Rename_management("airports_SUMMARIZED", "airports_SUMpreMERGE")
    arcpy.Rename_management("airports_point_SUMMARIZED", "airports_point_SUMpreMERGE")
    arcpy.Rename_management("cities_SUMMARIZED", "cities_SUMpreMERGE")
    arcpy.Rename_management("cities_point_SUMMARIZED", "cities_point_SUMpreMERGE")

def merge():
    env.workspace = database
    env.overwriteOutput = True
    print "Copying mdb..."
    newDbase = "T:\\DATAMGT\\MAPPING\\Mapping Products\\CountyMapbook\\Calendar year 2014\\Feature Indicies\\Working\\2014_INDEXS_Geodatabase"+today+".mdb"
    arcpy.Copy_management("T:\\DATAMGT\\MAPPING\\Mapping Products\\CountyMapbook\\Calendar year 2014\\Feature Indicies\\Working\\2014_INDEXS_Geodatabase.mdb", newDbase)
    print "Overwriting tables..."
    tList = arcpy.ListTables()
    for table in tList:
        if table.split("_")[-1] == "SUMMARIZED":
            name = table.split("_")[0]
            print name
            capname = name.title()
            arcpy.Copy_management(table, newDbase + "\\" + capname)



preparation()
intersects()
merge()
print "That's all folks!"
