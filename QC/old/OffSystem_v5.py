__file__ = 'OffSystem_v1'
__date__ = '5/29/14'
__author__ = 'ABREZNIC'

import os, arcpy, xlwt, datetime, math

#date
now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + "_" + curMonth + "_" + curDay

#variables
qcfolder = "C:\\TxDOT\\QC\\OffSystem"
workspace = qcfolder + "\\" + today
where = """ RTE_CLASS = '2' OR RTE_CLASS = '3'  """
database = workspace + "\\Comanche_Copy.gdb"
roadways = database + "\\TXDOT_Roadways"
subfiles = database + "\\SUBFILES"
cities = database + "\\City"
districts = database + "\\District"

if not os.path.exists(workspace):
    os.makedirs(workspace)
else:
    arcpy.Delete_management(database)
    for file in os.listdir(workspace):
        thefile = os.path.join(workspace, file)
        os.remove(thefile)

txdotroads = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
txdotsubs = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
txdotcity = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.City\\TPP_GIS.APP_TPP_GIS_ADMIN.City"
txdotdist = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.District\\TPP_GIS.APP_TPP_GIS_ADMIN.District"

def copylocal():
    arcpy.CreateFileGDB_management(workspace, "Comanche_Copy.gdb")
    arcpy.TableSelect_analysis(txdotsubs, subfiles, "(SUBFILE = 2 AND ADMIN_SYSTEM <> 8) OR SUBFILE = 3")
    arcpy.Copy_management(txdotcity, cities)
    arcpy.Copy_management(txdotdist, districts)
    arcpy.SpatialJoin_analysis(txdotroads, districts, roadways)

def overlap():
    arcpy.Select_analysis(roadways, database + "\\FC_Streets", """ RTE_CLASS = '3' """)
    arcpy.Erase_analysis(database + "\\FC_Streets", cities, database + "\\FC_Streets_Errors")
    arcpy.Clip_analysis(roadways, cities, database + "\\City_Roads")
    arcpy.Select_analysis(database + "\\City_Roads", database + "\\County_Roads_Errors", """ RTE_CLASS = '2' """)

    arcpy.Merge_management([database + "\\County_Roads_Errors", database + "\\FC_Streets_Errors"],
                           database + "\\MergedErrors")
    arcpy.SpatialJoin_analysis(database + "\\MergedErrors", districts, workspace + "\\City_OverlapErrors.shp")

    arcpy.Delete_management(database + "\\City_Roads")
    arcpy.Delete_management(database + "\\FC_Streets")
    arcpy.Delete_management(database + "\\County_Roads_Errors")
    arcpy.Delete_management(database + "\\FC_Streets_Errors")
    arcpy.Delete_management(database + "\\MergedErrors")

    errors = []
    cursor = arcpy.UpdateCursor(workspace + "\\City_OverlapErrors.shp")
    counter = 0
    for row in cursor:
        geom = row.shape
        len = geom.length * .000621371
        if len < .003:
            cursor.deleteRow(row)
        else:
            row.setValue("RTE_LEN", len)
            cursor.updateRow(row)
            rowinfo = [row.RTE_ID, row.RTE_LEN, row.DIST_NM, row.DIST_NBR]
            errors.append(rowinfo)
            counter += 1
    print str(counter) + " overlap errors."
    del cursor
    del row
    return errors

def routeopen():
    errors = []
    openstatus = {}
    counter = 0
    cursor = arcpy.SearchCursor(roadways, where)
    for row in cursor:
        id = row.RTE_ID
        if id is not None and id != "":
            open = str(row.RTE_OPEN)
            length = row.RTE_LEN
            key = id + "=" + open
            if key not in openstatus.keys():
                openstatus[key] = length
            else:
                openstatus[key] = openstatus[key] + length
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
    print str(counter) + " null/bad RouteID errors."
    del cursor
    counter = 0
    hwystatus = {}
    cursor = arcpy.SearchCursor(subfiles)
    for row in cursor:
        id = row.RTE_ID
        length = row.LEN_OF_SECTION
        status = row.HIGHWAY_STATUS
        if status == 4:
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
    del cursor
    for key in openstatus.keys():
        if key in hwystatus.keys():
            linelen = openstatus[key]
            sublen = hwystatus[key]
            id = key.split("=")[0]
            open = key.split("=")[1]
            if abs(linelen - sublen) > .004:
                errorinfo = []
                errorinfo.append(id)
                errorinfo.append(open)
                errorinfo.append("N/A")
                errorinfo.append("Length error. RTE_ID in TxDOT_Roadways with this RTE_OPEN does not match SUBFILES'")
                errorinfo.append(row.DISTRICT)
                errors.append(errorinfo)
                counter += 1
            else:
                pass
        else:
            id = key.split("=")[0]
            open = key.split("=")[1]
            errorinfo = []
            errorinfo.append(id)
            errorinfo.append(open)
            errorinfo.append("N/A")
            errorinfo.append("RTE_ID in TxDOT_Roadways with this RTE_OPEN does not match SUBFILES' HIGHWAY_STATUS")
            errorinfo.append(row.DISTRICT)
            errors.append(errorinfo)
            counter += 1
    print str(counter) + " subfile vs roadways Route Open errors."
    return errors

