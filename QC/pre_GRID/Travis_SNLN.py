__date__ = '5/29/14'
__author__ = 'ABREZNIC'

import os, arcpy, xlwt, datetime, math, multiprocessing, shutil, smtplib, base64, sys

# date
now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + "_" + curMonth + "_" + curDay
runday = now.strftime("%B") + " " + curDay + ", " + curYear

check0 = "C:\\TxDOT\\QC\\ErrorChecks"
allchecks = "false"
cityoverlaps = "false"
routeopens = "false"
offgeommeas = "false"
sublen = "false"
multimeasPNG = "false"
onattmeas = "false"
offatt = "false"
scnln = "true"
offsystoll = "false"
federalrds = "false"

qcfolder = check0
workspace = qcfolder + "\\ScreenLines" + today
where = """ ( RDBD_TYPE = 'CNCTR-GS' AND RTE_CLASS = '1' ) OR( (RTE_CLASS = '2' OR RTE_CLASS = '3') AND RDBD_TYPE = 'KG' ) OR RTE_CLASS = '6' OR RTE_CLASS = '7' """
whereto = """ ( RDBD_TYPE = 'CNCTR-GS' AND RTE_CLASS = '1' ) OR( (RTE_CLASS = '2' OR RTE_CLASS = '3' OR RTE_CLASS = '6' OR RTE_CLASS = '7') AND RDBD_TYPE <> 'CONNECTOR' AND RDBD_TYPE <> 'OTHER' AND RDBD_TYPE <> 'RAMP' AND RDBD_TYPE <> 'TURNAROUND' )  """
database = workspace + "\\Comanche_Copy.gdb"
roadways = database + "\\TXDOT_Roadways"
subfiles = database + "\\SUBFILES"
cities = database + "\\City"
districts = database + "\\District"
tolls = database + "\\RTE_TOLL"
disterrors = []

if not os.path.exists(workspace):
    os.makedirs(workspace)

txdotroads = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
txdotsubs = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
txdotcity = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.City\\TPP_GIS.APP_TPP_GIS_ADMIN.City"
txdotdist = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.District\\TPP_GIS.APP_TPP_GIS_ADMIN.District"
cityexcept = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.ERRCHKS_CITY_OVERLAP"
tolltable = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.RTE_TOLL"

def copylocal():
    arcpy.AddMessage("Copying data local...")
    arcpy.CreateFileGDB_management(workspace, "Comanche_Copy.gdb")
    arcpy.TableToTable_conversion(txdotsubs, database, "SUBFILES")
    arcpy.AddMessage("Subfiles copied.")
    arcpy.TableToTable_conversion(tolltable, database, "RTE_TOLL")
    arcpy.AddMessage("Toll table copied.")
    arcpy.Copy_management(txdotcity, cities)
    arcpy.AddMessage("Cities copied.")
    arcpy.Copy_management(txdotdist, districts)
    arcpy.AddMessage("Districts copied.")
    arcpy.SpatialJoin_analysis(txdotroads, districts, roadways)
    arcpy.AddMessage("Roadways copied.")


def overlap():
    arcpy.AddMessage("Starting city overlap check...")
    arcpy.CreateFileGDB_management(workspace, "Overlap_Working.gdb")
    dbase = workspace + "\\Overlap_Working.gdb"
    from arcpy import env
    env.workspace = dbase
    arcpy.env.outputMFlag = "Disabled"
    overlaproads = "OverlapRoads"
    print "City Overlap Errors (1/9): Spatial Join Roads and Cities"
    arcpy.SpatialJoin_analysis(roadways, cities, overlaproads)
    print "City Overlap Errors (2/9): Finding FC Streets"
    arcpy.Select_analysis(overlaproads, "FC_Streets", """ RTE_CLASS = '3' """)
    print "City Overlap Errors (3/9): Removing correct FC Streets"
    arcpy.Erase_analysis("FC_Streets", cities, "FC_Streets_Errors")
    print "City Overlap Errors (4/9): Clipping city roads"
    arcpy.Clip_analysis(overlaproads, cities, "City_Roads")
    print "City Overlap Errors (5/9): Finding County Roads in the Cities"
    arcpy.Select_analysis("City_Roads", "County_Roads_Errors", """ RTE_CLASS = '2' """)
    print "City Overlap Errors (6/9): Compiling Errors"
    arcpy.Merge_management(["County_Roads_Errors", "FC_Streets_Errors"],
                           "MergedErrors")
    print "City Overlap Errors (7/9): Applying District Numbers"
    arcpy.SpatialJoin_analysis("MergedErrors", districts, "City_OverlapErrors")
    print "City Overlap Errors (8/9): Finalizing Errors"
    exceptions = {}
    cursor = arcpy.SearchCursor(cityexcept)
    for row in cursor:
        exceptions[row.RTE_ID] = [row.CITY, row.EXCEPTION]
    del cursor
    del row

    errors = []
    cursor = arcpy.UpdateCursor("City_OverlapErrors")
    counter = 0
    for row in cursor:
        geom = row.shape
        len = geom.length * .000621371
        if len < .003:
            cursor.deleteRow(row)
        else:
            row.setValue("RTE_LEN", len)
            cursor.updateRow(row)
            if row.RTE_ID in exceptions.keys():
                values = exceptions[row.RTE_ID]
                cex = values[0]
                eex = values[1]
                thediff = abs(len - eex)
                citynbr = int(row.TX_CITY_NBR)
                if citynbr != cex or thediff > .003:
                    rowinfo = [row.RTE_ID, row.RTE_LEN, row.DIST_NM, row.DIST_NBR, row.CITY_NM, row.TX_CITY_NBR]
                    errors.append(rowinfo)
                    counter += 1
            else:
                rowinfo = [row.RTE_ID, row.RTE_LEN, row.DIST_NM, row.DIST_NBR, row.CITY_NM, row.TX_CITY_NBR]
                errors.append(rowinfo)
                counter += 1
    del row
    del cursor
    print "City Overlap Errors (9/9): Creating Shapefile"
    arcpy.FeatureClassToShapefile_conversion("City_OverlapErrors", workspace)
    arcpy.AddMessage(str(counter) + " overlap errors.")
    return errors


def routeopen():
    arcpy.AddMessage("Starting route open check...")
    errors = []
    openstatus = {}
    counter = 0
    cursor = arcpy.SearchCursor(roadways, whereto)
    for row in cursor:
        id = row.RTE_ID
        if id is not None and id != "":
            open = str(row.RTE_OPEN)
            length = row.RTE_LEN
            key = id + "=" + open
            try:
                if key not in openstatus.keys():
                    openstatus[key] = length
                else:
                    openstatus[key] = openstatus[key] + length
            except:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(str(open))
                errorinfo.append(str(length))
                errorinfo.append("Bad value RTE_OPEN or RTE_LEN field.")
                errorinfo.append(row.DIST_NBR)
                errors.append(errorinfo)
                counter += 1
        else:
            errorinfo = []
            oid = str(row.OBJECTID)
            errorinfo.append("OID: " + oid)
            errorinfo.append("N/A")
            errorinfo.append("N/A")
            errorinfo.append("BAD RTE_ID")
            errorinfo.append(row.DIST_NBR)
            errors.append(errorinfo)
            counter += 1
    arcpy.AddMessage(str(counter) + " null/bad RouteID errors.")
    del cursor
    counter = 0
    hwystatus = {}
    cursor = arcpy.SearchCursor(subfiles, "SUBFILE <> 4 AND SUBFILE <> 5")
    for row in cursor:
        id = row.RTE_ID
        if id is not None and id != "":
            length = row.LEN_OF_SECTION
            status = row.HIGHWAY_STATUS
            if status == 4 or status == 1:
                thiskey = id + "=" + str(1)
                if thiskey in openstatus.keys():
                    if thiskey in hwystatus:
                        hwystatus[thiskey] = hwystatus[thiskey] + length
                    else:
                        hwystatus[thiskey] = length
                else:
                    errorinfo = []
                    errorinfo.append(id)
                    errorinfo.append("N/A")
                    errorinfo.append(status)
                    errorinfo.append("RTE_ID has SUBFILES with status which does not match TxDOT_Roadways' RTE_OPEN")
                    errorinfo.append(row.DISTRICT)
                    errors.append(errorinfo)
                    counter += 1
            elif status == 0:
                thiskey = id + "=" + str(0)
                if thiskey in openstatus.keys():
                    if thiskey in hwystatus:
                        hwystatus[thiskey] = hwystatus[thiskey] + length
                    else:
                        hwystatus[thiskey] = length
                else:
                    errorinfo = []
                    errorinfo.append(id)
                    errorinfo.append("N/A")
                    errorinfo.append(status)
                    errorinfo.append("RTE_ID has SUBFILES with status which does not match TxDOT_Roadways' RTE_OPEN")
                    errorinfo.append(row.DISTRICT)
                    errors.append(errorinfo)
                    counter += 1
            else:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append("N/A")
                errorinfo.append(status)
                errorinfo.append("HIGHWAY_STATUS must be 0 or 4")
                errorinfo.append(row.DISTRICT)
                errors.append(errorinfo)
                counter += 1
        else:
            errorinfo = []
            errorinfo.append(id)
            errorinfo.append(row.COUNTY)
            errorinfo.append(row.CONTROLSEC)
            errorinfo.append("RTE_ID is NULL. Look up this COUNTY and CONTROLSEC in SUBFILES")
            errorinfo.append(row.DISTRICT)
            errors.append(errorinfo)
            counter += 1
    del cursor
    for key in openstatus.keys():
        if key in hwystatus.keys():
            linelen = openstatus[key]
            sublen = hwystatus[key]
            id = key.split("=")[0]
            open = key.split("=")[1]
            if abs(linelen - sublen) > .004:
                cursor = arcpy.SearchCursor(subfiles, "RTE_ID = '" + id + "'")
                for row in cursor:
                    Dist_Num = row.DISTRICT
                try:
                    errorinfo = []
                    errorinfo.append(id)
                    errorinfo.append(open)
                    errorinfo.append("N/A")
                    errorinfo.append("Length error. SUBFILES LEN_OF_SECTIONS does not match ROADWAYS Route_Length")
                    errorinfo.append(Dist_Num)
                    errors.append(errorinfo)
                except:
                    errorinfo = []
                    errorinfo.append(id)
                    errorinfo.append(open)
                    errorinfo.append("N/A")
                    errorinfo.append("RTE_ID does not exist in SUBFILES")
                    errorinfo.append(Dist_Num)
                    errors.append(errorinfo)
                    arcpy.AddMessage("check out: " + str(id))
                counter += 1
            else:
                pass
        else:
            id = key.split("=")[0]
            open = key.split("=")[1]
            cursor = arcpy.SearchCursor(roadways, "RTE_ID = '" + id + "'")
            for row in cursor:
                Dist_Num = row.DIST_NBR
            try:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(open)
                errorinfo.append("N/A")
                errorinfo.append("RTE_ID in TxDOT_Roadways with this RTE_OPEN does not match SUBFILES' HIGHWAY_STATUS")
                errorinfo.append(Dist_Num)
                errors.append(errorinfo)
            except:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(open)
                errorinfo.append("N/A")
                errorinfo.append("RTE_ID does not exist in SUBFILES")
                errorinfo.append(Dist_Num)
                errors.append(errorinfo)
                arcpy.AddMessage("check out: " + str(id))
            counter += 1
    arcpy.AddMessage(str(counter) + " subfile vs roadways Route Open errors.")
    return errors


