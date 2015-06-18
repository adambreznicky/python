#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      CST05
#
# Created:     01/11/2013
# Copyright:   (c) CST05 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy
from arcpy import env

env.workspace = "C:\\Student\\PYTH\\Selections\\SanDiego.gdb"

desc = arcpy.Describe("Freeways_routes")
shapefieldname = desc.ShapeFieldName
newpart = ""
with arcpy.da.UpdateCursor("Freeways_routes", ["SHAPE@"]) as rows:
    for row in rows:
        feat = row[0]
        print "row_________________"
 #       partnum = 0
        ary = arcpy.Array()
        for part in feat:
 #           for pnt in part.getPart(partnum):
            pos = 0
            for pnt in part:
                if pnt:
# fix - need to create parts....
                    nupnt = arcpy.Point(pnt.X, pnt.Y, 0, 42)
                    print "pnt = {} {} {} ".format(pnt.X, pnt.Y, pnt.M)
                    print "nupnt = {} {} {} ".format(nupnt.X, nupnt.Y, nupnt.M)
                    ary.add(nupnt)
                    pos = pos + 1
        nugeom = arcpy.Polyline(ary, None, False, True)




        for part in nugeom:
 #           for pnt in part.getPart(partnum):
            for pnt in part:
                if pnt:
                    print "new = {} {} {} ".format(pnt.X, pnt.Y, pnt.M)
        row[0] = nugeom
        rows.updateRow(row)