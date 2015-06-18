__file__ = 'BlanksCleanUp_v2'
__date__ = '3/10/14'
__author__ = 'ABREZNIC'

import arcpy


routeList = []
blanks = "C:\\TxDOT\\_Subfile Validations\\EOY\\2014\\blanks.dbf"
cursor = arcpy.SearchCursor(blanks)
for row in cursor:
    route = str(row.RTE_ID)
    if route not in routeList:
        routeList.append(route)
        print route
del cursor
print "route list created"


default = {}
#default["AADT_Combination"] = 0
#default["AADT_Single_Unit"] = 0
default["ACR_GROUP"] = "0000"
default["ADT_CURRENT"] = 85
default["ADT_YEAR"] = 1978
default["ADT_YEAR1"] = 0
default["ADT_YEAR2"] = 0
default["ADT_YEAR3"] = 0
default["ADT_YEAR4"] = 0
default["ADT_YEAR5"] = 0
default["ADT_YEAR6"] = 0
default["ADT_YEAR7"] = 0
default["ADT_YEAR8"] = 0
default["ADT_YEAR9"] = 0
default["ATHWLDHUN"] = 0
default["ATHWLDTAN"] = 0
#default["BEGIN_TERMINI"] = 0
default["BLANK"] = "0"
default["CENSUS_CITY"] = 0
default["COMBO_ADT"] = 1.4
default["COMBO_DHV"] = 1
#default["CONTROLSEC"] =
default["DESIGN_HOUR"] = 0
default["DIR_DIST"] = 60
#default["END_TERMINI"] = 0
default["ESTIMATED_VEH"] = 0
default["FAP"] = 0
default["FC"] = 7
default["FILLER"] = 0
default["FILLER2"] = 0
default["FILLER3"] = 0
default["FILLER4"] = 0
default["FILLER5"] = 0
default["FILLER6"] = 0
default["FLEX"] = 0
default["FUTURE_ADT"] = 0
default["FUTURE_YEAR"] = 0
default["HIGHWAY_NUMBER"] = 0
default["HIGHWAY_SUFFIX"] = 0
default["HIGHWAY_SYSTEM"] = 0
default["HP"] = 0
default["HPMS_CUR_SECTION"] = 0
default["INCREASE_FACTOR"] = 0
default["K_FACTOR"] = 10.2
default["LOAD_LIMIT"] = 0
default["MAINTENANCE_CLASS"] = 0
default["MAINTENANCE_SECTION"] = 0
default["MILEPOINT_DATE"] = 200901
default["MPA"] = 0
default["NHS"] = 0
default["POP"] = 1
default["RESERVATION"] = 0
default["RIGID"] = 0
default["SHOULDER_TYPE"] = 0
default["SINGLE_ADT"] = 1.8
default["SINGLE_DHV"] = 1.4
default["SPECIAL_SYSTEMS"] = 0
#default["STREET_NAME"] = 0
default["TOLL"] = 0
default["TRUCK_AXLE_FACTOR"] = 0
default["TRUCK_ROUTE"] = 0
default["TRUCKS_IN_AADT"] = 3.2
default["TRUCKS_IN_DHV"] = 2.4
default["UAN"] = 0
default["VEHICLE_MILES_DAILY"] = 0
#default["HPMSID"] = 0
print "default dictionary created"

subfiles = "Database Connections\\Direct_Comanche.sde\\TPP_GIS.MCHAMB1.SUBFILES"
#where = """ ADMIN_SYSTEM = 8 """
cursor = arcpy.UpdateCursor(subfiles)
for row in cursor:
    rte = str(row.RTE_ID)
    if rte in routeList:
        print rte
        for fieldname in default.keys():
            value = row.getValue(fieldname)
            if value == None or value == "" or value == 0:
                print fieldname
                row.setValue(fieldname, default[fieldname])
                cursor.updateRow(row)
        if row.getValue("ACR_GROUP") == "0":
            row.setValue("ACR_GROUP", default["ACR_GROUP"])
            print "ACR_GROUP updated"
        cursor.updateRow(row)
        print rte
del cursor



print "all done."