def measurelength():
    arcpy.AddMessage("Starting off-system geometry check...")
    counter = 0
    cursor = arcpy.SearchCursor(roadways, whereto)
    errors = []
    for row in cursor:
        errorinfo = []
        id = row.RTE_ID
        geom = row.shape
        ext = geom.extent
        Mmin = round(ext.MMin, 3)
        Mmax = round(ext.MMax, 3)
        Mdiff = abs(Mmax - Mmin)
        wholelen = geom.length * .000621371
        shp_len = float(format(float(wholelen), '.3f'))
        rte_len = row.RTE_LEN

        testlen = abs(shp_len - Mdiff)
        if rte_len is not None and id is not None:
            if row.DIST_NBR != "" and row.DIST_NBR is not None:
                if testlen <= .003 and abs(rte_len - shp_len) > .003:
                    oid = str(row.OBJECTID)
                    # arcpy.AddMessage(
                    #     "RTE_LEN replaced: " + str(oid) + "," + str(rte_len) + "," + str(shp_len) + "," + str(Mdiff))
                    # cur = arcpy.UpdateCursor(txdotroads, "OBJECTID = " + oid)
                    # for i in cur:
                    #     i.setValue("RTE_LEN", wholelen)
                    #     cur.updateRow(i)
                    errorinfo.append(id)
                    errorinfo.append(Mdiff)
                    errorinfo.append(shp_len)
                    errorinfo.append(rte_len)
                    errorinfo.append(row.DIST_NM)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(abs(rte_len - shp_len))
                    errors.append(errorinfo)
                    counter += 1
                elif abs(shp_len - Mdiff) > .003:
                    errorinfo.append(id)
                    errorinfo.append(Mdiff)
                    errorinfo.append(shp_len)
                    errorinfo.append(rte_len)
                    errorinfo.append(row.DIST_NM)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(abs(shp_len - Mdiff))
                    errors.append(errorinfo)
                    counter += 1
                elif abs(rte_len - Mdiff) > .003:
                    errorinfo.append(id)
                    errorinfo.append(Mdiff)
                    errorinfo.append(shp_len)
                    errorinfo.append(rte_len)
                    errorinfo.append(row.DIST_NM)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(abs(rte_len - Mdiff))
                    errors.append(errorinfo)
                    counter += 1
                elif abs(shp_len - rte_len) > .003:
                    errorinfo.append(id)
                    errorinfo.append(Mdiff)
                    errorinfo.append(shp_len)
                    errorinfo.append(rte_len)
                    errorinfo.append(row.DIST_NM)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(abs(shp_len - rte_len))
                    errors.append(errorinfo)
                    counter += 1
                else:
                    pass
            else:
                arcpy.AddMessage("district issue with RTE_ID: " + id)
                errorinfo.append(id)
                errorinfo.append(Mdiff)
                errorinfo.append(shp_len)
                errorinfo.append(rte_len)
                errorinfo.append("Dist Number Issue, geometry outside of district boundary.")
                errorinfo.append(0)
                errorinfo.append(abs(shp_len - Mdiff))
                errors.append(errorinfo)
                counter += 1
        else:
            oid = str(row.OBJECTID)
            errorinfo.append("OID: " + oid)
            errorinfo.append(str(Mdiff))
            errorinfo.append(str(shp_len))
            errorinfo.append(str(rte_len))
            errorinfo.append(row.DIST_NM)
            errorinfo.append(row.DIST_NBR)
            errorinfo.append("")
            errors.append(errorinfo)
            counter += 1
    arcpy.AddMessage(str(counter) + " measure length errors.")
    del cursor
    del row
    return errors


def roadwaydict():
    errors = []
    counter = 0
    arcpy.AddMessage("...creating subfile length dictionary...")
    dictionary = {}
    cursor = arcpy.SearchCursor(roadways, whereto)
    for row in cursor:
        id = row.RTE_ID
        if row.RTE_LEN is not None:
            len = row.RTE_LEN
        else:
            len = 0
            oid = str(row.OBJECTID)
            errorinfo = []
            errorinfo.append(id)
            errorinfo.append(row.DIST_NBR)
            errorinfo.append("")
            errorinfo.append(Mmin)
            errorinfo.append("")
            errorinfo.append(Mmax)
            errorinfo.append("")
            errorinfo.append(len)
            errorinfo.append("NO RTE_LEN POPULATED. OBJECTID: " + oid)
            errors.append(errorinfo)
            counter += 1
        geom = row.shape
        ext = geom.extent
        try:
            Mmin = float(format(float(ext.MMin), '.3f'))
            Mmax = float(format(float(ext.MMax), '.3f'))
            if id not in dictionary.keys() and id is not None:
                dictionary[str(id)] = [len, Mmin, Mmax]
            elif id in dictionary.keys() and id is not None:
                currentrecord = dictionary[id]
                currentlength = currentrecord[0]
                currentmin = currentrecord[1]
                currentmax = currentrecord[2]
                newlen = currentlength + len
                if Mmin < currentmin:
                    currentmin = Mmin
                if Mmax > currentmax:
                    currentmax = Mmax
                dictionary[str(id)] = [newlen, currentmin, currentmax]
            else:
                oid = str(row.OBJECTID)
                errorinfo = []
                errorinfo.append("OBJECTID: " + oid)
                errorinfo.append("")
                errorinfo.append("")
                errorinfo.append(Mmin)
                errorinfo.append("")
                errorinfo.append(Mmax)
                errorinfo.append("")
                errorinfo.append(len)
                errorinfo.append("NO ROUTE ID. OBJECTID: " + oid)
                errors.append(errorinfo)
                counter += 1
        except:
            errorinfo = []
            errorinfo.append(id)
            errorinfo.append(row.DIST_NBR)
            errorinfo.append("")
            errorinfo.append(ext.MMin)
            errorinfo.append("")
            errorinfo.append(ext.MMax)
            errorinfo.append("")
            errorinfo.append(len)
            errorinfo.append("Error with Min/Max Measures")
            counter += 1
    del cursor
    del row
    arcpy.AddMessage("Dictionary complete")
    arcpy.AddMessage(str(counter) + " null RTE_ID and RTE_LEN errors")
    theball = [errors, dictionary]
    return theball


def subfilelength():
    arcpy.AddMessage("Starting subfile length check...")
    theball = roadwaydict()
    errors = theball[0]
    dictionary = theball[1]
    total = 0
    cursor = arcpy.SearchCursor(subfiles, "SUBFILE <> 4 AND SUBFILE <> 5")
    for row in cursor:
        total += 1
    del cursor
    del row
    # counto = int(arcpy.GetCount_management(subfiles).getOutput(0))
    # total = counto - 1
    starter = 0
    counter = 0
    previous = ""
    cursor = arcpy.SearchCursor(subfiles, "SUBFILE <> 4 AND SUBFILE <> 5", "", "", "RTE_ID A; BMP A")
    for row in cursor:
        id = row.RTE_ID
        if row.EMP is not None and row.BMP is not None and row.LEN_OF_SECTION is not None:
            if id in dictionary.keys():
                current = id
                if starter == 0:
                    sublength = 0
                    linevalues = dictionary[current]
                    linelen = linevalues[0]
                    linemin = linevalues[1]
                    linemax = linevalues[2]
                    bmp1 = row.BMP
                    bmp = row.BMP
                    emp = row.EMP
                    sublength += row.LEN_OF_SECTION
                    dist = row.DISTRICT
                    if abs((emp - bmp) - row.LEN_OF_SECTION) > .001:
                        errorinfo = []
                        errorinfo.append(current)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append("")
                        errorinfo.append(emp)
                        errorinfo.append("")
                        errorinfo.append(sublength)
                        errorinfo.append("")
                        errorinfo.append(
                            "BMP and EMP difference does not equal the LEN_OF_SECTION. SUBFILE OID: " + str(row.OBJECTID))
                        errors.append(errorinfo)
                        counter += 1
                    previous = current

                elif current != previous and starter != total:
                    if abs(linelen - sublength) > .003:
                        errorinfo = []
                        errorinfo.append(previous)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append(linemin)
                        errorinfo.append(emp)
                        errorinfo.append(linemax)
                        errorinfo.append(sublength)
                        errorinfo.append(linelen)
                        errorinfo.append("RTE_LEN does not equal SUBFILES total LEN_OF_SECTION")
                        errors.append(errorinfo)
                        counter += 1
                    if abs(linemin - bmp1) > .002:
                        errorinfo = []
                        errorinfo.append(previous)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append(linemin)
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("Line minimum measure does not equal starting BMP")
                        errors.append(errorinfo)
                        counter += 1
                    if abs(linemax - emp) > .003:
                        errorinfo = []
                        errorinfo.append(previous)
                        errorinfo.append(dist)
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append(emp)
                        errorinfo.append(linemax)
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("Line maximum measure does not equal ending EMP")
                        errors.append(errorinfo)
                        counter += 1

                    sublength = 0
                    linevalues = dictionary[current]
                    linelen = linevalues[0]
                    linemin = linevalues[1]
                    linemax = linevalues[2]
                    bmp1 = row.BMP
                    bmp = row.BMP
                    emp = row.EMP
                    sublength += row.LEN_OF_SECTION
                    dist = row.DISTRICT
                    if abs((emp - bmp) - row.LEN_OF_SECTION) > .001:
                        errorinfo = []
                        errorinfo.append(current)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append("")
                        errorinfo.append(emp)
                        errorinfo.append("")
                        errorinfo.append(sublength)
                        errorinfo.append("")
                        errorinfo.append(
                            "BMP and EMP difference does not equal the LEN_OF_SECTION. SUBFILE OID: " + str(row.OBJECTID))
                        errors.append(errorinfo)
                        counter += 1
                    previous = current

                elif current == previous and starter != total:
                    bmp = row.BMP
                    emp = row.EMP
                    sublength += row.LEN_OF_SECTION
                    dist = row.DISTRICT
                    if abs((emp - bmp) - row.LEN_OF_SECTION) > .001:
                        errorinfo = []
                        errorinfo.append(current)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append("")
                        errorinfo.append(emp)
                        errorinfo.append("")
                        errorinfo.append(sublength)
                        errorinfo.append("")
                        errorinfo.append(
                            "BMP and EMP difference does not equal the LEN_OF_SECTION. SUBFILE OID: " + str(row.OBJECTID))
                        errors.append(errorinfo)
                        counter += 1
                    previous = current

                elif current != previous and starter == total:
                    if abs(linelen - sublength) > .003:
                        errorinfo = []
                        errorinfo.append(previous)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append(linemin)
                        errorinfo.append(emp)
                        errorinfo.append(linemax)
                        errorinfo.append(sublength)
                        errorinfo.append(linelen)
                        errorinfo.append("RTE_LEN does not equal SUBFILES total LEN_OF_SECTION")
                        errors.append(errorinfo)
                        counter += 1
                    if abs(linemin - bmp1) > .002:
                        errorinfo = []
                        errorinfo.append(previous)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append(linemin)
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("Line minimum measure does not equal starting BMP")
                        errors.append(errorinfo)
                        counter += 1
                    if abs(linemax - emp) > .003:
                        errorinfo = []
                        errorinfo.append(previous)
                        errorinfo.append(dist)
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append(emp)
                        errorinfo.append(linemax)
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("Line maximum measure does not equal ending EMP")
                        errors.append(errorinfo)
                        counter += 1

                    sublength = 0
                    linevalues = dictionary[current]
                    linelen = linevalues[0]
                    linemin = linevalues[1]
                    linemax = linevalues[2]
                    bmp1 = row.BMP
                    bmp = row.BMP
                    emp = row.EMP
                    sublength += row.LEN_OF_SECTION
                    dist = row.DISTRICT
                    if abs((emp - bmp) - row.LEN_OF_SECTION) > .001:
                        errorinfo = []
                        errorinfo.append(current)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append("")
                        errorinfo.append(emp)
                        errorinfo.append("")
                        errorinfo.append(sublength)
                        errorinfo.append("")
                        errorinfo.append(
                            "BMP and EMP difference does not equal the LEN_OF_SECTION. SUBFILE OID: " + str(row.OBJECTID))
                        errors.append(errorinfo)
                        counter += 1
                    if abs(linelen - sublength) > .003:
                        errorinfo = []
                        errorinfo.append(current)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append(linemin)
                        errorinfo.append(emp)
                        errorinfo.append(linemax)
                        errorinfo.append(sublength)
                        errorinfo.append(linelen)
                        errorinfo.append("RTE_LEN does not equal SUBFILES total LEN_OF_SECTION")
                        errors.append(errorinfo)
                        counter += 1
                    if abs(linemin - bmp1) > .002:
                        errorinfo = []
                        errorinfo.append(current)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append(linemin)
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("Line minimum measure does not equal starting BMP")
                        errors.append(errorinfo)
                        counter += 1
                    if abs(linemax - emp) > .003:
                        errorinfo = []
                        errorinfo.append(current)
                        errorinfo.append(dist)
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append(emp)
                        errorinfo.append(linemax)
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("Line maximum measure does not equal ending EMP")
                        errors.append(errorinfo)
                        counter += 1

                elif current == previous and starter == total:
                    bmp = row.BMP
                    emp = row.EMP
                    sublength += row.LEN_OF_SECTION
                    dist = row.DISTRICT
                    if abs((emp - bmp) - row.LEN_OF_SECTION) > .001:
                        errorinfo = []
                        errorinfo.append(current)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append("")
                        errorinfo.append(emp)
                        errorinfo.append("")
                        errorinfo.append(sublength)
                        errorinfo.append("")
                        errorinfo.append(
                            "BMP and EMP difference does not equal the LEN_OF_SECTION. SUBFILE OID: " + str(row.OBJECTID))
                        errors.append(errorinfo)
                        counter += 1
                    if abs(linelen - sublength) > .003:
                        errorinfo = []
                        errorinfo.append(current)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append(linemin)
                        errorinfo.append(emp)
                        errorinfo.append(linemax)
                        errorinfo.append(sublength)
                        errorinfo.append(linelen)
                        errorinfo.append("RTE_LEN does not equal SUBFILES total LEN_OF_SECTION")
                        errors.append(errorinfo)
                        counter += 1
                    if abs(linemin - bmp1) > .002:
                        errorinfo = []
                        errorinfo.append(current)
                        errorinfo.append(dist)
                        errorinfo.append(bmp1)
                        errorinfo.append(linemin)
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("Line minimum measure does not equal starting BMP")
                        errors.append(errorinfo)
                        counter += 1
                    if abs(linemax - emp) > .003:
                        errorinfo = []
                        errorinfo.append(current)
                        errorinfo.append(dist)
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append(emp)
                        errorinfo.append(linemax)
                        errorinfo.append("")
                        errorinfo.append("")
                        errorinfo.append("Line maximum measure does not equal ending EMP")
                        errors.append(errorinfo)
                        counter += 1
                starter += 1
                arcpy.AddMessage(str(starter) + "/" + str(total))

            else:
                starter += 1
                arcpy.AddMessage(str(starter) + "/" + str(total))
                pass
        else:
            errorinfo = []
            errorinfo.append(id)
            errorinfo.append(row.DISTRICT)
            errorinfo.append(row.BMP)
            errorinfo.append("")
            errorinfo.append(row.EMP)
            errorinfo.append("")
            errorinfo.append(row.LEN_OF_SECTION)
            errorinfo.append("")
            errorinfo.append("BMP, EMP, or LEN_OF_SECTION in SUBFILES is NULL. Please populate.")
            errors.append(errorinfo)
            counter += 1
    arcpy.AddMessage(str(counter) + " subfile length errors.")
    return errors


