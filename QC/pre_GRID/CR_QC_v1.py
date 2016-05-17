__file__ = 'QC_v1'
__date__ = '6/2/14'
__author__ = 'ABREZNIC'
import os, arcpy, xlwt, datetime
#variables
county = "028"
txdotroads = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
subfiles = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
txdotcity = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.City\\TPP_GIS.APP_TPP_GIS_ADMIN.City"
txdotdist = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.District\\TPP_GIS.APP_TPP_GIS_ADMIN.District"
txdotcnty = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.County\\TPP_GIS.APP_TPP_GIS_ADMIN.County"
txdotmpo = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.MPO_Planning_Boundary\\TPP_GIS.APP_TPP_GIS_ADMIN.MPO_Planning_Boundary_2014"
txdotuza = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Urbanized_Areas_2000\\TPP_GIS.APP_TPP_GIS_ADMIN.Adjusted_Urbanized_Area_2000"

now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + "_" + curMonth + "_" + curDay
directory = "C:\\TxDOT\\QC\\CountyRoad\\Reports\\" + today + "_CR" + county
os.makedirs(directory)


def defaultsdict():
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

    print "Populate defaults..."
    defaults = default
    where = "SUBFILE = 2 AND COUNTY = " + county
    cursor = arcpy.UpdateCursor(subfiles, where)
    for row in cursor:
        id = str(row.RTE_ID)
        for fieldname in defaults.keys():
            value = row.getValue(fieldname)
            if value is None or value == "" or value == 0:
                row.setValue(fieldname, defaults[fieldname])
                cursor.updateRow(row)
        if row.getValue("ACR_GROUP") == "0":
            row.setValue("ACR_GROUP", defaults["ACR_GROUP"])
        cursor.updateRow(row)
    del cursor

def streetnames():
    names = {}
    where = "RTE_CLASS = '2' AND RTE_ID LIKE '" + str(county) + "A%'"
    cursor = arcpy.SearchCursor(txdotroads, where)
    for row in cursor:
        id = row.RTE_ID
        if id not in names.keys():
            names[id] = row.FULL_ST_NM
    del cursor
    where = "SUBFILE = 2 AND COUNTY = " + county
    cursor = arcpy.UpdateCursor(subfiles, where)
    for row in cursor:
        id = row.RTE_ID
        if id in names.keys():
            row.setValue("STREET_NAME", names[id])
        cursor.updateRow(row)
    del cursor

def districts():
    dist = {}
    cursor = arcpy.SearchCursor(txdotdist)
    for row in cursor:
        dist[row.DIST_NM] = row.DIST_NBR
    del cursor
    cnty_dist = {}
    cursor = arcpy.SearchCursor(txdotcnty)
    for row in cursor:
        cnty = str(row.CNTY_NBR)
        if len(cnty) == 2:
            cnty = "0" + cnty
        elif len(cnty) == 1:
            cnty = "00" + cnty
        name = row.DIST_NM
        if name in dist.keys():
            cnty_dist[cnty] = dist[name]
    del cursor
    return cnty_dist

