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
# check0 = arcpy.GetParameterAsText(0)
# check1 = arcpy.GetParameterAsText(1)
# check2 = arcpy.GetParameterAsText(2)
# check3 = arcpy.GetParameterAsText(3)
# check4 = arcpy.GetParameterAsText(4)
# check5 = arcpy.GetParameterAsText(5)
# check6 = arcpy.GetParameterAsText(6)
# check7 = arcpy.GetParameterAsText(7)
# check8 = arcpy.GetParameterAsText(8)
# check9 = arcpy.GetParameterAsText(9)
check0 = "C:\\TxDOT\\Scripts\\QC\\Error Checks"
check1 = "false"
check2 = "false"
check3 = "false"
check4 = "false"
check5 = "false"
check6 = "false"
check7 = "true"
check8 = "true"
check9 = "true"

if check1 != "true":
    check1 = "false"
if check2 != "true":
    check2 = "false"
if check3 != "true":
    check3 = "false"
if check4 != "true":
    check4 = "false"
if check5 != "true":
    check5 = "false"
if check6 != "true":
    check6 = "false"
if check7 != "true":
    check7 = "false"
if check8 != "true":
    check8 = "false"
if check9 != "true":
    check9 = "false"

qcfolder = check0
workspace = qcfolder + "\\" + today
where = """ ( RDBD_TYPE = 'CNCTR-GS' AND RTE_CLASS = '1' ) OR( (RTE_CLASS = '2' OR RTE_CLASS = '3') AND RDBD_TYPE = 'KG' AND RTE_CLASS <> '8' )  """
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
    arcpy.TableToTable_conversion(txdotsubs, database, "SUBFILES")
    # arcpy.TableSelect_analysis(txdotsubs, subfiles, "(SUBFILE = 2 AND ADMIN_SYSTEM <> 8) OR SUBFILE = 3 OR SUBFILE = 1")
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
    arcpy.AddMessage(str(counter) + " overlap errors.")
    del cursor
    del row
    return errors

def routeopen():
    errors = []
    openstatus = {}
    counter = 0
    whereto = """ ( RDBD_TYPE = 'CNCTR-GS' AND RTE_CLASS = '1' ) OR( (RTE_CLASS = '2' OR RTE_CLASS = '3') AND RDBD_TYPE = 'KG' AND RTE_CLASS <> '8' ) OR( RTE_NM = '183A' AND RTE_ID LIKE '183A-%')  """
    cursor = arcpy.SearchCursor(roadways, whereto)
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
    arcpy.AddMessage(str(counter) + " null/bad RouteID errors.")
    del cursor
    counter = 0
    hwystatus = {}
    cursor = arcpy.SearchCursor(subfiles, "(SUBFILE = 2 AND ADMIN_SYSTEM <> 8) OR SUBFILE = 3 OR SUBFILE = 1")
    for row in cursor:
        id = row.RTE_ID
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
    del cursor
    for key in openstatus.keys():
        if key in hwystatus.keys():
            linelen = openstatus[key]
            sublen = hwystatus[key]
            id = key.split("=")[0]
            open = key.split("=")[1]
            if abs(linelen - sublen) > .004:
                cursor = arcpy.SearchCursor(subfiles,"RTE_ID = '"+id+"'")
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
                    errorinfo.append("")
                    errors.append(errorinfo)
                    arcpy.AddMessage("check out: " + str(id))
                counter += 1
            else:
                pass
        else:
            id = key.split("=")[0]
            open = key.split("=")[1]
            cursor = arcpy.SearchCursor(subfiles,"RTE_ID = '"+id+"'")
            for row in cursor:
                Dist_Num = row.DISTRICT
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
                errorinfo.append("")
                errors.append(errorinfo)
                arcpy.AddMessage("check out: " + str(id))
            counter += 1
    arcpy.AddMessage(str(counter) + " subfile vs roadways Route Open errors.")
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
        shp_len = format(float(wholelen), '.3f')
        rte_len = row.RTE_LEN

        testlen = abs(shp_len - Mdiff)
        if rte_len is not None and id is not None:
            if testlen <= .003 and abs(rte_len - shp_len) > .003:
                oid = str(row.OBJECTID)
                arcpy.AddMessage("RTE_LEN replaced: " + str(oid) + "," + str(rte_len) + "," + str(shp_len) + "," + str(Mdiff))
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
                errorinfo.append(abs(shp_len - Mdiff))
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
    arcpy.AddMessage("Creating dictionary")
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
        Mmin = format(float(ext.MMin), '.3f')
        Mmax = format(float(ext.MMax), '.3f')
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
    arcpy.AddMessage("Dictionary complete")
    arcpy.AddMessage(str(counter) + " null RTE_ID and RTE_LEN errors")
    theball = [errors, dictionary]
    return theball