def removevertices():
    arcpy.AddMessage("Starting multipart and vertex measure check...")
    counter = 0
    errors = []
    query = """ RDBD_TYPE <> 'CNCTR-GS' AND RDBD_TYPE <> 'CONNECTOR' AND RDBD_TYPE <> 'OTHER' AND RDBD_TYPE <> 'RAMP' AND RDBD_TYPE <> 'TURNAROUND'  """
    cursor = arcpy.SearchCursor(roadways, query)
    for row in cursor:
        geom = row.shape
        allparts = geom.getPart()
        if geom.isMultipart:
            errorinfo = []
            errorinfo.append(row.OBJECTID)
            errorinfo.append(row.RTE_ID)
            errorinfo.append(row.DIST_NM)
            errorinfo.append(row.DIST_NBR)
            errorinfo.append("Multipart feature.")
            errors.append(errorinfo)
            counter += 1
        try:
            lastX = 0
            lastY = 0
            lastM = 0
            for part in allparts:
                srtpnt = 0
                for pnt in part:
                    if srtpnt == 0:
                        x = pnt.X
                        y = pnt.Y
                        m = pnt.M
                        if row.RDBD_TYPE == "LG" or row.RDBD_TYPE == "XG":
                            if math.isnan(m):
                                errorinfo = []
                                errorinfo.append(row.OBJECTID)
                                errorinfo.append(row.RTE_ID)
                                errorinfo.append(row.DIST_NM)
                                errorinfo.append(row.DIST_NBR)
                                errorinfo.append("Has vertex with zero measure, apply measures.")
                                if errorinfo not in errors:
                                    errors.append(errorinfo)
                                    counter += 1
                        lastX = x
                        lastY = y
                        lastM = m
                        srtpnt += 1
                    else:
                        x = pnt.X
                        y = pnt.Y
                        m = pnt.M
                        if row.RDBD_TYPE == "LG" or row.RDBD_TYPE == "XG":
                            if math.isnan(m):
                                errorinfo = []
                                errorinfo.append(row.OBJECTID)
                                errorinfo.append(row.RTE_ID)
                                errorinfo.append(row.DIST_NM)
                                errorinfo.append(row.DIST_NBR)
                                errorinfo.append("Has vertex with zero measure, apply measures.")
                                if errorinfo not in errors:
                                    errors.append(errorinfo)
                                    counter += 1
                            if m >= lastM:
                                errorinfo = []
                                errorinfo.append(row.OBJECTID)
                                errorinfo.append(row.RTE_ID)
                                errorinfo.append(row.DIST_NM)
                                errorinfo.append(row.DIST_NBR)
                                errorinfo.append("LG or XG with non-decreasing measure, Re-apply measures.")
                                if errorinfo not in errors:
                                    errors.append(errorinfo)
                                    counter += 1
                        elif row.RDBD_TYPE == "KG" or row.RDBD_TYPE == "AG" or row.RDBD_TYPE == "XG":
                            if math.isnan(m):
                                errorinfo = []
                                errorinfo.append(row.OBJECTID)
                                errorinfo.append(row.RTE_ID)
                                errorinfo.append(row.DIST_NM)
                                errorinfo.append(row.DIST_NBR)
                                errorinfo.append("Has vertex with zero measure, apply measures.")
                                if errorinfo not in errors:
                                    errors.append(errorinfo)
                                    counter += 1
                            if m <= lastM:
                                errorinfo = []
                                errorinfo.append(row.OBJECTID)
                                errorinfo.append(row.RTE_ID)
                                errorinfo.append(row.DIST_NM)
                                errorinfo.append(row.DIST_NBR)
                                errorinfo.append("KG, AG, or XG with non-increasing measure, Re-apply measures.")
                                if errorinfo not in errors:
                                    errors.append(errorinfo)
                                    counter += 1
                        lastX = x
                        lastY = y
                        lastM = m
        except:
            errorinfo = []
            errorinfo.append(row.OBJECTID)
            errorinfo.append(row.RTE_ID)
            errorinfo.append(row.DIST_NM)
            errorinfo.append(row.DIST_NBR)
            errorinfo.append("Geometry Error. Please check geometry.")
            errors.append(errorinfo)
            counter += 1
    print str(counter) + " multipart and vertex measure errors."

    arcpy.AddMessage("Creating PNGs...")
    arcpy.AddMessage("Exporting 1 of 3...")
    mxd = arcpy.mapping.MapDocument("T:\\DATAMGT\\MAPPING\\Data Quality Checks\\Error_Check_Scripts\\MeasureErrors.mxd")
    arcpy.mapping.ExportToPNG(mxd, workspace + "\\Measure Errors " + str(today) + ".png")
    del mxd
    arcpy.AddMessage("Exporting 2 of 3...")
    mxd = arcpy.mapping.MapDocument(
        "T:\\DATAMGT\\MAPPING\\Data Quality Checks\\Error_Check_Scripts\\MeasureErrors_LG_XG.mxd")
    arcpy.mapping.ExportToPNG(mxd, workspace + "\\Measure LG XG Red is Bad " + str(today) + ".png")
    del mxd
    arcpy.AddMessage("Exporting 3 of 3...")
    mxd = arcpy.mapping.MapDocument(
        "T:\\DATAMGT\\MAPPING\\Data Quality Checks\\Error_Check_Scripts\\MeasureErrors_Not_LG_XG.mxd")
    arcpy.mapping.ExportToPNG(mxd, workspace + "\\Measure RG AG Red is Bad " + str(today) + ".png")
    del mxd
    arcpy.AddMessage("PNGs Complete.")
    return errors