def roadways():
    errors = []
    where = "RTE_CLASS = '2' AND RTE_ID LIKE '" + str(county) + "A%'"
    cursor = arcpy.SearchCursor(txdotroads, where)
    for row in cursor:
        id = row.RTE_ID
        if row.RTE_NM != id:
            errorinfo = []
            errorinfo.append(id)
            errorinfo.append(row.RTE_NM)
            errorinfo.append("")
            errorinfo.append("RTE_ID does not equal RTE_NM")
            errors.append(errorinfo)

        if len(row.RTE_NBR) == 3:
            cs = str(row.RTE_PRFX) + "0" + str(row.RTE_NBR)
        elif len(row.RTE_NBR) == 2:
            cs = str(row.RTE_PRFX) + "00" + str(row.RTE_NBR)
        elif len(row.RTE_NBR) == 1:
            cs = str(row.RTE_PRFX) + "000" + str(row.RTE_NBR)
        else:
            cs = str(row.RTE_PRFX) + str(row.RTE_NBR)

        if id[3:] != cs:
            errorinfo = []
            errorinfo.append(id)
            errorinfo.append(str(row.RTE_PRFX))
            errorinfo.append(str(row.RTE_NBR))
            errorinfo.append("RTE_ID does not equal RTE_PRFX and RTE_NBR")
            errors.append(errorinfo)

        if row.ST_PRFX is None:
            prfx = ""
        else:
            prfx = str(row.ST_PRFX)
        if row.ST_NM is None:
            stnm = ""
        else:
            stnm = str(row.ST_NM)
        if row.ST_SFX is None:
            sfx = ""
        else:
            sfx = str(row.ST_SFX)
        if row.ST_SFX_DIR is None:
            dir = ""
        else:
            dir = str(row.ST_SFX_DIR)
        fullname = prfx + " " + stnm + " " + sfx + " " + dir
        fixedname = fullname.strip()
        if row.FULL_ST_NM != fixedname:
            errorinfo = []
            errorinfo.append(id)
            errorinfo.append(row.FULL_ST_NM)
            errorinfo.append(fixedname)
            errorinfo.append("FULL_ST_NM does not equal composite name")
            errors.append(errorinfo)

        geom = row.shape
        ext = geom.extent
        Mmin = round(ext.MMin, 3)
        Mmax = round(ext.MMax, 3)
        Mdiff = abs(Mmax - Mmin)
        wholelen = geom.length * .000621371
        shp_len = round(wholelen, 3)
        rte_len = row.RTE_LEN

        errorinfo = []
        testlen = abs(shp_len - Mdiff)
        if rte_len is not None and id is not None:
            if testlen <= .003 and abs(rte_len - shp_len) > .003:
                print "RTE_LEN: " + str(id) + "," + str(rte_len) + "," + str(shp_len) + "," + str(Mdiff)
                errorinfo.append(id)
                errorinfo.append("MeasDiff: " + str(Mdiff))
                errorinfo.append("ShpLen: " + str(shp_len))
                errorinfo.append("RTE_LEN: " + str(rte_len))
                errors.append(errorinfo)
            elif abs(shp_len - Mdiff) > .003:
                errorinfo.append(id)
                errorinfo.append("MeasDiff: " + str(Mdiff))
                errorinfo.append("ShpLen: " + str(shp_len))
                errorinfo.append("RTE_LEN: " + str(rte_len))
                errors.append(errorinfo)
            elif abs(rte_len - Mdiff) > .003:
                errorinfo.append(id)
                errorinfo.append("MeasDiff: " + str(Mdiff))
                errorinfo.append("ShpLen: " + str(shp_len))
                errorinfo.append("RTE_LEN: " + str(rte_len))
                errors.append(errorinfo)
            elif abs(shp_len - rte_len) > .003:
                errorinfo.append(id)
                errorinfo.append("MeasDiff: " + str(Mdiff))
                errorinfo.append("ShpLen: " + str(shp_len))
                errorinfo.append("RTE_LEN: " + str(rte_len))
                errors.append(errorinfo)
            else:
                pass
        else:
            oid = str(row.OBJECTID)
            errorinfo.append("OID: " + oid)
            errorinfo.append("MeasDiff: " + str(Mdiff))
            errorinfo.append("ShpLen: " + str(shp_len))
            errorinfo.append("RTE_LEN: " + str(rte_len))
            errors.append(errorinfo)
    return errors

