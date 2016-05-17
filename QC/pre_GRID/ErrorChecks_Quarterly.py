#March 2014
#Adam Breznicky - TxDOT TPP - Mapping Group
#
#
#
#
#


import arcpy, math, xlwt, datetime, os

now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + "_" + curMonth + "_" + curDay

#variables
roadways = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
# roadways = "C:\\TxDOT\\QC\\GSC\\test.gdb\\roadways_1"
where = """ RDBD_TYPE = 'CONNECTOR' OR RDBD_TYPE = 'RAMP' OR RDBD_TYPE = 'TURNAROUND' OR RDBD_TYPE = 'OTHER'  """
where2 = """ RDBD_TYPE = 'CNCTR-GS' """
subfiles = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
# subfiles = "C:\\TxDOT\\QC\\GSC\\test.gdb\\subfiles_1"
output = "C:\\TxDOT\\QC\\GSC"

if os.path.exists(output + os.sep + "GSC_Errors" + today + ".xls"):
    os.remove(output + os.sep + "GSC_Errors" + today + ".xls")
if os.path.exists(output + os.sep + "Multipart_Errors" + today + ".xls"):
    os.remove(output + os.sep + "Multipart_Errors" + today + ".xls")

def applymeasures():
    print "Applying odd roadbed type measures (zero to length)..."
    spatialRef = arcpy.Describe(roadways).spatialReference
    rows = arcpy.UpdateCursor(roadways, where)
    for row in rows:
        geom = row.shape
        print str(row.RDBD_TYPE) + " ID: " + str(row.getValue("OBJECTID"))
        allparts = geom.getPart()
        partnum = 0
        partAry = arcpy.Array()
        # count = allparts.count
        # if count > 1:
        #     multipart.append(str(row.OBJECTID))
        srtPnt = 0
        lastX = 0
        lastY = 0
        lastM = 0
        for part in allparts:
            #print "part: " + str(partnum) + " of " + str(count)
            # aryPos = partnum - 1
            # totalNum = len(part) - 1
            ary = arcpy.Array()
            for pnt in part:
                if srtPnt == 0:
                    x = pnt.X
                    y = pnt.Y
                    m = 0
                    nupnt = arcpy.Point(x, y, 0, m)
                    ary.add(nupnt)
                    lastX = x
                    lastY = y
                    lastM = 0
                    #print str(x) + "," + str(y) + "," + str(m)
                    srtPnt += 1
                else:
                    x = pnt.X
                    y = pnt.Y
                    newM = (math.sqrt((abs(x - lastX)) ** 2 + (abs(y - lastY)) ** 2))
                    newMiles = newM * .000621371
                    m = lastM + newMiles
                    #print str(m)
                    nupnt = arcpy.Point(x, y, 0, m)
                    ary.add(nupnt)
                    #print str(x) + "," + str(y) + "," + str(m)
                    lastX = x
                    lastY = y
                    lastM = m
            partAry.add(ary)
            partnum += 1
        row.shape = arcpy.Polyline(partAry, spatialRef, False, True)
        rows.updateRow(row)
        geom = row.shape
        wholeLen = geom.length * .000621371
        print "old: " + str(row.RTE_LEN)
        row.setValue("RTE_LEN", wholeLen)
        rows.updateRow(row)
        print "new: " + str(row.RTE_LEN)
    del rows
    del row
    print "Finished applying measures to odd roadbed types."