def onsystem():
    arcpy.AddMessage("Starting on-system attribute and measure checks...")
    counter = 0
    attexceptions = ['SHOSR-KG']
    atterrors = []
    measerrors = []
    query = """ RTE_CLASS ='1' AND RDBD_TYPE <> 'RAMP' AND RDBD_TYPE <> 'TURNAROUND' AND RDBD_TYPE <> 'CONNECTOR' """
    cursor = arcpy.SearchCursor(roadways, query)
    for row in cursor:
        if row.RTE_ID not in attexceptions:
            if row.RTE_ID is not None:
                idpfx = row.RTE_ID[:2]
                if row.RTE_PRFX != idpfx:
                    if row.RDBD_TYPE != "CNCTR-GS":
                        errorinfo = []
                        errorinfo.append(row.RTE_ID)
                        errorinfo.append(row.DIST_NBR)
                        errorinfo.append(row.RTE_PRFX)
                        errorinfo.append(idpfx)
                        errorinfo.append("RTE_PRFX inconsistent with RTE_ID")
                        atterrors.append(errorinfo)
                        counter += 1

                if row.RTE_NBR is None:
                    idnbr = row.RTE_ID[2:6]
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append("NULL")
                    errorinfo.append(idnbr)
                    errorinfo.append("RTE_NBR is Null. Populate RTE_NBR.")
                    atterrors.append(errorinfo)
                    counter += 1
                    txtRTE_NBR = ""
                elif len(row.RTE_NBR) == 1:
                    txtRTE_NBR = "000" + row.RTE_NBR
                elif len(row.RTE_NBR) == 2:
                    txtRTE_NBR = "00" + row.RTE_NBR
                elif len(row.RTE_NBR) == 3:
                    txtRTE_NBR = "0" + row.RTE_NBR
                else:
                    txtRTE_NBR = row.RTE_NBR
                idnbr = row.RTE_ID[2:6]
                if txtRTE_NBR != idnbr:
                    if row.RDBD_TYPE != "CNCTR-GS":
                        errorinfo = []
                        errorinfo.append(row.RTE_ID)
                        errorinfo.append(row.DIST_NBR)
                        errorinfo.append(txtRTE_NBR)
                        errorinfo.append(idnbr)
                        errorinfo.append("RTE_NBR inconsistent with RTE_ID")
                        atterrors.append(errorinfo)
                        counter += 1
                if row.RTE_NM != "" and row.RTE_NM is not None:
                    nmpfx = row.RTE_NM[:2]
                    if row.RTE_PRFX != nmpfx:
                        if row.RDBD_TYPE != "CNCTR-GS":
                            errorinfo = []
                            errorinfo.append(row.RTE_ID)
                            errorinfo.append(row.DIST_NBR)
                            errorinfo.append(row.RTE_PRFX)
                            errorinfo.append(nmpfx)
                            errorinfo.append("RTE_PRFX inconsistent with RTE_NM")
                            atterrors.append(errorinfo)
                            counter += 1
                    idtype = row.RTE_ID[-2:]
                    if row.RDBD_TYPE != idtype:
                        if row.RDBD_TYPE != "RAMP" and row.RDBD_TYPE != "CONNECTOR" and row.RDBD_TYPE != "TURNAROUND" and row.RDBD_TYPE != "CNCTR-GS" and row.RDBD_TYPE != "OTHER":
                            errorinfo = []
                            errorinfo.append(row.RTE_ID)
                            errorinfo.append(row.DIST_NBR)
                            errorinfo.append(row.RDBD_TYPE)
                            errorinfo.append(idtype)
                            errorinfo.append("RDBD_TYPE inconsistent with RTE_ID")
                            atterrors.append(errorinfo)
                            counter += 1
                    nmnbr = row.RTE_NM[2:6]
                    if txtRTE_NBR != nmnbr:
                        if row.RDBD_TYPE != "CNCTR-GS":
                            errorinfo = []
                            errorinfo.append(row.RTE_ID)
                            errorinfo.append(row.DIST_NBR)
                            errorinfo.append(txtRTE_NBR)
                            errorinfo.append(nmnbr)
                            errorinfo.append("RTE_NBR inconsistent with RTE_NM")
                            atterrors.append(errorinfo)
                            counter += 1
                    if len(row.RTE_NM) == 7:
                        nmsfx = row.RTE_NM[-1:]
                        if row.RTE_SFX != nmsfx:
                            if row.RDBD_TYPE != "CNCTR-GS":
                                errorinfo = []
                                errorinfo.append(row.RTE_ID)
                                errorinfo.append(row.DIST_NBR)
                                errorinfo.append(row.RTE_SFX)
                                errorinfo.append(nmsfx)
                                errorinfo.append("RTE_SFX inconsistent with RTE_NM")
                                atterrors.append(errorinfo)
                                counter += 1
                        idsfx = row.RTE_ID[6:7]
                        if row.RTE_SFX != idsfx:
                            if row.RDBD_TYPE != "CNCTR-GS":
                                errorinfo = []
                                errorinfo.append(row.RTE_ID)
                                errorinfo.append(row.DIST_NBR)
                                errorinfo.append(row.RTE_SFX)
                                errorinfo.append(idsfx)
                                errorinfo.append("RTE_SFX inconsistent with RTE_ID")
                                atterrors.append(errorinfo)
                                counter += 1
                else:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_NM)
                    errorinfo.append(row.FULL_ST_NM)
                    errorinfo.append("RTE_NM is Null. Populate RTE_NM.")
                    atterrors.append(errorinfo)
                    counter += 1
            else:
                errorinfo = []
                errorinfo.append(row.RTE_ID)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append(row.RTE_NM)
                errorinfo.append(row.FULL_ST_NM)
                errorinfo.append("RTE_ID is Null. Sort by RTE_ID ascending and Populate the Null RTE_ID.")
                atterrors.append(errorinfo)
                counter += 1
        else:
            id = row.RTE_ID
            rdbd = id[-2:]
            if row.RTE_ID == 'SHOSR-KG':
                if row.RTE_NM != 'SHOSR':
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_NM)
                    errorinfo.append("")
                    errorinfo.append("RTE_NM inconsistent with RTE_ID")
                    atterrors.append(errorinfo)
                    counter += 1
                if row.RTE_PRFX != 'SH':
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_PRFX)
                    errorinfo.append("")
                    errorinfo.append("RTE_PRFX inconsistent with RTE_ID")
                    atterrors.append(errorinfo)
                    counter += 1
                if row.RTE_NBR != 'OSR':
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_NBR)
                    errorinfo.append("")
                    errorinfo.append("RTE_NBR inconsistent with RTE_ID")
                    atterrors.append(errorinfo)
                    counter += 1
                if row.RDBD_TYPE != rdbd:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RDBD_TYPE)
                    errorinfo.append("")
                    errorinfo.append("RDBD_TYPE inconsistent with RTE_ID")
                    atterrors.append(errorinfo)
                    counter += 1
            else:
                errorinfo = []
                errorinfo.append(row.RTE_ID)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append(row.RTE_NM)
                errorinfo.append("")
                errorinfo.append("Bad RTE_ID")
                atterrors.append(errorinfo)

        id = row.RTE_ID
        geom = row.shape
        ext = geom.extent
        Mmin = round(ext.MMin, 3)
        Mmax = round(ext.MMax, 3)
        Mdiff = abs(Mmax - Mmin)
        wholelen = geom.length * .000621371
        shp_len = float(format(float(wholelen), '.3f'))
        rte_len = row.RTE_LEN
        testlen = abs(shp_len - Mdiff)
        if rte_len is not None and id is not None:
            if testlen <= .003 and abs(rte_len - shp_len) > .003:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(Mdiff)
                errorinfo.append(shp_len)
                errorinfo.append(rte_len)
                errorinfo.append(row.DIST_NM)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append(abs(rte_len - shp_len))
                measerrors.append(errorinfo)
                counter += 1
            elif abs(shp_len - Mdiff) > .003:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(Mdiff)
                errorinfo.append(shp_len)
                errorinfo.append(rte_len)
                errorinfo.append(row.DIST_NM)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append(abs(shp_len - Mdiff))
                measerrors.append(errorinfo)
                counter += 1
            elif abs(rte_len - Mdiff) > .003:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(Mdiff)
                errorinfo.append(shp_len)
                errorinfo.append(rte_len)
                errorinfo.append(row.DIST_NM)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append(abs(rte_len - Mdiff))
                measerrors.append(errorinfo)
                counter += 1
            elif abs(shp_len - rte_len) > .003:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(Mdiff)
                errorinfo.append(shp_len)
                errorinfo.append(rte_len)
                errorinfo.append(row.DIST_NM)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append(abs(shp_len - rte_len))
                measerrors.append(errorinfo)
                counter += 1
            else:
                pass
        else:
            oid = str(row.OBJECTID)
            id = str(row.RTE_ID)
            errorinfo = []
            errorinfo.append(id)
            errorinfo.append(str(Mdiff))
            errorinfo.append(str(shp_len))
            errorinfo.append(str(rte_len))
            errorinfo.append(row.DIST_NM)
            errorinfo.append(row.DIST_NBR)
            errorinfo.append("OID: " + oid)
            measerrors.append(errorinfo)
            counter += 1

    arcpy.AddMessage(str(counter) + " on system attribute and measure errors.")
    errors = [atterrors, measerrors]
    return errors