def subfilelength():
    theball = roadwaydict()
    errors = theball[0]
    dictionary = theball[1]
    now1 = datetime.datetime.now()
    total = 0
    cursor = arcpy.SearchCursor(subfiles, "(SUBFILE = 2 AND ADMIN_SYSTEM <> 8) OR SUBFILE = 3 OR SUBFILE = 1")
    for row in cursor:
        total += 1
    del cursor
    del row
    # counto = int(arcpy.GetCount_management(subfiles).getOutput(0))
    # total = counto - 1
    starter = 0
    counter = 0
    previous = ""
    cursor = arcpy.SearchCursor(subfiles, "(SUBFILE = 2 AND ADMIN_SYSTEM <> 8) OR SUBFILE = 3 OR SUBFILE = 1", "", "", "RTE_ID A; BMP A")
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
            arcpy.AddMessage(str(starter) + "/" + str(total))

        else:
            starter += 1
            arcpy.AddMessage(str(starter) + "/" + str(total))
            pass
    then = datetime.datetime.now()
    arcpy.AddMessage(str(now1))
    arcpy.AddMessage("Update Done. " + str(then))
    arcpy.AddMessage(str(counter) + " subfile length errors.")
    return errors

def removevertices():
    counter = 0
    errors = []
    query = """ RDBD_TYPE <> 'CNCTR-GS' AND RDBD_TYPE <> 'CONNECTOR' AND RDBD_TYPE <> 'OTHER' AND RDBD_TYPE <> 'RAMP' AND RDBD_TYPE <> 'TURNAROUND'  """
    cursor = arcpy.SearchCursor(roadways, query)
    for row in cursor:
        geom = row.shape
        allparts = geom.getPart()
        if allparts.count > 1:
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
    arcpy.mapping.ExportToPNG(mxd,workspace + "\\Measure Errors " + str(today) + ".png")
    del mxd
    arcpy.AddMessage("Exporting 2 of 3...")
    mxd = arcpy.mapping.MapDocument("T:\\DATAMGT\\MAPPING\\Data Quality Checks\\Error_Check_Scripts\\MeasureErrors_LG_XG.mxd")
    arcpy.mapping.ExportToPNG(mxd,workspace + "\\Measure LG XG Red is Bad " + str(today) + ".png")
    del mxd
    arcpy.AddMessage("Exporting 3 of 3...")
    mxd = arcpy.mapping.MapDocument("T:\\DATAMGT\\MAPPING\\Data Quality Checks\\Error_Check_Scripts\\MeasureErrors_Not_LG_XG.mxd")
    arcpy.mapping.ExportToPNG(mxd,workspace + "\\Measure RG AG Red is Bad " + str(today) + ".png")
    del mxd

    return errors

