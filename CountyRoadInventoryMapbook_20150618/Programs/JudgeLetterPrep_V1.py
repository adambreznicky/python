__file__ = 'JudgeLetterPrep_V1'
__date__ = '3/4/2015'
__author__ = 'ABREZNIC'
import arcpy, datetime, xlwt, os

#variables
input = "C:\\TxDOT\\County Road Inventory Mapbooks\\Resources\\Documents\\JudgeLetters\\prep\\2015\\TxOfficeofCourtAdmin_Judges_20150303.xls\\t2089417553$"
output = "C:\\TxDOT\\County Road Inventory Mapbooks\\Resources\\Documents\\JudgeLetters\\prep\\2015"
cycle = "South"

#process
resourcesFolder = "C:\\TxDOT\\County Road Inventory Mapbooks"
if cycle == "North":
    CountyLayer = resourcesFolder + "\\Resources\\South and North County Shapefiles\\NorthCounties.shp"
elif cycle == "South":
    CountyLayer = resourcesFolder + "\\Resources\\South and North County Shapefiles\\SouthCounties.shp"
else:
    print "You must use ether 'North' or 'South' for your cycle option"
arcpy.MakeFeatureLayer_management(CountyLayer, "working")
print "Feature layer made."
arcpy.AddJoin_management("working", "CNTY_NM", input, "County", "KEEP_COMMON")
print "County layer joined."

now = datetime.datetime.now()
suffix = now.strftime("%Y%m%d")
subfiles = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
countyref = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.County\\TPP_GIS.APP_TPP_GIS_ADMIN.County"
namer = "CntyRoadMileage" + suffix
final = output + os.sep + namer + ".dbf"
where = """ "SUBFILE" = 2 AND "HIGHWAY_STATUS" = 4 AND "ADMIN_SYSTEM" = 2 """
arcpy.MakeQueryTable_management(subfiles, "temptable", "ADD_VIRTUAL_KEY_FIELD", "", "", where)
print "Query table made."
arcpy.Statistics_analysis("temptable", final, [["LEN_OF_SECTION", "SUM"]], "COUNTY")
print "County mileages summarized."
arcpy.JoinField_management(final, "COUNTY", countyref, "CNTY_NBR", ["CNTY_NM"])
print "County name field joined."

arcpy.AddJoin_management("working", "CNTY_NM", final, "CNTY_NM")
print "County mileages joined."

pfx = input.split("\\")[-1]
fields = [pfx + ".Court", pfx + ".County", pfx + ".Address", pfx + ".City", pfx + ".Zip Code", pfx + ".Phone", pfx + ".First Name", pfx + ".Middle Name", pfx + ".Last Name", pfx + ".Suffix", pfx + ".Email", namer + ".SUM_LEN_OF"]
counties = []
cursor = arcpy.da.SearchCursor("working", fields, "", "", "", (None, "ORDER BY " + pfx + ".County ASC"))
for row in cursor:
    f = row[6]
    if "(" in f or ")" in f:
        pos1 = f.index("(")
        pos2 = pos1 - 1
        pos3 = f.index(")")
        pos4 = pos3 + 1
        f = f[:pos2] + f[pos4:]
    # m = row[7]
    # if m is not None:
    #     if "(" in m or ")" in m:
    #         m = None
    l = row[8]
    s = row[9]
    # if m is not None and s is not None:
    #     fullname = f + " " + m + " " + l + " " + s
    # elif m is not None and s is None:
    #     fullname = f + " " + m + " " + l
    # elif m is None and s is not None:
    #     fullname = f + " " + l + " " + s
    # elif m is None and s is None:
    #     fullname = f + " " + l
    fullname = f + " " + l
    cityzip = row[3] + ", Texas " + row[4]
    roundedmiles = round(row[11])
    values = [row[0], row[1], row[2], row[3], row[4], row[5], "The Honorable " + fullname, cityzip, roundedmiles, row[11], fullname, l, row[10]]
    counties.append(values)
    print row[1] + " compiled."
del cursor
del row
print "All counties compiled."

header = ["Court", "County", "Address", "City", "Zip", "Phone", "Name", "CTY_ST_ZIP", "Mileage", "SUM", "Full", "Last Name", "Email"]
book = xlwt.Workbook()
sheet = book.add_sheet("JudgeAddresses_Complete")
line = 0
row = 0
for i in header:
    sheet.write(line, row, i)
    row += 1
line += 1
for j in counties:
    row = 0
    for p in j:
        sheet.write(line, row, p)
        row += 1
    line += 1
book.save(output + "\\JudgeAddresses.xls")
print "Excel saved: " + output + "\\JudgeAddresses.xls"

print "that's all folks!"