def offsysatt():
    arcpy.AddMessage("Starting off-system attribute check...")

    counter = 0
    errors = []
    query = """ (RTE_CLASS = '2' OR RTE_CLASS = '3') AND RDBD_TYPE <> 'CONNECTOR' AND RDBD_TYPE <> 'OTHER' AND RDBD_TYPE <> 'RAMP' AND RDBD_TYPE <> 'TURNAROUND' AND RDBD_TYPE <> 'CNCTR-GS' """
    cursor = arcpy.SearchCursor(roadways, query)
    for row in cursor:
        if row.DIST_NBR is not None:
            if row.RTE_CLASS == '2':
                if row.RTE_ID is not None:
                    IDlen = len(row.RTE_ID)
                    if IDlen != 9:
                        errorinfo = []
                        errorinfo.append(row.RTE_ID)
                        errorinfo.append(row.DIST_NBR)
                        errorinfo.append(IDlen)
                        errorinfo.append("9")
                        errorinfo.append("RTE_ID should be 9 characters long. (3 digit County #) + (AA prefix) + (4 digit RTE_NBR)")
                        errors.append(errorinfo)
                        counter += 1
                else:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append("NULL")
                    errorinfo.append("RTE_ID is NULL. Sort TXDOT_ROADWAYS ascending by RTE_ID.")
                    errors.append(errorinfo)
                    counter += 1
                if row.RTE_NM != "" and row.RTE_NM is not None:
                    nmpfx1 = row.RTE_NM[3:5]
                    nmpfx2 = row.RTE_NM[3:4]
                    nmnbr1 = row.RTE_NM[5:9]
                    nmnbr2 = row.RTE_NM[4:9]
                else:
                    nmpfx1 = ""
                    nmpfx2 = ""
                    nmnbr1 = ""
                    nmnbr2 = ""
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_NM)
                    errorinfo.append("")
                    errorinfo.append("RTE_NM is ether NULL or not populated.")
                    errors.append(errorinfo)
                    counter += 1
                if row.RTE_PRFX == nmpfx1 or row.RTE_PRFX == nmpfx2:
                    pass
                else:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_PRFX)
                    errorinfo.append(nmpfx1)
                    errorinfo.append("RTE_PRFX inconsistent with RTE_NM")
                    errors.append(errorinfo)
                    counter += 1
                idpfx1 = row.RTE_ID[3:5]
                idpfx2 = row.RTE_ID[3:4]
                if row.RTE_PRFX == idpfx1 or row.RTE_PRFX == idpfx2:
                    pass
                else:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_PRFX)
                    errorinfo.append(idpfx1)
                    errorinfo.append("RTE_PRFX inconsistent with RTE_ID")
                    errors.append(errorinfo)
                    counter += 1
                if row.RTE_ID != row.RTE_NM:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.RTE_NM)
                    errorinfo.append("RTE_ID inconsistent with RTE_NM")
                    errors.append(errorinfo)
                    counter += 1
                if row.RTE_NBR is None:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_NBR)
                    errorinfo.append(row.RTE_CLASS)
                    errorinfo.append("RTE_NBR is NULL")
                    errors.append(errorinfo)
                    counter += 1
                    txtRTE_NBR = ""
                elif len(row.RTE_NBR) == 1:
                    txtRTE_NBR = "000" + row.RTE_NBR
                elif len(row.RTE_NBR) == 2:
                    txtRTE_NBR = "00" + row.RTE_NBR
                elif len(row.RTE_NBR) == 3:
                    txtRTE_NBR = "0" + row.RTE_NBR
                else:
                    txtRTE_NBR = row.RTE_NBR

                if txtRTE_NBR == nmnbr1 or txtRTE_NBR == nmnbr2:
                    pass
                else:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(txtRTE_NBR)
                    errorinfo.append(nmnbr2)
                    errorinfo.append("RTE_NBR inconsistent with RTE_NM")
                    errors.append(errorinfo)
                    counter += 1
                idnbr1 = row.RTE_ID[5:9]
                idnbr2 = row.RTE_ID[4:9]
                if txtRTE_NBR == idnbr1 or txtRTE_NBR == idnbr2:
                    pass
                else:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(txtRTE_NBR)
                    errorinfo.append(idnbr2)
                    errorinfo.append("RTE_NBR inconsistent with RTE_ID")
                    errors.append(errorinfo)
                    counter += 1
            if row.RTE_CLASS == '3':
                if row.RTE_PRFX != "FC":
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_PRFX)
                    errorinfo.append(row.RTE_CLASS)
                    errorinfo.append("RTE_PRFX inconsistent with RTE_CLASS. Should be 'FC'.")
                    errors.append(errorinfo)
                    counter += 1
                if row.RTE_NM is None:
                    pass
                elif len(row.RTE_NM) > 1:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_NM)
                    errorinfo.append(row.RTE_CLASS)
                    errorinfo.append("RTE_NM should not be populated for RTE_CLASS = 3")
                    errors.append(errorinfo)
                    counter += 1
                if row.RTE_ID is None:
                    oid = str(row.OBJECTID)
                    errorinfo = []
                    errorinfo.append("OID: " + oid)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_NBR)
                    errorinfo.append(row.RTE_CLASS)
                    errorinfo.append("RTE_ID is NULL")
                    errors.append(errorinfo)
                    counter += 1
                elif len(row.RTE_ID) != 6:
                    if len(row.RTE_ID) == 7:
                        specificID = row.RTE_ID
                        tail = specificID[-1]
                        if tail != 'L' and tail != 'R':
                            errorinfo = []
                            errorinfo.append(row.RTE_ID)
                            errorinfo.append(row.DIST_NBR)
                            errorinfo.append(tail)
                            errorinfo.append("'L' or 'R'")
                            errorinfo.append("7 character FC RTE_IDs should end with the 'L' or 'R' representing the roadbed.")
                            errors.append(errorinfo)
                            counter += 1
                    else:
                        print "'" + row.RTE_ID + "'"
                        errorinfo = []
                        errorinfo.append(row.RTE_ID)
                        errorinfo.append(row.DIST_NBR)
                        errorinfo.append(row.RTE_ID)
                        errorinfo.append(row.RTE_CLASS)
                        errorinfo.append("RTE_ID should be 6 characters long for this RTE_CLASS")
                        errors.append(errorinfo)
                        counter += 1
                if row.RTE_NBR is None:
                    pass
                elif len(row.RTE_NBR) > 1:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_NBR)
                    errorinfo.append(row.RTE_CLASS)
                    errorinfo.append("RTE_NBR should be blank for RTE_CLASS = 3.")
                    errors.append(errorinfo)
                    counter += 1
        else:
            errorinfo = []
            errorinfo.append(row.RTE_ID)
            errorinfo.append("")
            errorinfo.append("")
            errorinfo.append("")
            errorinfo.append("Road is drawn outside of district, county, or state boundary. Please fix geometry.")
            errors.append(errorinfo)
            counter += 1
    del cursor
    del row

    query = """ SUBFILE = 2 OR SUBFILE = 3  """
    cursor = arcpy.da.SearchCursor(subfiles, ["SUBFILE", "DISTRICT", "COUNTY", "RTE_ID", "CONTROLSEC", "ADMIN_SYSTEM", "CENSUS_CITY"], query)
    for row in cursor:
        sub = row[0]
        dist = row[1]
        cnty = row[2]
        id = row[3]
        cs = row[4]
        admin = row[5]
        city = row[6]

        if sub == 2:
            if id is not None:
                IDleng = len(id)
                if IDleng != 9:
                    errorinfo = []
                    errorinfo.append(id)
                    errorinfo.append(dist)
                    errorinfo.append(IDleng)
                    errorinfo.append("9")
                    errorinfo.append("RTE_ID should be 9 characters long. (3 digit County #) + (AA prefix) + (4 digit RTE_NBR)")
                    errors.append(errorinfo)
                    counter += 1
            else:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append("NULL")
                errorinfo.append("")
                errorinfo.append("RTE_ID is NULL. Sort ascending by RTE_ID in SUBFILES.")
                errors.append(errorinfo)
                counter += 1
            idcnty = id[:3]
            idcntyNUM = int(idcnty)
            if cnty != idcntyNUM:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(cnty)
                errorinfo.append(idcnty)
                errorinfo.append("RTE_ID county number should match COUNTY number.")
                errors.append(errorinfo)
                counter += 1
            cntyRange = range(1, 255)
            if cnty not in cntyRange:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(cnty)
                errorinfo.append("")
                errorinfo.append("COUNTY number not valid. Must be 1-254.")
                errors.append(errorinfo)
                counter += 1
            idcs = id[3:]
            if idcs != cs:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(idcs)
                errorinfo.append(cs)
                errorinfo.append("RTE_ID prefix and number should match CONSTROLSEC.")
                errors.append(errorinfo)
                counter += 1
            if city != 0 and city is not None:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(city)
                errorinfo.append("0")
                errorinfo.append("County Road should not be located in a city. CENSUS_CITY should be '0'.")
                errors.append(errorinfo)
                counter += 1
            if admin != 2:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(admin)
                errorinfo.append("2")
                errorinfo.append("County Road ADMIN_SYSTEM should be '2'.")
                errors.append(errorinfo)
                counter += 1
            distRange = range(1, 26)
            if dist not in distRange:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append("")
                errorinfo.append("")
                errorinfo.append("DISTRICT number not valid. Must be 1-25.")
                errors.append(errorinfo)
                counter += 1

        elif sub == 3:
            idlen = len(id)
            if idlen != 6:
                if idlen == 7:
                    tail = id[-1]
                    if tail != 'L' and tail != 'R':
                        errorinfo = []
                        errorinfo.append(id)
                        errorinfo.append(dist)
                        errorinfo.append(idlen)
                        errorinfo.append("6")
                        errorinfo.append("7 character FC RTE_IDs should end with the 'L' or 'R' representing the roadbed.")
                        errors.append(errorinfo)
                        counter += 1
                else:
                    errorinfo = []
                    errorinfo.append(id)
                    errorinfo.append(dist)
                    errorinfo.append(idlen)
                    errorinfo.append("6")
                    errorinfo.append("RTE_ID should be a 6 digit number.")
                    errors.append(errorinfo)
                    counter += 1
            if cs is not None:
                cslen = len(cs)
            else:
                cslen = 0
            if cslen != 6:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(cs)
                errorinfo.append(cslen)
                errorinfo.append("CONTROLSEC should be 6 digits long.")
                errors.append(errorinfo)
                counter += 1
            if city > 0:
                pass
            else:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(city)
                errorinfo.append("")
                errorinfo.append("FC Streets should be located in a city. CENSUS_CITY should be populated.")
                errors.append(errorinfo)
                counter += 1
            if admin != 4:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(admin)
                errorinfo.append("4")
                errorinfo.append("FC Streets' ADMIN_SYSTEM should be '4'.")
                errors.append(errorinfo)
                counter += 1
            cntyRange = range(1, 255)
            if cnty not in cntyRange:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(cnty)
                errorinfo.append("")
                errorinfo.append("COUNTY number not valid. Must be 1-254.")
                errors.append(errorinfo)
                counter += 1
            distRange = range(1, 26)
            if dist not in distRange:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append("")
                errorinfo.append("")
                errorinfo.append("DISTRICT number not valid. Must be 1-25.")
                errors.append(errorinfo)
                counter += 1

    del cursor
    del row

    arcpy.AddMessage(str(counter) + " off system attribute errors.")
    return errors


def screenlines():
    arcpy.AddMessage("Starting screen lines check...")
    errors = []
    counter = 0
    arcpy.CreateFileGDB_management(workspace, "SL_Working.gdb")
    slbase = workspace + "\\SL_Working.gdb"
    from arcpy import env
    env.workspace = slbase
    arcpy.env.outputMFlag = "Enabled"
    comancheSL = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.QAQC\\TPP_GIS.APP_TPP_GIS_ADMIN.Screen_Lines"
    # Screen_Lines = slbase + "\\Screen_Lines"
    # Screen_Join_Output_shp = slbase + "\\Screen_Join_Output"
    # OnSystem_Roadways = slbase + "\\OnSystem_Roadways"
    # Screen_Line_Intersect_shp = slbase + "\\Screen_Line_Intersect"
    # Screen_Line_Result_dbf = slbase + "\\Screen_Line_Result"
    # Screen_Lines_Summarized_dbf = slbase + "\\Screen_Lines_Summarized"
    Screen_Lines = "Screen_Lines"
    Screen_Join_Output_shp = "Screen_Join_Output"
    OnSystem_Roadways = "OnSystem_Roadways"
    Screen_Line_Intersect_shp = "Screen_Line_Intersect"
    Screen_Line_Result_dbf = "result"
    Screen_Lines_Summarized_dbf = "summarized"
    Output_Event_Table_Properties = "RID POINT MEAS"

    print "Screen Lines (1/8): Exporting Screen Lines"
    arcpy.FeatureClassToFeatureClass_conversion(comancheSL, slbase, "Screen_Lines")
    print "Screen Lines (2/8): Joining with Districts from Comanche"
    arcpy.SpatialJoin_analysis(Screen_Lines, txdotdist, Screen_Join_Output_shp, "JOIN_ONE_TO_ONE", "KEEP_ALL")
    try:
        print "Screen Lines (3/8): Exporting On-System Roadways"
        arcpy.FeatureClassToFeatureClass_conversion(txdotroads, slbase, "OnSystem_Roadways", """RTE_CLASS = '1' AND RTE_OPEN = 1""")
        print "Screen Lines (4/8): Intersecting Screen Lines with Roadbeds"
        arcpy.Intersect_analysis([OnSystem_Roadways, Screen_Join_Output_shp], Screen_Line_Intersect_shp, "ALL", "", "POINT")
        print "Screen Lines (5/8): Locating Points along Routes"
        arcpy.LocateFeaturesAlongRoutes_lr(Screen_Line_Intersect_shp, OnSystem_Roadways, "RTE_ID", "0 Meters", Screen_Line_Result_dbf, Output_Event_Table_Properties)
        print "Screen Lines (6/8): Calculating Summary Statistics"
        arcpy.Statistics_analysis(Screen_Line_Result_dbf, Screen_Lines_Summarized_dbf, "MEAS MIN;MEAS MAX;DIST_NM FIRST;DIST_NBR FIRST", "SCREEN_ID")
        print "Screen Lines (7/8): Adding Difference Column"
        arcpy.AddField_management(Screen_Lines_Summarized_dbf, "CALC_DIFF", "FLOAT")
        # print "Calculating Difference Column"
        # arcpy.CalculateField_management(Screen_Lines_Summarized_dbf, "DIFFERENCE", "Abs ([MAX_MEAS]- [MIN_MEAS])", "VB", "")

        exceptions = {}
        cursor = arcpy.SearchCursor(Screen_Lines)
        for row in cursor:
            exceptions[row.SCREEN_ID] = row.DIFFERENCE
        del cursor
        del row

        print "Screen Lines (8/8): Compiling Errors"
        cursor = arcpy.UpdateCursor(Screen_Lines_Summarized_dbf)
        for row in cursor:
            screen = row.getValue("SCREEN_ID")
            minimum = row.getValue("MIN_MEAS")
            maximum = row.getValue("MAX_MEAS")
            distnm = row.getValue("FIRST_DIST_NM")
            distnbr = row.getValue("FIRST_DIST_NBR")
            diff = abs(maximum - minimum)
            thediff = float(format(float(diff), '.3f'))
            row.setValue("CALC_DIFF", thediff)
            cursor.updateRow(row)
            knowndiff = float(exceptions[screen])
            exceptiondiff = abs(thediff - knowndiff)
            if exceptiondiff < .003:
                pass
            else:
                thisrow = [str(screen), str(minimum), str(maximum), str(distnm), str(distnbr), str(thediff)]
                errors.append(thisrow)
                counter += 1
        arcpy.AddMessage(str(counter) + " screen line errors.")
        del cursor
        del row
    except:
        print "Screen Line error occured... investigate."
    return errors

