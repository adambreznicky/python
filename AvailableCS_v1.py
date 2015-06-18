__file__ = 'AvailableCS_v1'
__date__ = '10/21/2014'
__author__ = 'ABREZNIC'
import arcpy, string

city = []
counter = 0
comanche = "Connection to Comanche.sde"
subfiles = "Database Connections\\" + comanche + "\\TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES"
cursor = arcpy.da.SearchCursor(subfiles, ["CONTROLSEC", "CENSUS_CITY"], """ SUBFILE = 3 """)
for row in cursor:
    cs = row[0]
    letters = string.uppercase[:26]
    if cs is not None and len(cs) > 1:
        if cs[:3] != "TOL":
            if cs[2] in letters:
                if row[1] not in city:
                    city.append(row[1])
                print str(row[1]) + "," + str(row[0])
                counter += 1
del cursor
del row
print "total " + str(counter)
print str(city)
print len(city)
print "that's all folks!"