def gsc_Check():
    print "Beginning Grade Separated Connector error checks..."
    multiLine = 0
    book = xlwt.Workbook()
    sheet = book.add_sheet("GSC_Errors")
    sheet.write(multiLine, 0, "The following are Grade Separated Connectors with Subfile records that don't match the measures:")
    multiLine += 1
    sheet.write(multiLine, 0, "RTE ID")
    sheet.write(multiLine, 1, "Mmin")
    sheet.write(multiLine, 2, "Mmax")
    sheet.write(multiLine, 3, "first BMP")
    sheet.write(multiLine, 4, "last EMP")
    sheet.write(multiLine, 5, "# of Subfiles")
    sheet.write(multiLine, 6, "LEN_OF_SECTION Total")
    sheet.write(multiLine, 7, "Subfile OBJECTID BMPvsEMPvsLOS Error")
    sheet.write(multiLine, 8, "Description")
    multiLine += 1
    #
    spatialRef = arcpy.Describe(roadways).spatialReference
    rows = arcpy.SearchCursor(roadways, where2)
    for row in rows:
        GSCid = row.RTE_ID
        print GSCid
        geom = row.shape
        wholeLen = geom.length * .000621371
        rte_len = row.RTE_LEN
        ext = geom.extent
        Mmin = round(ext.MMin, 3)
        Mmax = round(ext.MMax, 3)
        cursor = arcpy.SearchCursor(subfiles, "RTE_ID = '" + GSCid + "'", "", "", "BMP A")
        counter = 0
        flag = 0
        recError = 0
        OBJID = ""
        for i in cursor:
            if flag == 0:
                bmp = i.BMP
                flag += 1
            emp = i.EMP
            brow = i.BMP
            if abs((emp - brow) - i.LEN_OF_SECTION) > .001:
                OBJID = i.OBJECTID
                sheet.write(multiLine, 0, GSCid)
                sheet.write(multiLine, 1, Mmin)
                sheet.write(multiLine, 2, Mmax)
                sheet.write(multiLine, 3, brow)
                sheet.write(multiLine, 4, emp)
                sheet.write(multiLine, 5, "")
                sheet.write(multiLine, 6, i.LEN_OF_SECTION)
                sheet.write(multiLine, 7, OBJID)
                sheet.write(multiLine, 8, "SUBFILES record(s) LEN_OF_SECTION <> difference between the EMP and BMP.")
                multiLine += 1
            recError += i.LEN_OF_SECTION
            counter += 1

        if counter == 0:
            sheet.write(multiLine, 0, GSCid)
            sheet.write(multiLine, 1, Mmin)
            sheet.write(multiLine, 2, Mmax)
            sheet.write(multiLine, 3, "")
            sheet.write(multiLine, 4, "")
            sheet.write(multiLine, 5, counter)
            sheet.write(multiLine, 6, recError)
            sheet.write(multiLine, 7, OBJID)
            sheet.write(multiLine, 8, "No SUBFILES exist for this GSC. Please create SUBFILES record.")
            multiLine += 1
        else:
            if bmp != Mmin:
                sheet.write(multiLine, 0, GSCid)
                sheet.write(multiLine, 1, Mmin)
                sheet.write(multiLine, 2, Mmax)
                sheet.write(multiLine, 3, bmp)
                sheet.write(multiLine, 4, emp)
                sheet.write(multiLine, 5, counter)
                sheet.write(multiLine, 6, recError)
                sheet.write(multiLine, 7, OBJID)
                sheet.write(multiLine, 8, "Beginning BMP SUBFILE measure <> Min Measure in geometry.")
                multiLine += 1
            if abs(emp - Mmax) > .002:
                sheet.write(multiLine, 0, GSCid)
                sheet.write(multiLine, 1, Mmin)
                sheet.write(multiLine, 2, Mmax)
                sheet.write(multiLine, 3, bmp)
                sheet.write(multiLine, 4, emp)
                sheet.write(multiLine, 5, counter)
                sheet.write(multiLine, 6, recError)
                sheet.write(multiLine, 7, OBJID)
                sheet.write(multiLine, 8, "Ending EMP SUBFILE measure <> Max Measure in geometry.")
                multiLine += 1
            if bmp != 0:
                sheet.write(multiLine, 0, GSCid)
                sheet.write(multiLine, 1, Mmin)
                sheet.write(multiLine, 2, Mmax)
                sheet.write(multiLine, 3, bmp)
                sheet.write(multiLine, 4, emp)
                sheet.write(multiLine, 5, counter)
                sheet.write(multiLine, 6, recError)
                sheet.write(multiLine, 7, OBJID)
                sheet.write(multiLine, 8, "Beginning BMP SUBFILE measure <> 0. GSCs should be zero to length measures.")
                multiLine += 1
            if Mmin != 0:
                sheet.write(multiLine, 0, GSCid)
                sheet.write(multiLine, 1, Mmin)
                sheet.write(multiLine, 2, Mmax)
                sheet.write(multiLine, 3, bmp)
                sheet.write(multiLine, 4, emp)
                sheet.write(multiLine, 5, counter)
                sheet.write(multiLine, 6, "Min measure <> 0. GSCs should be zero to length measures.")
                multiLine += 1
            if abs(recError - Mmax) > .002:
                sheet.write(multiLine, 0, GSCid)
                sheet.write(multiLine, 1, Mmin)
                sheet.write(multiLine, 2, Mmax)
                sheet.write(multiLine, 3, bmp)
                sheet.write(multiLine, 4, emp)
                sheet.write(multiLine, 5, counter)
                sheet.write(multiLine, 6, recError)
                sheet.write(multiLine, 7, OBJID)
                sheet.write(multiLine, 8, "Sum LEN_OF_SECTIONs in SUBFILES <> length/Max-measure in geometry.")
                multiLine += 1
            if abs(recError - rte_len) > .002:
                sheet.write(multiLine, 0, GSCid)
                sheet.write(multiLine, 1, Mmin)
                sheet.write(multiLine, 2, Mmax)
                sheet.write(multiLine, 3, bmp)
                sheet.write(multiLine, 4, emp)
                sheet.write(multiLine, 5, counter)
                sheet.write(multiLine, 6, recError)
                sheet.write(multiLine, 7, OBJID)
                sheet.write(multiLine, 8, "Sum LEN_OF_SECTIONs in SUBFILES <> RTE_LEN.")
                multiLine += 1
            if abs(wholeLen - rte_len) > .002:
                sheet.write(multiLine, 0, GSCid)
                sheet.write(multiLine, 1, Mmin)
                sheet.write(multiLine, 2, Mmax)
                sheet.write(multiLine, 3, bmp)
                sheet.write(multiLine, 4, emp)
                sheet.write(multiLine, 5, counter)
                sheet.write(multiLine, 6, recError)
                sheet.write(multiLine, 7, OBJID)
                sheet.write(multiLine, 8, "Geometry length <> RTE_LEN.")
                multiLine += 1
            if abs(recError - wholeLen) > .002:
                sheet.write(multiLine, 0, GSCid)
                sheet.write(multiLine, 1, Mmin)
                sheet.write(multiLine, 2, Mmax)
                sheet.write(multiLine, 3, bmp)
                sheet.write(multiLine, 4, emp)
                sheet.write(multiLine, 5, counter)
                sheet.write(multiLine, 6, recError)
                sheet.write(multiLine, 7, OBJID)
                sheet.write(multiLine, 8, "Sum LEN_OF_SECTIONs in SUBFILES <> Geometry Length.")
                multiLine += 1
        del cursor
    del rows
    del row
    book.save(output + os.sep + "GSC_Errors" + today + ".xls")
    print "Finished Grade Separated Connector error checks. Report found here: "
    print output + os.sep + "GSC_Errors" + today + ".xls"