def tollrdatt():
    arcpy.AddMessage("Starting tollroad attribute check...")

    tolldict = {}
    cursor = arcpy.da.SearchCursor(tolls, ["ON_SYSTEM", "RTE_ID", "ABRVN", "MAP_LBL"])
    for row in cursor:
        isON = row[0]
        if isON != 1:
            id = row[1]
            abv = row[2]
            lbl = row[3]
            tolldict[id] = [abv, lbl]
    del cursor
    del row

    counter = 0
    errors = []
    query = """ (RTE_CLASS = '6') AND RDBD_TYPE <> 'CONNECTOR' AND RDBD_TYPE <> 'OTHER' AND RDBD_TYPE <> 'RAMP' AND RDBD_TYPE <> 'TURNAROUND' AND RDBD_TYPE <> 'CNCTR-GS' """
    cursor = arcpy.SearchCursor(roadways, query)
    for row in cursor:
        if row.DIST_NBR is not None:
            if row.RDBD_TYPE != 'KG' and row.RDBD_TYPE != 'LG' and row.RDBD_TYPE != 'RG':
                curid = row.RTE_ID
                idcore = curid[:6]
                id = idcore + "-KG"
            else:
                id = row.RTE_ID
            if id in tolldict.keys():
                tableatts = tolldict[id]
                abv = tableatts[0]
                lbl = tableatts[1]

                if row.RTE_NM != abv:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_NM)
                    errorinfo.append(abv)
                    errorinfo.append("RTE_NM does not match RTE_TOLL table ABRVN field.")
                    errors.append(errorinfo)
                    counter += 1
                if row.RTE_PRFX !="TL":
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_PRFX)
                    errorinfo.append("TL")
                    errorinfo.append("RTE_PRFX sould be 'TL'.")
                    errors.append(errorinfo)
                    counter += 1
                idpfx1 = row.RTE_ID[:2]
                idrdbd = row.RTE_ID[-2:]
                if idpfx1 != "TL":
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(idpfx1)
                    errorinfo.append("TL")
                    errorinfo.append("RTE_ID prefix inconsistent. Should be 'TL'.")
                    errors.append(errorinfo)
                    counter += 1
                if idrdbd != row.RDBD_TYPE:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(idrdbd)
                    errorinfo.append(row.RDBD_TYPE)
                    errorinfo.append("RTE_ID roadbed inconsistent with RDBD_TYPE.")
                    errors.append(errorinfo)
                    counter += 1
                if row.RTE_NBR is None:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.RTE_NBR)
                    errorinfo.append(row.RTE_CLASS)
                    errorinfo.append("RTE_NBR is NULL")
                    errors.append(errorinfo)
                    counter += 1
                    txtRTE_NBR = ""
                elif len(row.RTE_NBR) == 1:
                    txtRTE_NBR = "000" + row.RTE_NBR
                elif len(row.RTE_NBR) == 2:
                    txtRTE_NBR = "00" + row.RTE_NBR
                elif len(row.RTE_NBR) == 3:
                    txtRTE_NBR = "0" + row.RTE_NBR
                else:
                    txtRTE_NBR = row.RTE_NBR

                idnum = row.RTE_ID[2:6]
                if txtRTE_NBR != idnum:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(txtRTE_NBR)
                    errorinfo.append(idnum)
                    errorinfo.append("RTE_NBR inconsistent with RTE_ID number.")
                    errors.append(errorinfo)
                    counter += 1

                if row.FULL_ST_NM != lbl:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(row.FULL_ST_NM)
                    errorinfo.append(lbl)
                    errorinfo.append("FULL_ST_NM inconsistent with MAP_LBL field in the RTE_TOLL table.")
                    errors.append(errorinfo)
                    counter += 1
            else:
                errorinfo = []
                errorinfo.append(row.RTE_ID)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append("")
                errorinfo.append("")
                errorinfo.append("RTE_ID not in the RTE_TOLL table. Cannot verify attributes.")
                errors.append(errorinfo)
                counter += 1
        else:
            errorinfo = []
            errorinfo.append(row.RTE_ID)
            errorinfo.append("")
            errorinfo.append("")
            errorinfo.append("")
            errorinfo.append("Road is drawn outside of district, county, or state boundary. Please fix geometry.")
            errors.append(errorinfo)
            counter += 1
    del cursor
    del row

    gscID = {}
    query = """ RTE_CLASS = '6' AND RDBD_TYPE = 'CNCTR-GS' """
    cursor = arcpy.da.SearchCursor(roadways,["RTE_ID", "RTE_PRFX", "RTE_NBR"] , query)
    for row in cursor:
        theID = row[0]
        pfx = row[1]
        nbr = row[2]
        cs = pfx + nbr
        gscID[theID] = cs
    del cursor
    del row

    adminexceptiondict = {}
    adminexceptiondict["TL0029-KG"] = 7
    adminexceptiondict["TL0029-RG"] = 7
    adminexceptiondict["TL0029-LG"] = 7
    query = """SUBFILE = 6"""
    cursor = arcpy.da.SearchCursor(subfiles, ["RTE_ID", "CONTROLSEC", "ADMIN_SYSTEM", "DISTRICT", "TOLL", "COUNTY"], query)
    for row in cursor:
        id = row[0]
        cs = row[1]
        admin = row[2]
        dist = row[3]
        tollflag = row[4]
        cnty = row[5]

        if id not in gscID.keys():
            idcs = id[:6]
            if idcs != cs:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(idcs)
                errorinfo.append(cs)
                errorinfo.append("RTE_ID does not match CONTROLSEC.")
                errors.append(errorinfo)
                counter += 1
            prfx = id[:2]
            if prfx != "TL":
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(prfx)
                errorinfo.append("TL")
                errorinfo.append("RTE_ID must start with prefix 'TL'.")
                errors.append(errorinfo)
                counter += 1
        else:
            idlength = len(id)
            if idlength != 5 or id is None:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(idlength)
                errorinfo.append("5")
                errorinfo.append("RTE_ID should be '5' characters long.")
                errors.append(errorinfo)
                counter += 1
            theCS = gscID[id]
            if theCS != cs:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(cs)
                errorinfo.append(theCS)
                errorinfo.append("CONTROLSEC should match the control section for this GSC's associated highway.")
                errors.append(errorinfo)
                counter += 1
        if id not in adminexceptiondict.keys():
            if admin != 5 and admin != 6:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(admin)
                errorinfo.append("5 or 6")
                errorinfo.append("ADMIN_SYSTEM must be 5 (Private Toll) or 6 (Local Toll Authority).")
                errors.append(errorinfo)
                counter += 1
        else:
            value = adminexceptiondict[id]
            if admin != value:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(admin)
                errorinfo.append(value)
                errorinfo.append("RTE_ID is an exception. ADMIN_SYSTEM should be the value listed.")
                errors.append(errorinfo)
                counter += 1
        if tollflag != 1:
            errorinfo = []
            errorinfo.append(id)
            errorinfo.append(dist)
            errorinfo.append(tollflag)
            errorinfo.append("1")
            errorinfo.append("TOLL field should be populated as 1.")
            errors.append(errorinfo)
            counter += 1
        cntyRange = range(1, 255)
        if cnty not in cntyRange:
            errorinfo = []
            errorinfo.append(id)
            errorinfo.append(dist)
            errorinfo.append(cnty)
            errorinfo.append("")
            errorinfo.append("COUNTY number not valid. Must be 1-254.")
            errors.append(errorinfo)
            counter += 1
        distRange = range(1, 26)
        if dist not in distRange:
            errorinfo = []
            errorinfo.append(id)
            errorinfo.append(dist)
            errorinfo.append("")
            errorinfo.append("")
            errorinfo.append("DISTRICT number not valid. Must be 1-25.")
            errors.append(errorinfo)
            counter += 1

    del cursor
    del row

    arcpy.AddMessage(str(counter) + " tollroad attribute errors.")
    return errors

