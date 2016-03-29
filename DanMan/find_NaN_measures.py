__file__ = 'find_NaN_measures.py'
__date__ = '3/29/2016'
__author__ = 'ABREZNIC'
"""
The MIT License (MIT)

Copyright (c) 2016 Texas Department of Transportation
Author: Adam Breznicky

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import arcpy, math

# feature_class = "T:\\DATAMGT\\HPMS-DATA\\2015Data\\Pavement\\IRI\\IRIData\\OffSystem_For_Script\\Input.gdb\\PossumLines"
feature_class = "C:\\TxDOT\\Projects\\IRI_dan\\2016\\input\\offsystem\\Input.gdb\\PossumLines"

counter = 0
bad_routes = []
cursor = arcpy.da.SearchCursor(feature_class, ["OBJECTID", "ROUTE_ID", "SHAPE@"])
for row in cursor:
    geom = row[2]
    for part in geom:
        for pnt in part:
            measure = float(pnt.M)
            if math.isnan(measure):
                if row[1] not in bad_routes:
                    bad_routes.append(row[1])
                    counter += 1

del cursor
del row

print str(counter) + " ROUTE_IDs with bad geometry."
print bad_routes
print "that's all folks!!"