def blanks():
    print "Applying default values to NULLs in SUBFILES..."
    # routeList = []
    # blanks = "C:\\TxDOT\\_Subfile Validations\\EOY\\2014\\blanks.dbf"
    # cursor = arcpy.SearchCursor(blanks)
    # for row in cursor:
    #     route = str(row.RTE_ID)
    #     if route not in routeList:
    #         routeList.append(route)
    #         print route
    # del cursor
    # print "route list created"

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

    cursor = arcpy.UpdateCursor(subfiles)
    for row in cursor:
        rte = str(row.RTE_ID)
        print rte
        for fieldname in default.keys():
            value = row.getValue(fieldname)
            if value is None or value == "" or value == " " or value == 0:
                row.setValue(fieldname, default[fieldname])
                # cursor.updateRow(row)
        if row.getValue("ACR_GROUP") == "0":
            row.setValue("ACR_GROUP", default["ACR_GROUP"])
        cursor.updateRow(row)
    del cursor
    del row
    print "Finished applying defaults to NULL values."

def multipart():
    print "Beginning multipart error check..."
    errors = []
    cursor = arcpy.SearchCursor(roadways)
    for row in cursor:
        geom = row.shape
        rteID = row.RTE_ID
        OID = row.OBJECTID
        print rteID
        if geom.isMultipart:
            info = [OID, rteID]
            errors.append(info)
    del cursor
    del row
    number = len(errors)
    if number == 0:
        print "No multipart errors."
        blanks()
        applymeasures()
        gsc_Check()
    else:
        print str(number) + " multipart errors."
        line = 0
        book = xlwt.Workbook()
        sheet = book.add_sheet("Multipart_Features")
        sheet.write(line, 0, "The following TxDOT_Roadways features are Multipart. Fix these feature and re-run this check for GSC errors:")
        line += 1
        sheet.write(line, 0, "OBJECTID")
        sheet.write(line, 1, "RTE ID")
        line += 1
        for i in errors:
            column1 = i[0]
            column2 = i[1]
            sheet.write(line, 0, column1)
            sheet.write(line, 1, column2)
            line += 1
        book.save(output + os.sep + "Multipart_Errors" + today + ".xls")
        print "Please fix the multipart errors and re-run this error check script for GSC errors. Report found here: "
        print output + os.sep + "Multipart_Errors" + today + ".xls"

multipart()
print "that's all folks!"