def measurelength():
    counter = 0
    cursor = arcpy.SearchCursor(roadways, where)
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
        shp_len = round(wholelen, 3)
        rte_len = row.RTE_LEN

        testlen = abs(shp_len - Mdiff)
        if rte_len is not None and id is not None:
            if testlen <= .003 and abs(rte_len - shp_len) > .003:
                oid = row.OBJECTID
                print "RTE_LEN: " + str(oid) + "," + str(rte_len) + "," + str(shp_len) + "," + str(Mdiff)
                # cur = arcpy.UpdateCursor(txdotroads, "OBJECTID = " + oid)
                # for i in cur:
                #     i.setValue("RTE_LEN", wholelen)
                #     cur.updateRow(i)
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
    print str(counter) + " measure length errors."
    del cursor
    del row
    return errors

def roadwaydict():
    errors = []
    counter = 0
    print "Creating dictionary"
    dictionary = {}
    cursor = arcpy.SearchCursor(roadways, where)
    for row in cursor:
        id = row.RTE_ID
        if row.RTE_LEN is not None:
            len = row.RTE_LEN
        else:
            len = 0
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
            errorinfo.append("NO RTE_LEN POPULATED. OBJECTID: " + oid)
            errors.append(errorinfo)
            counter += 1
        geom = row.shape
        ext = geom.extent
        Mmin = round(ext.MMin, 3)
        Mmax = round(ext.MMax, 3)
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
    del cursor
    del row
    print "Dictionary complete"
    print str(counter) + " null RTE_ID and RTE_LEN errors"
    theball = [errors, dictionary]
    return theball

def subfilelength():
    theball = roadwaydict()
    errors = theball[0]
    dictionary = theball[1]
    now1 = datetime.datetime.now()
    counto = int(arcpy.GetCount_management(subfiles).getOutput(0))
    total = counto - 1
    starter = 0
    counter = 0
    previous = ""
    cursor = arcpy.SearchCursor(subfiles, "", "", "", "RTE_ID A; BMP A")
    for row in cursor:
        id = row.RTE_ID
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
                    errorinfo.append("BMP and EMP difference does not equal the LEN_OF_SECTION. SUBFILE OID: " + str(row.OBJECTID))
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
                    errorinfo.append("BMP and EMP difference does not equal the LEN_OF_SECTION. SUBFILE OID: " + str(row.OBJECTID))
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
                    errorinfo.append("BMP and EMP difference does not equal the LEN_OF_SECTION. SUBFILE OID: " + str(row.OBJECTID))
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
                    errorinfo.append("BMP and EMP difference does not equal the LEN_OF_SECTION. SUBFILE OID: " + str(row.OBJECTID))
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
                    errorinfo.append("BMP and EMP difference does not equal the LEN_OF_SECTION. SUBFILE OID: " + str(row.OBJECTID))
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
            print str(starter) + "/" + str(total)

        else:
            starter += 1
            print str(starter) + "/" + str(total)
            pass
    then = datetime.datetime.now()
    print str(now1)
    print "Update Done. " + str(then)
    print str(counter) + " subfile length errors."
    return errors

def removevertices():
    counter = 0
    errors = []
    spatialRef = arcpy.Describe(txdotroads).spatialReference
    cursor = arcpy.SearchCursor(txdotroads, where)
    for row in cursor:
        errorinfo = []
        geom = row.shape
        allparts = geom.getPart()
        if allparts.count > 1:
            errorinfo.append(row.OBJECTID)
            errorinfo.append(row.RTE_ID)
            errorinfo.append(row.DIST_NM)
            errorinfo.append(row.DIST_NBR)
            errors.append(errorinfo)
            counter += 1
        partAry = arcpy.Array()
        srtpnt = 0
        lastX = 0
        lastY = 0
        for part in allparts:
            ary = arcpy.Array()
            for pnt in part:
                if srtpnt == 0:
                    x = pnt.X
                    y = pnt.Y
                    m = pnt.M
                    nupnt = arcpy.Point(x, y, 0, m)
                    ary.add(nupnt)
                    lastX = x
                    lastY = y
                    srtpnt += 1
                else:
                    x = pnt.X
                    y = pnt.Y
                    m = pnt.M
                    newM = (math.sqrt((abs(x - lastX)) ** 2 + (abs(y - lastY)) ** 2))
                    newMiles = newM * .000621371
                    if newMiles >= .001 and pnt.ID != len(part):
                        nupnt = arcpy.Point(x, y, 0, m)
                        ary.add(nupnt)
                        lastX = x
                        lastY = y
                    elif newMiles < .001 and pnt.ID == len(part):
                        ary.remove(-1)
                        nupnt = arcpy.Point(x, y, 0, m)
                        ary.add(nupnt)
                    elif newMiles >= .001 and pnt.ID == len(part):
                        nupnt = arcpy.Point(x, y, 0, m)
                        ary.add(nupnt)
            partAry.add(ary)
        row.shape - arcpy.Polyline(partAry, spatialRef, False, True)
        cursor.updateRow(row)
    print str(counter) + " multipart errors."
    return errors