def onsystem():
    counter = 0
    atterrors = []
    measerrors = []
    query = """ (RTE_CLASS ='1' or RTE_CLASS ='6') AND RDBD_TYPE <> 'RAMP' AND RDBD_TYPE <> 'TURNAROUND' AND RDBD_TYPE <> 'CONNECTOR' """
    cursor = arcpy.SearchCursor(roadways, query)
    for row in cursor:
        # try:
        print row.RTE_ID
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
                oid = str(row.OBJECTID)
                arcpy.AddMessage("RTE_LEN replaced: " + str(oid) + "," + str(rte_len) + "," + str(shp_len) + "," + str(Mdiff))
                # cur = arcpy.UpdateCursor(txdotroads, "OBJECTID = " + oid)
                # for i in cur:
                #     i.setValue("RTE_LEN", wholelen)
                #     cur.updateRow(i)
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
            errorinfo = []
            errorinfo.append("OID: " + oid)
            errorinfo.append(str(Mdiff))
            errorinfo.append(str(shp_len))
            errorinfo.append(str(rte_len))
            errorinfo.append(row.DIST_NM)
            errorinfo.append(row.DIST_NBR)
            errorinfo.append("")
            measerrors.append(errorinfo)
            counter += 1
        # except:
        #     errorinfo = []
        #     errorinfo.append(id)
        #     errorinfo.append("OBJECTID = '" + str(row.OBJECTID) + "'")
        #     errorinfo.append("")
        #     errorinfo.append("")
        #     errorinfo.append(row.DIST_NM)
        #     errorinfo.append(row.DIST_NBR)
        #     errorinfo.append("ERROR in geometry? Maybe measures? Investigate!")
        #     measerrors.append(errorinfo)
        #     counter += 1


    arcpy.AddMessage(str(counter) + " on system attribute and measure errors.")
    errors = [atterrors, measerrors]
    return errors

def offsysatt():
    counter = 0
    errors = []
    query = """ (RTE_CLASS = '2' OR RTE_CLASS = '3') AND RDBD_TYPE = 'KG' """
    cursor = arcpy.SearchCursor(roadways, query)
    for row in cursor:
        if row.RTE_CLASS == '2':
            nmpfx1 = row.RTE_NM[3:5]
            nmpfx2 = row.RTE_NM[3:4]
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

            if len(row.RTE_NBR) == 1:
                txtRTE_NBR = "000" + row.RTE_NBR
            elif len(row.RTE_NBR) == 2:
                txtRTE_NBR = "00" + row.RTE_NBR
            elif len(row.RTE_NBR) == 3:
                txtRTE_NBR = "0" + row.RTE_NBR
            else:
                txtRTE_NBR = row.RTE_NBR
            nmnbr1 = row.RTE_NM[5:9]
            nmnbr2 = row.RTE_NM[4:9]
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
                errorinfo.append("RTE_PRFX inconsistent with RTE_CLASS")
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
            if len(row.RTE_ID) > 6:
                errorinfo = []
                errorinfo.append(row.RTE_ID)
                errorinfo.append(row.DIST_NBR)
                errorinfo.append(row.RTE_ID)
                errorinfo.append(row.RTE_CLASS)
                errorinfo.append("RTE_ID should not be more than 6 characters long")
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
                errorinfo.append("RTE_NBR should be blank")
                errors.append(errorinfo)
                counter += 1

    arcpy.AddMessage(str(counter) + " off system attribute errors.")
    for i in errors:
        print i[0] + "," + i[4]
    return errors

