import arcpy
from arcpy import env

env.workspace = "C:\\TxDOT\\FederalRoads"

# desc = arcpy.Describe("tester.shp")
# shapefieldname = desc.ShapeFieldName
spatialRef = arcpy.Describe("tester.shp").spatialReference

rows = arcpy.UpdateCursor("tester.shp")
for row in rows:
	geom = row.shape
	wholeLen = geom.length*.000621371
	row.setValue("calc_len", wholeLen)
	print "FID: " + str(row.getValue("FID"))
	allparts = geom.getPart()
	count = allparts.count
	partnum = 1
	partAry = arcpy.Array()
	for part in allparts:
		print "part: " + str(partnum) + " of " + str(count)
		aryPos = partnum - 1
		ary = arcpy.Array()
		totalNum = len(part) - 1
		for pnt in part:
			x = pnt.X
			y = pnt.Y
			m = pnt.M
			print "point info(X,Y,M): " + str(x) + "," + str(y) + "," + str(m)
			nupnt = arcpy.Point(x,y,0,0)
			ary.add(nupnt)
		
		partAry.add(ary)
		partnum += 1
	row.shape = arcpy.Polyline(partAry, spatialRef, False, True)
	rows.updateRow(row)
del rows
print "done"