def fedrdatt():
    arcpy.AddMessage("Starting federal attribute check...")

    counter = 0
    errors = []
    query = """ (RTE_CLASS = '7') AND RDBD_TYPE <> 'CONNECTOR' AND RDBD_TYPE <> 'OTHER' AND RDBD_TYPE <> 'RAMP' AND RDBD_TYPE <> 'TURNAROUND' AND RDBD_TYPE <> 'CNCTR-GS' """
    cursor = arcpy.SearchCursor(roadways, query)
    for row in cursor:
        if row.DIST_NBR is not None:
            if row.RTE_NM != "" and row.RTE_NM is not None:
                errorinfo = []
                errorinfo.append(row.RTE_ID)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append(row.RTE_NM)
                errorinfo.append("")
                errorinfo.append("RTE_NM should be blank.")
                errors.append(errorinfo)
                counter += 1
            if row.RTE_PRFX !="" and row.RTE_PRFX is not None:
                errorinfo = []
                errorinfo.append(row.RTE_ID)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append(row.RTE_PRFX)
                errorinfo.append("")
                errorinfo.append("RTE_PRFX should be blank.")
                errors.append(errorinfo)
                counter += 1
            if row.RTE_NBR !="" and row.RTE_NBR !=" " and row.RTE_NBR is not None:
                errorinfo = []
                errorinfo.append(row.RTE_ID)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append(row.RTE_NBR)
                errorinfo.append("")
                errorinfo.append("RTE_NBR should be blank.")
                errors.append(errorinfo)
                counter += 1

            idrange = range(700000, 706000)
            if row.RTE_ID is not None:
                id = int(row.RTE_ID)
                if id not in idrange:
                    errorinfo = []
                    errorinfo.append(row.RTE_ID)
                    errorinfo.append(row.DIST_NBR)
                    errorinfo.append(id)
                    errorinfo.append("")
                    errorinfo.append("RTE_ID not in range. Should be 700000 - 705999.")
                    errors.append(errorinfo)
                    counter += 1
            else:
                errorinfo = []
                errorinfo.append(row.RTE_ID)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append("")
                errorinfo.append("")
                errorinfo.append("RTE_ID is NULL. Sort TXDOT_ROADWAYS ascending RTE_ID to find and populate RTE_ID.")
                errors.append(errorinfo)
                counter += 1

        else:
            errorinfo = []
            errorinfo.append(row.RTE_ID)
            errorinfo.append("")
            errorinfo.append("")
            errorinfo.append("")
            errorinfo.append("Road is drawn outside of district, county, or state boundary. Please fix geometry.")
            errors.append(errorinfo)
            counter += 1
    del cursor
    del row

    query = """SUBFILE = 7"""
    cursor = arcpy.da.SearchCursor(subfiles, ["RTE_ID", "CONTROLSEC", "ADMIN_SYSTEM", "DISTRICT", "COUNTY"], query)
    for row in cursor:
        id = row[0]
        cs = row[1]
        admin = row[2]
        dist = row[3]
        cnty = row[4]

        if id is not None:
            idcs = id[2:]
            csnum = cs[2:]
            if idcs != csnum:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(idcs)
                errorinfo.append(csnum)
                errorinfo.append("RTE_ID (last 4 digits) does not match CONTROLSEC (last 4 digits).")
                errors.append(errorinfo)
                counter += 1
            prfx = cs[:2]
            if prfx != "FD":
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(prfx)
                errorinfo.append("FD")
                errorinfo.append("CONSTROLSEC must start with prefix 'FD'.")
                errors.append(errorinfo)
                counter += 1
            idrange = range(700000, 706000)
            id = int(id)
            if id not in idrange:
                errorinfo = []
                errorinfo.append(row.RTE_ID)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append(id)
                errorinfo.append("")
                errorinfo.append("RTE_ID not in range. Should be 700000 - 705999.")
                errors.append(errorinfo)
                counter += 1

            adminrange = range(7, 16)
            if admin not in adminrange:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(admin)
                errorinfo.append("7 - 15")
                errorinfo.append("ADMIN_SYSTEM must be in range 7 - 15 designating the Federal Agency.")
                errors.append(errorinfo)
                counter += 1

            cntyRange = range(1, 255)
            if cnty not in cntyRange:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append(cnty)
                errorinfo.append("")
                errorinfo.append("COUNTY number not valid. Must be 1-254.")
                errors.append(errorinfo)
                counter += 1
            distRange = range(1, 26)
            if dist not in distRange:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(dist)
                errorinfo.append("")
                errorinfo.append("")
                errorinfo.append("DISTRICT number not valid. Must be 1-25.")
                errors.append(errorinfo)
                counter += 1

        else:
            errorinfo = []
            errorinfo.append(row.RTE_ID)
            errorinfo.append(row.DIST_NBR)
            errorinfo.append("")
            errorinfo.append("")
            errorinfo.append("RTE_ID is NULL. Sort ascending RTE_ID in SUBFILES to find and populate RTE_ID.")
            errors.append(errorinfo)
            counter += 1
    del cursor
    del row

    arcpy.AddMessage(str(counter) + " federal attribute errors.")
    return errors


def assemblereport(check1, check2, check3, check4, check5, check6, check7, check8, check9, check10, check11):
    arcpy.AddMessage("Beginning error checks...")
    if check1 == "true":
        check2 = "true"
        check3 = "true"
        check4 = "true"
        check5 = "true"
        check6 = "true"
        check7 = "true"
        check8 = "true"
        check9 = "true"
        check10 = "true"
        check11 = "true"

    font = xlwt.Font()  # Create the Font
    font.name = 'Calibri'
    font.height = 240  # =point size you want * 20
    style = xlwt.XFStyle()  # Create the Style
    style.font = font  # Apply the Font to the Style

    if check2 == "true":
        arcpy.AddMessage("Overlap Errors...")
        overlapsheet = book.add_sheet("City Boundary Overlap")
        oeline = 0
        overlapsheet.write(oeline, 0, "RTE_ID", style=style)
        overlapsheet.write(oeline, 1, "Overlap Length", style=style)
        overlapsheet.write(oeline, 2, "District Name", style=style)
        overlapsheet.write(oeline, 3, "District Number", style=style)
        overlapsheet.write(oeline, 4, "City Name", style=style)
        overlapsheet.write(oeline, 5, "City Number", style=style)
        overlapsheet.write(oeline, 7,
                           "The following Route IDs are County Roads and FC Streets which cross a City Boundary as found in City_OverlapErrors.shp",
                           style=style)
        oeline += 1
        overlaplist = overlap()
        for i in overlaplist:
            if i[3] not in disterrors:
                disterrors.append(int(i[3]))
            overlapsheet.write(oeline, 0, i[0], style=style)
            overlapsheet.write(oeline, 1, i[1], style=style)
            overlapsheet.write(oeline, 2, i[2], style=style)
            overlapsheet.write(oeline, 3, i[3], style=style)
            overlapsheet.write(oeline, 4, i[4], style=style)
            overlapsheet.write(oeline, 5, i[5], style=style)
            oeline += 1
    if check3 == "true":
        arcpy.AddMessage("Route Open Errors...")
        opensheet = book.add_sheet("Route Open")
        roline = 0
        opensheet.write(roline, 0, "RTE_ID", style=style)
        opensheet.write(roline, 1, "RTE_OPEN", style=style)
        opensheet.write(roline, 2, "HIGHWAY_STATUS", style=style)
        opensheet.write(roline, 3, "Description", style=style)
        opensheet.write(roline, 4, "District Number", style=style)
        opensheet.write(roline, 6,
                        "The following Route IDs contain an error between RTE_OPEN in TxDOT_Roadways and ROADWAY_STATUS in SUBFILES",
                        style=style)
        roline += 1
        openlist = routeopen()
        for i in openlist:
            if i[4] not in disterrors:
                disterrors.append(int(i[4]))
            opensheet.write(roline, 0, i[0], style=style)
            opensheet.write(roline, 1, i[1], style=style)
            opensheet.write(roline, 2, i[2], style=style)
            opensheet.write(roline, 3, i[3], style=style)
            opensheet.write(roline, 4, i[4], style=style)
            roline += 1
    if check4 == "true":
        arcpy.AddMessage("OffSystem Geometry & Measure Errors...")
        geomsheet = book.add_sheet("OffSystem Geometry & Measures")
        ogline = 0
        geomsheet.write(ogline, 0, "RTE_ID", style=style)
        geomsheet.write(ogline, 1, "Measures' Length", style=style)
        geomsheet.write(ogline, 2, "Shape Length", style=style)
        geomsheet.write(ogline, 3, "RTE_LEN", style=style)
        geomsheet.write(ogline, 4, "District Name", style=style)
        geomsheet.write(ogline, 5, "District Number", style=style)
        geomsheet.write(ogline, 6, "Difference", style=style)
        geomsheet.write(ogline, 8,
                        "The following Route IDs contain an error between their measures' length, shape length, and RTE_LEN",
                        style=style)
        ogline += 1
        geomlist = measurelength()
        for i in geomlist:
            if i[5] not in disterrors:
                try:
                    disterrors.append(int(i[5]))
                except:
                    pass
            geomsheet.write(ogline, 0, i[0], style=style)
            geomsheet.write(ogline, 1, i[1], style=style)
            geomsheet.write(ogline, 2, i[2], style=style)
            geomsheet.write(ogline, 3, i[3], style=style)
            geomsheet.write(ogline, 4, i[4], style=style)
            geomsheet.write(ogline, 5, i[5], style=style)
            geomsheet.write(ogline, 6, i[6], style=style)
            ogline += 1
    if check5 == "true":
        arcpy.AddMessage("Subfile Length Errors...")
        subsheet = book.add_sheet("Subfile Lengths")
        sfline = 0
        subsheet.write(sfline, 0, "RTE_ID", style=style)
        subsheet.write(sfline, 1, "District Number", style=style)
        subsheet.write(sfline, 2, "BMP", style=style)
        subsheet.write(sfline, 3, "Min Measure", style=style)
        subsheet.write(sfline, 4, "EMP", style=style)
        subsheet.write(sfline, 5, "Max Measure", style=style)
        subsheet.write(sfline, 6, "Subfile Len", style=style)
        subsheet.write(sfline, 7, "RTE_LEN", style=style)
        subsheet.write(sfline, 8, "Description", style=style)
        subsheet.write(sfline, 10, "The following Route IDs contain an error between their line and SUBFILES lengths",
                       style=style)
        sfline += 1
        sublist = subfilelength()
        for i in sublist:
            if i[1] not in disterrors:
                try:
                    disterrors.append(int(i[1]))
                except:
                    pass
            subsheet.write(sfline, 0, i[0], style=style)
            subsheet.write(sfline, 1, i[1], style=style)
            subsheet.write(sfline, 2, i[2], style=style)
            subsheet.write(sfline, 3, i[3], style=style)
            subsheet.write(sfline, 4, i[4], style=style)
            subsheet.write(sfline, 5, i[5], style=style)
            subsheet.write(sfline, 6, i[6], style=style)
            subsheet.write(sfline, 7, i[7], style=style)
            subsheet.write(sfline, 8, i[8], style=style)
            sfline += 1
    if check6 == "true":
        arcpy.AddMessage("Multipart Errors and Measure Errors...")
        multisheet = book.add_sheet("Multipart & Measure Errors")
        mmline = 0
        multisheet.write(mmline, 0, "OBJECTID", style=style)
        multisheet.write(mmline, 1, "RTE_ID", style=style)
        multisheet.write(mmline, 2, "District Name", style=style)
        multisheet.write(mmline, 3, "District Number", style=style)
        multisheet.write(mmline, 4, "Description", style=style)
        multisheet.write(mmline, 6, "The following Object IDs are multipart features or have measure errors.",
                         style=style)
        mmline += 1
        multilist = removevertices()
        for i in multilist:
            if i[3] not in disterrors:
                try:
                    disterrors.append(int(i[3]))
                except:
                    pass
            multisheet.write(mmline, 0, i[0], style=style)
            multisheet.write(mmline, 1, i[1], style=style)
            multisheet.write(mmline, 2, i[2], style=style)
            multisheet.write(mmline, 3, i[3], style=style)
            multisheet.write(mmline, 4, i[4], style=style)
            mmline += 1
    if check7 == "true":
        arcpy.AddMessage("OnSystem Attribute and Geometry & Measure Checks...")
        onsysatt = book.add_sheet("OnSystem Attributes")
        onsysmeas = book.add_sheet("OnSystem Geometry & Measures")
        online = 0
        onsysatt.write(online, 0, "RTE_ID", style=style)
        onsysatt.write(online, 1, "District Number", style=style)
        onsysatt.write(online, 2, "Comparison Field", style=style)
        onsysatt.write(online, 3, "Comparison Field", style=style)
        onsysatt.write(online, 4, "Description", style=style)
        onsysatt.write(online, 6, "The following Object IDs are on-system attribute errors.", style=style)
        onsysmeas.write(online, 0, "RTE_ID", style=style)
        onsysmeas.write(online, 1, "Measures' Length", style=style)
        onsysmeas.write(online, 2, "Shape Length", style=style)
        onsysmeas.write(online, 3, "RTE_LEN", style=style)
        onsysmeas.write(online, 4, "District Name", style=style)
        onsysmeas.write(online, 5, "District Number", style=style)
        onsysmeas.write(online, 6, "Difference", style=style)
        onsysmeas.write(online, 8,
                        "The following Route IDs contain an error between their measures' length, shape length, and RTE_LEN",
                        style=style)
        online += 1
        onsyslist = onsystem()
        atty = onsyslist[0]
        measy = onsyslist[1]
        for i in atty:
            if i[1] not in disterrors:
                try:
                    disterrors.append(int(i[1]))
                except:
                    pass
            onsysatt.write(online, 0, i[0], style=style)
            onsysatt.write(online, 1, i[1], style=style)
            onsysatt.write(online, 2, i[2], style=style)
            onsysatt.write(online, 3, i[3], style=style)
            onsysatt.write(online, 4, i[4], style=style)
            online += 1
        online = 1
        for i in measy:
            if i[5] not in disterrors:
                try:
                    disterrors.append(int(i[5]))
                except:
                    pass
            onsysmeas.write(online, 0, i[0], style=style)
            onsysmeas.write(online, 1, i[1], style=style)
            onsysmeas.write(online, 2, i[2], style=style)
            onsysmeas.write(online, 3, i[3], style=style)
            onsysmeas.write(online, 4, i[4], style=style)
            onsysmeas.write(online, 5, i[5], style=style)
            onsysmeas.write(online, 6, i[6], style=style)
            online += 1
    if check8 == "true":
        arcpy.AddMessage("OffSystem Attribute Checks...")
        offatt = book.add_sheet("OffSystem Attributes")
        oaline = 0
        offatt.write(oaline, 0, "RTE_ID", style=style)
        offatt.write(oaline, 1, "District Number", style=style)
        offatt.write(oaline, 2, "Comparison Field", style=style)
        offatt.write(oaline, 3, "Comparison Field", style=style)
        offatt.write(oaline, 4, "Description", style=style)
        offatt.write(oaline, 6, "The following Object IDs are off-system attribute errors.", style=style)
        oaline += 1
        offattlist = offsysatt()
        for i in offattlist:
            if i[1] not in disterrors and i[1] != "":
                try:
                    disterrors.append(int(i[1]))
                except:
                    pass
            offatt.write(oaline, 0, i[0], style=style)
            offatt.write(oaline, 1, i[1], style=style)
            offatt.write(oaline, 2, i[2], style=style)
            offatt.write(oaline, 3, i[3], style=style)
            offatt.write(oaline, 4, i[4], style=style)
            oaline += 1
    if check9 == "true":
        arcpy.AddMessage("Screen Line Checks...")
        sline = book.add_sheet("Screen Lines")
        scline = 0
        sline.write(scline, 0, "SCREEN_ID", style=style)
        sline.write(scline, 1, "Min_Meas", style=style)
        sline.write(scline, 2, "Max_Meas", style=style)
        sline.write(scline, 3, "Dist_Name", style=style)
        sline.write(scline, 4, "Dist_Nbr", style=style)
        sline.write(scline, 5, "Difference", style=style)
        sline.write(scline, 6, "The following are screen line errors.", style=style)
        scline += 1
        slinelist = screenlines()
        for i in slinelist:
            if i[4] not in disterrors:
                try:
                    disterrors.append(int(i[4]))
                except:
                    pass
            sline.write(scline, 0, i[0], style=style)
            sline.write(scline, 1, i[1], style=style)
            sline.write(scline, 2, i[2], style=style)
            sline.write(scline, 3, i[3], style=style)
            sline.write(scline, 4, i[4], style=style)
            sline.write(scline, 5, i[5], style=style)
            scline += 1
    if check10 == "true":
        arcpy.AddMessage("Off-System Tollroad Attribute Checks...")
        trdatt = book.add_sheet("Tollroad Attributes")
        trdline = 0
        trdatt.write(trdline, 0, "RTE_ID", style=style)
        trdatt.write(trdline, 1, "District Number", style=style)
        trdatt.write(trdline, 2, "Comparison Field", style=style)
        trdatt.write(trdline, 3, "Comparison Field", style=style)
        trdatt.write(trdline, 4, "Description", style=style)
        trdatt.write(trdline, 6, "The following RTE_IDs are tollroad attribute errors.", style=style)
        trdline += 1
        trdattlist = tollrdatt()
        for i in trdattlist:
            if i[1] not in disterrors and i[1] != "":
                try:
                    disterrors.append(int(i[1]))
                except:
                    pass
            trdatt.write(trdline, 0, i[0], style=style)
            trdatt.write(trdline, 1, i[1], style=style)
            trdatt.write(trdline, 2, i[2], style=style)
            trdatt.write(trdline, 3, i[3], style=style)
            trdatt.write(trdline, 4, i[4], style=style)
            trdline += 1
    if check11 == "true":
        arcpy.AddMessage("Federal Road Attribute Checks...")
        fedatt = book.add_sheet("Federal Attributes")
        fedline = 0
        fedatt.write(fedline, 0, "RTE_ID", style=style)
        fedatt.write(fedline, 1, "District Number", style=style)
        fedatt.write(fedline, 2, "Comparison Field", style=style)
        fedatt.write(fedline, 3, "Comparison Field", style=style)
        fedatt.write(fedline, 4, "Description", style=style)
        fedatt.write(fedline, 6, "The following RTE_IDs are federal attribute errors.", style=style)
        fedline += 1
        fedattlist = fedrdatt()
        for i in fedattlist:
            if i[1] not in disterrors and i[1] != "":
                try:
                    disterrors.append(int(i[1]))
                except:
                    pass
            fedatt.write(fedline, 0, i[0], style=style)
            fedatt.write(fedline, 1, i[1], style=style)
            fedatt.write(fedline, 2, i[2], style=style)
            fedatt.write(fedline, 3, i[3], style=style)
            fedatt.write(fedline, 4, i[4], style=style)
            fedline += 1

