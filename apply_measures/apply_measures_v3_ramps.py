#March 2014
#Adam Breznicky - TxDOT TPP - Mapping Group
#
#this script is designed to identify ramp/connectors/grade separated connectors/turnarounds/other roadbed types
#via the 'where' variable query and assign their measures based on their geometrically drawn length
#
#
#
#



import arcpy, math, xlwt

#variables
roadways = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
#roadways = "C:\\TxDOT\\Scripts\\apply_measures\\v3_ramps.gdb\\TXDOT_Roadways3"
where = """ RDBD_TYPE = 'CNCTR-GS' OR RDBD_TYPE = 'CONNECTOR' OR RDBD_TYPE = 'RAMP' OR RDBD_TYPE = 'TURNAROUND' OR RDBD_TYPE = 'OTHER'  """
subfiles = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
#subfiles = "C:\\TxDOT\\Scripts\\apply_measures\\v3_ramps.gdb\\Export_Output3"

def applymeasures():
    spatialRef = arcpy.Describe(roadways).spatialReference
    multipart = []
    multiLine = 0
    multiLine2 = 0
    book = xlwt.Workbook()
    sheet = book.add_sheet("multiple_subfiles")
    sheet2 = book.add_sheet("non_zero_bmp")
    sheet.write(multiLine, 0, "The following are Grade Separated Connectors with multiple Subfile records that don't match the measures:")
    multiLine += 1
    sheet.write(multiLine, 0, "RTE ID")
    sheet.write(multiLine, 1, "Mmin")
    sheet.write(multiLine, 2, "Mmax")
    sheet.write(multiLine, 3, "first BMP")
    sheet.write(multiLine, 4, "last EMP")
    sheet.write(multiLine, 5, "# of Subfiles")
    sheet.write(multiLine, 6, "LEN_OF_SECTION Total")
    sheet.write(multiLine, 7, "Subfile OBJECTID BMPvsEMPvsLOS Error")
    multiLine += 1
    sheet2.write(multiLine2, 0, "The following Route IDs are Grade Separated Connectors with non-zero to length Subfile records:")
    multiLine2 += 1
    sheet2.write(multiLine2, 0, "RTE ID")
    sheet2.write(multiLine2, 1, "Mmin")
    sheet2.write(multiLine2, 2, "Mmax")
    sheet2.write(multiLine2, 3, "first BMP")
    sheet2.write(multiLine2, 4, "last EMP")
    sheet2.write(multiLine2, 5, "# of Subfiles")
    multiLine2 += 1
    rows = arcpy.UpdateCursor(roadways, where)
    for row in rows:
        if row.RDBD_TYPE != "CNCTR-GS":
            geom = row.shape

            print str(row.RDBD_TYPE) + " ID: " + str(row.getValue("OBJECTID"))
            allparts = geom.getPart()
            count = allparts.count
            partnum = 1
            partAry = arcpy.Array()
            if count > 1:
                multipart.append(str(row.OBJECTID))
            srtPnt = 0
            lastX = 0
            lastY = 0
            lastM = 0
            for part in allparts:
                #print "part: " + str(partnum) + " of " + str(count)
                aryPos = partnum - 1
                ary = arcpy.Array()
                totalNum = len(part) - 1

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
                        # if newMiles >= .001 and pnt.ID != len(part):
                        if pnt.ID != len(part):
                            m = lastM + newMiles
                            #print str(m)
                            nupnt = arcpy.Point(x, y, 0, m)
                            ary.add(nupnt)
                            #print str(x) + "," + str(y) + "," + str(m)
                            lastX = x
                            lastY = y
                            lastM = m
                        elif pnt.ID == len(part):
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
            wholeLen = geom.length * .000621371
            print "old: " + str(row.RTE_LEN)
            row.setValue("RTE_LEN", wholeLen)
            rows.updateRow(row)
            print "new: " + str(row.RTE_LEN)
        else:
            GSCid = row.RTE_ID
            geom = row.shape
            ext = geom.extent
            Mmin = round(ext.MMin, 3)
            Mmax = round(ext.MMax, 3)
            cursor = arcpy.UpdateCursor(subfiles, "RTE_ID = '" + GSCid + "'", "", "", "BMP A")
            counter = 0
            flag = 0
            recError = 0
            rowFlag = 0
            OBJID = ""
            for i in cursor:
                if flag == 0:
                    bmp = i.BMP
                    flag += 1
                emp = i.EMP
                brow = i.BMP
                if abs((emp - brow) - i.LEN_OF_SECTION) > .001:
                    rowFlag += 1
                    OBJID = i.OBJECTID
                recError += i.LEN_OF_SECTION
                counter += 1
            if counter > 1:
                if bmp != Mmin or (abs(emp - Mmax) > .002) or bmp != 0 or (abs(recError - Mmax) > .002) or rowFlag > 0:
                    sheet.write(multiLine, 0, GSCid)
                    sheet.write(multiLine, 1, Mmin)
                    sheet.write(multiLine, 2, Mmax)
                    sheet.write(multiLine, 3, bmp)
                    sheet.write(multiLine, 4, emp)
                    sheet.write(multiLine, 5, counter)
                    sheet.write(multiLine, 6, recError)
                    sheet.write(multiLine, 7, OBJID)
                    multiLine += 1
            else:
                if bmp != 0 or Mmin != 0:
                    sheet2.write(multiLine2, 0, GSCid)
                    sheet2.write(multiLine2, 1, Mmin)
                    sheet2.write(multiLine2, 2, Mmax)
                    sheet2.write(multiLine2, 3, bmp)
                    sheet2.write(multiLine2, 4, emp)
                    sheet2.write(multiLine2, 5, counter)
                    multiLine2 += 1
                else:
                    geom = row.shape
                    print str(row.RDBD_TYPE) + " ID: " + str(row.getValue("OBJECTID"))
                    allparts = geom.getPart()
                    count = allparts.count
                    partnum = 1
                    partAry = arcpy.Array()
                    if count > 1:
                        multipart.append(str(row.OBJECTID))
                    srtPnt = 0
                    lastX = 0
                    lastY = 0
                    lastM = 0
                    for part in allparts:
                        #print "part: " + str(partnum) + " of " + str(count)
                        aryPos = partnum - 1
                        ary = arcpy.Array()
                        totalNum = len(part) - 1

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
                                if newMiles >= .001 and pnt.ID != len(part):
                                    m = lastM + newMiles
                                    #print str(m)
                                    nupnt = arcpy.Point(x, y, 0, m)
                                    ary.add(nupnt)
                                    #print str(x) + "," + str(y) + "," + str(m)
                                    lastX = x
                                    lastY = y
                                    lastM = m
                                elif pnt.ID == len(part):
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
                    wholeLen = geom.length * .000621371
                    print "old: " + str(row.RTE_LEN)
                    row.setValue("RTE_LEN", wholeLen)
                    rows.updateRow(row)
                    print "new: " + str(row.RTE_LEN)

                    #SUBFILES UPDATE
                    for n in cursor:
                        n.setValue("BMP", 0)
                        n.setValue("EMP", m)
                        n.setValue("LEN_OF_SECTION", m)
                        n.setValue("LEN2", m)
                        cursor.updateRow(n)

    del rows
    book.save("C:\\TxDOT\\GSC_MulipleSubfiles.xls")

applymeasures()
print "success!"
#print "multipart issues: "
#for i in multipart:
#    print i