def urbanvalues():
    from arcpy import mapping
    arcpy.env.outputMFlag = "Disabled"
    arcpy.env.outputZFlag = "Disabled"
    routed = "routed"
    arcpy.MakeRouteEventLayer_lr(txdotroads, "RTE_ID", subfiles, "RTE_ID LINE BMP EMP", routed)
    lyr = mapping.Layer(routed)
    lyr.definitionQuery = """ "SUBFILE" = 2 AND "HIGHWAY_STATUS" = 4 AND "CONTROLSEC" NOT LIKE 'C%' AND "CONTROLSEC" NOT LIKE 'M%' AND "COUNTY" = """ + county
    urbanunion = directory + "\\UrbanUnion.shp"
    arcpy.Union_analysis([txdotcity, txdotcnty, txdotmpo, txdotuza], urbanunion)
    intersected = directory + "\\QC_UrbanOverlap.shp"
    arcpy.Intersect_analysis([lyr, urbanunion], intersected)
    arcpy.AddField_management(intersected, "Status", "TEXT")

    desc = arcpy.Describe(intersected)
    shapefieldname = desc.ShapeFieldName

    errors = []
    cursor = arcpy.UpdateCursor(intersected)
    for row in cursor:
        feat = row.getValue(shapefieldname)
        fixedlen = round((feat.length*.000621371), 3)
        if fixedlen <= .002:
            cursor.deleteRow(row)
        else:
            if row.TX_CITY_NB is None or row.TX_CITY_NB == "" or row.TX_CITY_NB == " ":
                ctynum = 0
            else:
                ctynum = int(row.TX_CITY_NB)
                print "ID: " + row.RTE_ID + "," + str(row.FID)
            if row.POP == row.POP_CD_1 and row.UAN == row.UZA_NBR and int(row.CENSUS_CIT) == ctynum and int(row.CENSUS_CIT) == 0 and row.MPA == row.MPO_NBR:
                cursor.deleteRow(row)
            elif row.POP == 1 and row.UAN == row.UZA_NBR and int(row.CENSUS_CIT) == ctynum and int(row.CENSUS_CIT) == 0 and row.MPA == row.MPO_NBR:
                if row.UAN == 0.0:
                    cursor.deleteRow(row)
                else:
                    row.setValue("LEN_OF_SEC", fixedlen)
                    cursor.updateRow(row)
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.POP)
                    errorinfo.append(row.POP_CD_1)
                    errorinfo.append("POP vs UAN Code Error")
                    errors.append(errorinfo)
            else:

                if row.POP != row.POP_CD_1:
                    if row.POP == 1:
                        if row.UAN == 0.0:
                            pass
                    else:
                        errorinfo = []
                        errorinfo.append(row.RTE_ID)
                        errorinfo.append(row.POP)
                        errorinfo.append(row.POP_CD_1)
                        errorinfo.append("POP Code Error")
                        errors.append(errorinfo)
                if row.UAN != row.UZA_NBR:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.UAN)
                    errorinfo.append(row.UZA_NBR)
                    errorinfo.append("UZA Number Error")
                    errors.append(errorinfo)
                if row.CENSUS_CIT != ctynum or ctynum != 0:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.CENSUS_CIT)
                    errorinfo.append(ctynum)
                    errorinfo.append("City Number Error")
                    errors.append(errorinfo)
                if row.MPA != row.MPO_NBR:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.MPA)
                    errorinfo.append(row.MPO_NBR)
                    errorinfo.append("MPO Number Error")
                    errors.append(errorinfo)

    del cursor
    return errors