def copyT():
    try:
        tdrive = "T:\\DATAMGT\\MAPPING\\Data Quality Checks\\Errors_" + str(today)
        shutil.copytree(workspace, tdrive, ignore=shutil.ignore_patterns('*.gdb'))
        print "Copied to T Drive."
    except Exception, e:
        arcpy.AddMessage("Failed to copy to the T-Drive and send emails.")
        f = open(workspace + "\\error.txt", "w")
        issue = repr(e)
        f.write("ISSUE" + issue)
        f.write("DISTERRORS: " + str(disterrors))
        f.close()
        print issue

def email():
    tdrive = "T:\\DATAMGT\\MAPPING\\Data Quality Checks\\Errors_" + str(today)
    analyst = {}
    analyst[1] = 'Tom.Neville@txdot.gov'
    analyst[2] = 'Chris.Bardash@txdot.gov'
    analyst[3] = 'David.Messineo@txdot.gov'
    analyst[4] = 'Richard.Barrientos@txdot.gov'
    analyst[5] = 'Richard.Barrientos@txdot.gov'
    analyst[6] = 'Jason.Ferrell@txdot.gov'
    analyst[7] = 'Jason.Kleinert@txdot.gov'
    analyst[8] = 'Jason.Kleinert@txdot.gov'
    analyst[9] = 'Samuel.Bogle@txdot.gov'
    analyst[10] = 'Jeff.Wilhelm@txdot.gov'
    analyst[11] = 'Jeremy.Rogers@txdot.gov'
    analyst[12] = 'Aja.Davidson@txdot.gov'
    analyst[13] = 'Jennifer.Sylvester@txdot.gov'
    analyst[14] = 'Jennifer.Sylvester@txdot.gov'
    analyst[15] = 'Travis.Scruggs@txdot.gov'
    analyst[16] = 'David.Hickman@txdot.gov'
    analyst[17] = 'Aja.Davidson@txdot.gov'
    analyst[18] = 'Tom.Neville@txdot.gov'
    analyst[19] = 'Jeff.Wilhelm@txdot.gov'
    analyst[20] = 'Jeremy.Rogers@txdot.gov'
    analyst[21] = 'David.Hickman@txdot.gov'
    analyst[22] = 'Travis.Scruggs@txdot.gov'
    analyst[23] = 'Samuel.Bogle@txdot.gov'
    analyst[24] = 'Jason.Ferrell@txdot.gov'
    analyst[25] = 'David.Messineo@txdot.gov'

    TO = []
    for n in disterrors:
        address = analyst[n]
        print address
        if address not in TO:
            TO.append(address)
    print "TO compiled."

    FROM = 'adam.breznicky@txdot.gov'
    SUBJECT = "Error Checks for " + runday
    TEXT = "You are receiving this email because your district(s) was listed within the error checks run on " \
           + runday + ".\nPlease review the error checks report and fix all errors within your district at your" \
                      " earliest convenience.\nYou can find a copy of the Error Checks here:\n\n" \
           + tdrive + "\n\nLove, Adam"
    # SUBJECT = "TEST, you can delete"
    # TEXT = "This is a test. if you have received this email please reply to me confirming that you did.\nI apologize for this series of dud emails. Kinks need workin.\n\nLove, Adam"
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
                """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    username = "adam.breznicky@txdot.gov"
    password = base64.b64decode("U2F0dXJkYXkxMjM=")
    server = smtplib.SMTP('owa.txdot.gov', 25)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.sendmail(FROM, TO, message)
    server.close()
    print "District emails delivered."

    sent = TO
    FROM = 'adam.breznicky@txdot.gov'
    TO = ['adam.breznicky@txdot.gov']
    SUBJECT = "Error Checks for " + runday
    TEXT = "Emails were sent to the following analysts because of errors in their districts:\n" \
           + str(sent) + "\n\nLove, Yourself"
    message = """\From: %s\nTo: %s\nSubject: %s\n\n%s
                """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    username = "adam.breznicky@txdot.gov"
    password = base64.b64decode("U3VuZGF5MTIz")
    server = smtplib.SMTP('owa.txdot.gov', 25)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(username, password)
    server.sendmail(FROM, TO, message)
    server.close()
    print "Email to yourself delivered."

nowS = datetime.datetime.now()
arcpy.AddMessage("and away we go... " + str(nowS))
book = xlwt.Workbook()
copylocal()
assemblereport(allchecks, cityoverlaps, routeopens, offgeommeas, sublen, multimeasPNG, onattmeas, offatt, scnln, offsystoll, federalrds)
print "Saving excel error report..."
book.save(workspace + "\\ErrorReport_" + today + ".xls")
print str(disterrors)
# copyT()
# email()
now = datetime.datetime.now()
arcpy.AddMessage("that's all folks!")
arcpy.AddMessage("started: " + str(nowS))
arcpy.AddMessage("finished: " + str(now))