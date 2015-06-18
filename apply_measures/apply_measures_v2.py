import arcpy, math
from arcpy import env

env.workspace = "C:\\TxDOT\\FederalRoads"


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
	
	srtPnt = 0
	lastX = 0
	lastY = 0
	lastM = 0
	for part in allparts:
		print "part: " + str(partnum) + " of " + str(count)
		aryPos = partnum - 1
		ary = arcpy.Array()
		totalNum = len(part) - 1
	
		
		for pnt in part:
			if srtPnt == 0:
				x = pnt.X
				y = pnt.Y
				m = 0
				nupnt = arcpy.Point(x,y,0,m)
				ary.add(nupnt)
				lastX = x
				lastY = y
				lastM = 0
				print str(x) + "," + str(y) + "," + str(m)
				srtPnt += 1
			else:
				x = pnt.X
				y = pnt.Y
				newM = (math.sqrt((abs(x - lastX))**2 + (abs(y - lastY))**2))
				m = lastM + (newM*.000621371)
				print str(m)
				nupnt = arcpy.Point(x,y,0,m)
				ary.add(nupnt)
				print str(x) + "," + str(y) + "," + str(m)
				lastX = x
				lastY = y
				lastM = m
		partAry.add(ary)
		partnum += 1
	row.shape = arcpy.Polyline(partAry, spatialRef, False, True)
	rows.updateRow(row)
del rows
print "done"