def qc():
    print "Creating default dictionary..."
    defaultsdict()
    print "Populating Street Names..."
    streetnames()

    print "Creating QC Report..."
    book = xlwt.Workbook()
    #tabs
    distsheet = book.add_sheet("Districts")
    cssheet = book.add_sheet("Control Section")
    cntysheet = book.add_sheet("County Nbr")
    adminsheet = book.add_sheet("Admin_System")
    fcsheet = book.add_sheet("FC")
    measuresheet = book.add_sheet("Measures")
    roadsheet = book.add_sheet("TxDOT_Roadways")
    urbansheet = book.add_sheet("Urban Values")
    surfsheet = book.add_sheet("Surface Values")
    line = 0
    #page descriptions
    distsheet.write(line, 0, "District # vs County # Error")
    cssheet.write(line, 0, "Control Section Inconsistency")
    cntysheet.write(line, 0, "County # Inconsistency")
    adminsheet.write(line, 0, "Admin_System must be 3, 4, 7, or 8")
    fcsheet.write(line, 0, "FC field must be between 2-7")
    measuresheet.write(line, 0, "Measure Calculation Error")
    roadsheet.write(line, 0, "Errors within TxDOT_ROADWAYS")
    urbansheet.write(line, 0, "Urban Value vs SUBFILE Value Errors")
    surfsheet.write(line, 0, "Surface Value Errors")
    line += 1
    #headers
    distsheet.write(line, 0, "RTE_ID")
    distsheet.write(line, 1, "SUBFILE District")
    distsheet.write(line, 2, "Correct District")
    distsheet.write(line, 3, "OID")
    diline = line
    diline += 1

    cssheet.write(line, 0, "RTE_ID")
    cssheet.write(line, 1, "CONTROLSEC")
    cssheet.write(line, 2, "OID")
    cssheet.write(line, 3, "ID Control Section")
    csline = line
    csline += 1

    cntysheet.write(line, 0, "RTE_ID")
    cntysheet.write(line, 1, "COUNTY field")
    cntysheet.write(line, 2, "OID")
    cntyline = line
    cntyline += 1

    adminsheet.write(line, 0, "RTE_ID")
    adminsheet.write(line, 1, "Admin_System")
    adminsheet.write(line, 2, "OID")
    adminline = line
    adminline += 1

    fcsheet.write(line, 0, "FC field must be between 2-7")
    fcsheet.write(line, 1, "FC field must be between 2-7")
    fcsheet.write(line, 2, "FC field must be between 2-7")
    fcline = line
    fcline += 1

    measuresheet.write(line, 0, "RTE_ID")
    measuresheet.write(line, 1, "BMP")
    measuresheet.write(line, 2, "EMP")
    measuresheet.write(line, 3, "LEN_OF_SECTION")
    measuresheet.write(line, 4, "OID")
    msline = line
    msline += 1

    roadsheet.write(line, 0, "RTE_ID")
    roadsheet.write(line, 1, "Field")
    roadsheet.write(line, 2, "Field")
    roadsheet.write(line, 3, "Description/Field")
    rdline = line
    rdline += 1

    urbansheet.write(line, 0, "RTE_ID")
    urbansheet.write(line, 1, "SUBFILE Value")
    urbansheet.write(line, 2, "Urban Value")
    urbansheet.write(line, 3, "Description")
    ubline = line
    ubline += 1

    surfsheet.write(line, 0, "RTE_ID")
    surfsheet.write(line, 1, "SUBFILE Value")
    surfsheet.write(line, 2, "Default Value")
    surfsheet.write(line, 3, "Description")
    sfline = line
    sfline += 1

    distref = districts()
    thisdist = distref[county]
    cursor = arcpy.SearchCursor(subfiles, "SUBFILE = 2 AND COUNTY = " + county)
    for row in cursor:
        oid = str(row.OBJECTID)
        id = row.RTE_ID
        idcnty = id[:3]
        idcs = id[3:]

        if len(str(row.COUNTY)) == 3:
            cnty = str(row.COUNTY)
        elif len(str(row.COUNTY)) == 2:
            cnty = "0" + str(row.COUNTY)
        elif len(str(row.COUNTY)) == 1:
            cnty = "00" + str(row.COUNTY)
        else:
            cntysheet.write(line, 0, id)
            cntysheet.write(line, 1, cnty)
            cntysheet.write(line, 2, oid)
            cntyline += 1

        if row.DISTRICT != thisdist:
            distsheet.write(diline, 0, id)
            distsheet.write(diline, 1, str(row.DISTRICT))
            distsheet.write(diline, 2, thisdist)
            distsheet.write(diline, 3, oid)
            diline += 1
        if idcs != row.CONTROLSEC:
            cssheet.write(csline, 0, id)
            cssheet.write(csline, 1, str(row.CONTROLSEC))
            cssheet.write(csline, 2, oid)
            cssheet.write(csline, 3, idcs)
            csline += 1
        if cnty != idcnty:
            cntysheet.write(cntyline, 0, id)
            cntysheet.write(cntyline, 1, cnty)
            cntysheet.write(cntyline, 2, oid)
            cntyline += 1
        if row.ADMIN_SYSTEM != 2:
            adminsheet.write(adminline, 0, id)
            adminsheet.write(adminline, 1, str(row.ADMIN_SYSTEM))
            adminsheet.write(adminline, 2, oid)
            adminline += 1
        fclist = [2, 3, 4, 5, 6, 7]
        if row.FC not in fclist:
            fcsheet.write(fcline, 0, id)
            fcsheet.write(fcline, 1, str(row.FC))
            fcsheet.write(fcline, 2, oid)
            fcline += 1
        if abs(abs(row.EMP - row.BMP) - row.LEN_OF_SECTION) > .001:
            measuresheet.write(msline, 0, id)
            measuresheet.write(msline, 1, str(row.BMP))
            measuresheet.write(msline, 2, str(row.EMP))
            measuresheet.write(msline, 3, str(row.LEN_OF_SECTION))
            measuresheet.write(msline, 4, oid)
            msline += 1
        surfdict = {}
        surfdict[10] = [30, 16, 0, 16]
        surfdict[32] = [30, 18, 0, 16]
        surfdict[51] = [40, 20, 2, 18]
        surfdict[55] = [40, 22, 4, 20]
        surfdict[61] = [40, 24, 1, 24]
        if row.SURFACE_TYPE not in surfdict.keys():
            surfsheet.write(sfline, 0, id)
            surfsheet.write(sfline, 1, row.SURFACE_TYPE)
            surfsheet.write(sfline, 2, 32)
            surfsheet.write(sfline, 3, "Surface must be 10, 32, 51, 55, or 61")
            sfline += 1
        if row.ROADBED_WIDTH > row.ROW:
            surfsheet.write(sfline, 0, id)
            surfsheet.write(sfline, 1, row.ROADBED_WIDTH)
            surfsheet.write(sfline, 2, "ROW:" + surfdict[row.SURFACE_TYPE][0])
            surfsheet.write(sfline, 3, "ROADBED_WIDTH must be < ROW")
            sfline += 1
        if row.SURFACE_WIDTH > row.ROADBED_WIDTH:
            surfsheet.write(sfline, 0, id)
            surfsheet.write(sfline, 1, row.SURFACE_WIDTH)
            surfsheet.write(sfline, 2, "RDBD:" + str(surfdict[row.SURFACE_TYPE][1]))
            surfsheet.write(sfline, 3, "SURFACE_WIDTH must be < ROADBED_WIDTH")
            sfline += 1
        if row.BASE_TYPE > 4 or row.BASE_TYPE < 0:
            surfsheet.write(sfline, 0, id)
            surfsheet.write(sfline, 1, row.BASE_TYPE)
            surfsheet.write(sfline, 2, surfdict[row.SURFACE_TYPE][2])
            surfsheet.write(sfline, 3, "BASE_TYPE must be between 0 and 4")
            sfline += 1
        if row.ROW <= 0:
            surfsheet.write(sfline, 0, id)
            surfsheet.write(sfline, 1, row.ROW)
            surfsheet.write(sfline, 2, surfdict[row.SURFACE_TYPE][0])
            surfsheet.write(sfline, 3, "ROW must be > 0")
            sfline += 1
        if row.ROADBED_WIDTH <= 0:
            surfsheet.write(sfline, 0, id)
            surfsheet.write(sfline, 1, row.ROADBED_WIDTH)
            surfsheet.write(sfline, 2, surfdict[row.SURFACE_TYPE][1])
            surfsheet.write(sfline, 3, "ROADBED_WIDTH must be > 0")
            sfline += 1
        if row.SURFACE_WIDTH <= 0:
            surfsheet.write(sfline, 0, id)
            surfsheet.write(sfline, 1, row.ROADBED_WIDTH)
            surfsheet.write(sfline, 2, surfdict[row.SURFACE_TYPE][3])
            surfsheet.write(sfline, 3, "SURFACE_WIDTH must be > 0")
            sfline += 1

    print "Finding Roadways Errors..."
    roaderrors = roadways()
    for i in roaderrors:
        roadsheet.write(rdline, 0, i[0])
        roadsheet.write(rdline, 1, i[1])
        roadsheet.write(rdline, 2, i[2])
        roadsheet.write(rdline, 3, i[3])
        rdline += 1

    print "Finding urban value errors..."
    urbanerrors = urbanvalues()
    for i in urbanerrors:
        urbansheet.write(ubline, 0, i[0])
        urbansheet.write(ubline, 1, i[1])
        urbansheet.write(ubline, 2, i[2])
        urbansheet.write(ubline, 3, i[3])
        ubline += 1

    #assemble and save
    book.save(directory + "\\CR" + county + "_ErrorReport_" + today + ".xls")





qc()


print "that's all folks."