def assemblereport():
    print "Copying data local..."
    copylocal()
    book = xlwt.Workbook()
    print "Overlap Errors..."
    overlapsheet = book.add_sheet("City Boundary Overlap")
    line = 0
    overlapsheet.write(line, 0, "RTE_ID")
    overlapsheet.write(line, 1, "Overlap Length")
    overlapsheet.write(line, 2, "District Name")
    overlapsheet.write(line, 3, "District Number")
    overlapsheet.write(line, 5,
                       "The following Route IDs are County Roads and FC Streets which cross a City Boundary as found in City_OverlapErrors.shp")
    line += 1
    overlaplist = overlap()
    for i in overlaplist:
        overlapsheet.write(line, 0, i[0])
        overlapsheet.write(line, 1, i[1])
        overlapsheet.write(line, 2, i[2])
        overlapsheet.write(line, 3, i[3])
        line += 1
    print "Route Open Errors..."
    opensheet = book.add_sheet("Route Open")
    line = 0
    opensheet.write(line, 0, "RTE_ID")
    opensheet.write(line, 1, "RTE_OPEN")
    opensheet.write(line, 2, "HIGHWAY_STATUS")
    opensheet.write(line, 3, "Description")
    opensheet.write(line, 4, "District Number")
    opensheet.write(line, 6,
                    "The following Route IDs contain an error between RTE_OPEN in TxDOT_Roadways and ROADWAY_STATUS in SUBFILES")
    line += 1
    openlist = routeopen()
    for i in openlist:
        opensheet.write(line, 0, i[0])
        opensheet.write(line, 1, i[1])
        opensheet.write(line, 2, i[2])
        opensheet.write(line, 3, i[3])
        opensheet.write(line, 4, i[4])
        line += 1
    print "Geometry and Measure Errors..."
    geomsheet = book.add_sheet("Geometry and Measures")
    line = 0
    geomsheet.write(line, 0, "RTE_ID")
    geomsheet.write(line, 1, "Measures' Length")
    geomsheet.write(line, 2, "Shape Length")
    geomsheet.write(line, 3, "RTE_LEN")
    geomsheet.write(line, 4, "District Name")
    geomsheet.write(line, 5, "District Number")
    geomsheet.write(line, 6, "Difference")
    geomsheet.write(line, 8,
                    "The following Route IDs contain an error between their measures' length, shape length, and RTE_LEN")
    line += 1
    geomlist = measurelength()
    for i in geomlist:
        geomsheet.write(line, 0, i[0])
        geomsheet.write(line, 1, i[1])
        geomsheet.write(line, 2, i[2])
        geomsheet.write(line, 3, i[3])
        geomsheet.write(line, 4, i[4])
        geomsheet.write(line, 5, i[5])
        geomsheet.write(line, 6, i[6])
        line += 1
    print "Subfile Length Errors..."
    subsheet = book.add_sheet("Subfile Lengths")
    line = 0
    subsheet.write(line, 0, "RTE_ID")
    subsheet.write(line, 1, "District Number")
    subsheet.write(line, 2, "BMP")
    subsheet.write(line, 3, "Min Measure")
    subsheet.write(line, 4, "EMP")
    subsheet.write(line, 5, "Max Measure")
    subsheet.write(line, 6, "Subfile Len")
    subsheet.write(line, 7, "RTE_LEN")
    subsheet.write(line, 8, "Description")
    subsheet.write(line, 10, "The following Route IDs contain an error between their line and SUBFILES lengths")
    line += 1
    sublist = subfilelength()
    for i in sublist:
        subsheet.write(line, 0, i[0])
        subsheet.write(line, 1, i[1])
        subsheet.write(line, 2, i[2])
        subsheet.write(line, 3, i[3])
        subsheet.write(line, 4, i[4])
        subsheet.write(line, 5, i[5])
        subsheet.write(line, 6, i[6])
        subsheet.write(line, 7, i[7])
        subsheet.write(line, 8, i[8])
        line += 1
    # print "Multipart Errors..."
    # multisheet = book.add_sheet("Multipart & Geometry Errors")
    # line = 0
    # multisheet.write(line, 0, "OBJECTID")
    # multisheet.write(line, 1, "RTE_ID")
    # multisheet.write(line, 2, "District Name")
    # multisheet.write(line, 3, "District Number")
    # multisheet.write(line, 5, "The following Object IDs are multipart features or have measure errors.")
    # line += 1
    # multilist = removevertices()
    # for i in multilist:
    #     multisheet.write(line, 0, i[0])
    #     multisheet.write(line, 1, i[1])
    #     multisheet.write(line, 2, i[2])
    #     multisheet.write(line, 3, i[3])
    #     line += 1
    book.save(workspace + "\\ErrorReport_" + today + ".xls")


nowS = datetime.datetime.now()
print "and away we go... " + str(nowS)
assemblereport()
now = datetime.datetime.now()
print "started " + str(nowS)
print "that's all folks!" + str(now)