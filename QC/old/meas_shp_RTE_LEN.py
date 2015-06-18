__file__ = 'meas_shp_RTE_LEN'
__date__ = '9/22/2014'
__author__ = 'ABREZNIC'
import arcpy, xlwt, math, datetime
roadways = ""
where = ""
workspace = ""

now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + "_" + curMonth + "_" + curDay



def measurelength():
    arcpy.AddMessage("Starting off-system geometry check...")
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
        shp_len = float(format(float(wholelen), '.3f'))
        rte_len = row.RTE_LEN

        testlen = abs(shp_len - Mdiff)
        if rte_len is not None and id is not None:
            if testlen <= .003 and abs(rte_len - shp_len) > .003:
                oid = str(row.OBJECTID)
                arcpy.AddMessage(
                    "RTE_LEN replaced: " + str(oid) + "," + str(rte_len) + "," + str(shp_len) + "," + str(Mdiff))
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

def assemblereport():
    arcpy.AddMessage("OffSystem Geometry & Measure Errors...")

    font = xlwt.Font()  # Create the Font
    font.name = 'Calibri'
    font.height = 240  # =point size you want * 20
    style = xlwt.XFStyle()  # Create the Style
    style.font = font  # Apply the Font to the Style

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
        geomsheet.write(ogline, 0, i[0], style=style)
        geomsheet.write(ogline, 1, i[1], style=style)
        geomsheet.write(ogline, 2, i[2], style=style)
        geomsheet.write(ogline, 3, i[3], style=style)
        geomsheet.write(ogline, 4, i[4], style=style)
        geomsheet.write(ogline, 5, i[5], style=style)
        geomsheet.write(ogline, 6, i[6], style=style)
        ogline += 1

book = xlwt.Workbook()
assemblereport()
print "Saving excel error report..."
book.save(workspace + "\\ErrorReport_" + today + ".xls")
print "that's all folks!"