def screenlines():
    comancheSL = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.QAQC\\TPP_GIS.APP_TPP_GIS_ADMIN.Screen_Lines"
    Screen_Lines = database + "\\Screen_Lines"
    Screen_Join_Output_shp = database + "\\Screen_Join_Output"
    OnSystem_Roadways = database + "\\OnSystem_Roadways"
    Screen_Line_Intersect_shp = database + "\\Screen_Line_Intersect"
    Screen_Line_Result_dbf = database + "\\Screen_Line_Result"
    Screen_Lines_Summarized_dbf = database + "\\Screen_Lines_Summarized"
    Output_Event_Table_Properties = "RID POINT MEAS"

    print "Exporting Screen Lines"
    arcpy.FeatureClassToFeatureClass_conversion(comancheSL, database, "Screen_Lines")
    print "Joining with Districts from Comanche"
    arcpy.SpatialJoin_analysis(Screen_Lines, districts, Screen_Join_Output_shp, "JOIN_ONE_TO_ONE", "KEEP_ALL")
    print "Exporting On-System Roadways"
    arcpy.FeatureClassToFeatureClass_conversion(roadways, database, "OnSystem_Roadways", """RTE_CLASS = '1' AND RTE_OPEN = 1""")
    print "Intersecting Screen Lines with Roadbeds"
    arcpy.Intersect_analysis([OnSystem_Roadways, Screen_Join_Output_shp], Screen_Line_Intersect_shp,"ALL", "", "POINT")
    print "Locating Points along Routes"
    arcpy.LocateFeaturesAlongRoutes_lr(Screen_Line_Intersect_shp, OnSystem_Roadways, "RTE_ID", "0 Meters", Screen_Line_Result_dbf, Output_Event_Table_Properties, "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
    print "Calculating Summary Statistics"
    arcpy.Statistics_analysis(Screen_Line_Result_dbf, Screen_Lines_Summarized_dbf, "MEAS MIN;MEAS MAX;DIST_NM FIRST", "SCREEN_ID")
    print "Adding Difference Column"
    arcpy.AddField_management(Screen_Lines_Summarized_dbf, "DIFFERENCE", "FLOAT")
    # print "Calculating Difference Column"
    # arcpy.CalculateField_management(Screen_Lines_Summarized_dbf, "DIFFERENCE", "Abs ([MAX_MEAS]- [MIN_MEAS])", "VB", "")
    print "Compiling Errors"
    errors = []
    cursor = arcpy.UpdateCursor(Screen_Lines_Summarized_dbf)
    for row in cursor:
        screen = row.getValue("SCREEN_ID")
        minimum = row.getValue("MIN_MEAS")
        maximum = row.getValue("MAX_MEAS")
        dist = row.getValue("FIRST_DIST_NM")
        diff = abs(maximum - minimum)
        thediff = format(float(diff), '.3f')
        thisrow = [str(screen), str(minimum), str(maximum), str(dist), str(thediff)]
        errors.append(thisrow)
        row.setValue("DIFFERENCE", thediff)
        cursor.updateRow(row)
    del cursor
    del row
    return errors

def proc2(style):
    arcpy.AddMessage("Overlap Errors...")
    overlapsheet = book.add_sheet("City Boundary Overlap")
    line = 0
    overlapsheet.write(line, 0, "RTE_ID", style = style)
    overlapsheet.write(line, 1, "Overlap Length", style = style)
    overlapsheet.write(line, 2, "District Name", style = style)
    overlapsheet.write(line, 3, "District Number", style = style)
    overlapsheet.write(line, 5,
                       "The following Route IDs are County Roads and FC Streets which cross a City Boundary as found in City_OverlapErrors.shp", style = style)
    line += 1
    overlaplist = overlap()
    for i in overlaplist:
        overlapsheet.write(line, 0, i[0], style = style)
        overlapsheet.write(line, 1, i[1], style = style)
        overlapsheet.write(line, 2, i[2], style = style)
        overlapsheet.write(line, 3, i[3], style = style)
        line += 1
def proc3(style):
    arcpy.AddMessage("Route Open Errors...")
    opensheet = book.add_sheet("Route Open")
    line = 0
    opensheet.write(line, 0, "RTE_ID", style = style)
    opensheet.write(line, 1, "RTE_OPEN", style = style)
    opensheet.write(line, 2, "HIGHWAY_STATUS", style = style)
    opensheet.write(line, 3, "Description", style = style)
    opensheet.write(line, 4, "District Number", style = style)
    opensheet.write(line, 6,
                    "The following Route IDs contain an error between RTE_OPEN in TxDOT_Roadways and ROADWAY_STATUS in SUBFILES", style = style)
    line += 1
    openlist = routeopen()
    for i in openlist:
        opensheet.write(line, 0, i[0], style = style)
        opensheet.write(line, 1, i[1], style = style)
        opensheet.write(line, 2, i[2], style = style)
        opensheet.write(line, 3, i[3], style = style)
        opensheet.write(line, 4, i[4], style = style)
        line += 1
def proc4(style):
    arcpy.AddMessage("OffSystem Geometry & Measure Errors...")
    geomsheet = book.add_sheet("OffSystem Geometry & Measures")
    line = 0
    geomsheet.write(line, 0, "RTE_ID", style = style)
    geomsheet.write(line, 1, "Measures' Length", style = style)
    geomsheet.write(line, 2, "Shape Length", style = style)
    geomsheet.write(line, 3, "RTE_LEN", style = style)
    geomsheet.write(line, 4, "District Name", style = style)
    geomsheet.write(line, 5, "District Number", style = style)
    geomsheet.write(line, 6, "Difference", style = style)
    geomsheet.write(line, 8,
                    "The following Route IDs contain an error between their measures' length, shape length, and RTE_LEN", style = style)
    line += 1
    geomlist = measurelength()
    for i in geomlist:
        geomsheet.write(line, 0, i[0], style = style)
        geomsheet.write(line, 1, i[1], style = style)
        geomsheet.write(line, 2, i[2], style = style)
        geomsheet.write(line, 3, i[3], style = style)
        geomsheet.write(line, 4, i[4], style = style)
        geomsheet.write(line, 5, i[5], style = style)
        geomsheet.write(line, 6, i[6], style = style)
        line += 1
def proc5(style):
    arcpy.AddMessage("Subfile Length Errors...")
    subsheet = book.add_sheet("Subfile Lengths")
    line = 0
    subsheet.write(line, 0, "RTE_ID", style = style)
    subsheet.write(line, 1, "District Number", style = style)
    subsheet.write(line, 2, "BMP", style = style)
    subsheet.write(line, 3, "Min Measure", style = style)
    subsheet.write(line, 4, "EMP", style = style)
    subsheet.write(line, 5, "Max Measure", style = style)
    subsheet.write(line, 6, "Subfile Len", style = style)
    subsheet.write(line, 7, "RTE_LEN", style = style)
    subsheet.write(line, 8, "Description", style = style)
    subsheet.write(line, 10, "The following Route IDs contain an error between their line and SUBFILES lengths", style = style)
    line += 1
    sublist = subfilelength()
    for i in sublist:
        subsheet.write(line, 0, i[0], style = style)
        subsheet.write(line, 1, i[1], style = style)
        subsheet.write(line, 2, i[2], style = style)
        subsheet.write(line, 3, i[3], style = style)
        subsheet.write(line, 4, i[4], style = style)
        subsheet.write(line, 5, i[5], style = style)
        subsheet.write(line, 6, i[6], style = style)
        subsheet.write(line, 7, i[7], style = style)
        subsheet.write(line, 8, i[8], style = style)
        line += 1
def proc6(style):
    arcpy.AddMessage("Multipart Errors and Measure Errors...")
    multisheet = book.add_sheet("Multipart & Measure Errors")
    line = 0
    multisheet.write(line, 0, "OBJECTID", style = style)
    multisheet.write(line, 1, "RTE_ID", style = style)
    multisheet.write(line, 2, "District Name", style = style)
    multisheet.write(line, 3, "District Number", style = style)
    multisheet.write(line, 4, "Description", style = style)
    multisheet.write(line, 6, "The following Object IDs are multipart features or have measure errors.", style = style)
    line += 1
    multilist = removevertices()
    for i in multilist:
        multisheet.write(line, 0, i[0], style = style)
        multisheet.write(line, 1, i[1], style = style)
        multisheet.write(line, 2, i[2], style = style)
        multisheet.write(line, 3, i[3], style = style)
        multisheet.write(line, 4, i[4], style = style)
        line += 1
def proc7(style):
    arcpy.AddMessage("OnSystem Attribute and Geometry & Measure Checks...")
    onsysatt = book.add_sheet("OnSystem Attributes")
    onsysmeas = book.add_sheet("OnSystem Geometry & Measures")
    line = 0
    onsysatt.write(line, 0, "RTE_ID", style = style)
    onsysatt.write(line, 1, "District Number", style = style)
    onsysatt.write(line, 2, "Comparison Field", style = style)
    onsysatt.write(line, 3, "Comparison Field", style = style)
    onsysatt.write(line, 4, "Description", style = style)
    onsysatt.write(line, 6, "The following Object IDs are on-system attribute errors.", style = style)
    onsysmeas.write(line, 0, "RTE_ID", style = style)
    onsysmeas.write(line, 1, "Measures' Length", style = style)
    onsysmeas.write(line, 2, "Shape Length", style = style)
    onsysmeas.write(line, 3, "RTE_LEN", style = style)
    onsysmeas.write(line, 4, "District Name", style = style)
    onsysmeas.write(line, 5, "District Number", style = style)
    onsysmeas.write(line, 6, "Difference", style = style)
    onsysmeas.write(line, 8,
                    "The following Route IDs contain an error between their measures' length, shape length, and RTE_LEN", style = style)
    line += 1
    onsyslist = onsystem()
    atty = onsyslist[0]
    measy = onsyslist[1]
    for i in atty:
        onsysatt.write(line, 0, i[0], style = style)
        onsysatt.write(line, 1, i[1], style = style)
        onsysatt.write(line, 2, i[2], style = style)
        onsysatt.write(line, 3, i[3], style = style)
        onsysatt.write(line, 4, i[4], style = style)
        line += 1
    line = 1
    for i in measy:
        onsysmeas.write(line, 0, i[0], style = style)
        onsysmeas.write(line, 1, i[1], style = style)
        onsysmeas.write(line, 2, i[2], style = style)
        onsysmeas.write(line, 3, i[3], style = style)
        onsysmeas.write(line, 4, i[4], style = style)
        onsysmeas.write(line, 5, i[5], style = style)
        onsysmeas.write(line, 6, i[6], style = style)
        line += 1
def proc8(style):
    arcpy.AddMessage("OffSystem Attribute Checks...")
    offatt = book.add_sheet("OffSystem Attributes")
    line = 0
    offatt.write(line, 0, "RTE_ID", style = style)
    offatt.write(line, 1, "District Number", style = style)
    offatt.write(line, 2, "Comparison Field", style = style)
    offatt.write(line, 3, "Comparison Field", style = style)
    offatt.write(line, 4, "Description", style = style)
    offatt.write(line, 6, "The following Object IDs are off-system attribute errors.", style = style)
    line += 1
    offattlist = offsysatt()
    for i in offattlist:
        offatt.write(line, 0, i[0], style = style)
        offatt.write(line, 1, i[1], style = style)
        offatt.write(line, 2, i[2], style = style)
        offatt.write(line, 3, i[3], style = style)
        offatt.write(line, 4, i[4], style = style)
        line += 1
def proc9(style):
    arcpy.AddMessage("Screen Line Checks...")
    sline = book.add_sheet("Screen Lines")
    line = 0
    sline.write(line, 0, "SCREEN_ID", style = style)
    sline.write(line, 1, "Min_Meas", style = style)
    sline.write(line, 2, "Max_Meas", style = style)
    sline.write(line, 3, "Dist_Name", style = style)
    sline.write(line, 4, "Difference", style = style)
    sline.write(line, 6, "The following are screen line errors.", style = style)
    line += 1
    slinelist = screenlines()
    for i in slinelist:
        sline.write(line, 0, i[0], style = style)
        sline.write(line, 1, i[1], style = style)
        sline.write(line, 2, i[2], style = style)
        sline.write(line, 3, i[3], style = style)
        sline.write(line, 4, i[4], style = style)
        line += 1

def assemblereport(check1, check2, check3, check4, check5, check6, check7, check8, check9):
    arcpy.AddMessage("Copying data local...")
    copylocal()
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

    font = xlwt.Font() # Create the Font
    font.name = 'Calibri'
    font.height = 240 # =point size you want * 20
    style = xlwt.XFStyle() # Create the Style
    style.font = font # Apply the Font to the Style

    if check2 == "true":
        proc2(style)
    if check3 == "true":
        proc3(style)
    if check4 == "true":
        proc4(style)
    if check5 == "true":
        proc5(style)
    if check6 == "true":
        proc6(style)
    if check7 == "true":
        proc7(style)
    if check8 == "true":
        proc8(style)
    if check9 == "true":
        proc9(style)

    book.save(workspace + "\\ErrorReport_" + today + ".xls")


nowS = datetime.datetime.now()
arcpy.AddMessage("and away we go... " + str(nowS))
book = xlwt.Workbook()
assemblereport(check1, check2, check3, check4, check5, check6, check7, check8, check9)
now = datetime.datetime.now()
arcpy.AddMessage("started " + str(nowS))
arcpy.AddMessage("that's all folks!" + str(now))