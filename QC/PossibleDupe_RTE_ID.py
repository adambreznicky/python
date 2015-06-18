__file__ = 'PossibleDupe_RTE_ID'
__date__ = '3/13/2015'
__author__ = 'ABREZNIC'
import arcpy

roadways = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"

print "checking rte classes."
dictionary = {}
cursor = arcpy.da.SearchCursor(roadways, ["RTE_ID", "RTE_CLASS"])
for row in cursor:
    if row[0] not in dictionary.keys():
        dictionary[row[0]] = row[1]
    else:
        compare = dictionary[row[0]]
        if compare != row[1]:
            print row[0] + " has multiple rte classes."
del cursor
del row

print "checking roadbeds."
dictionary = {}
cursor = arcpy.da.SearchCursor(roadways, ["RTE_ID", "RDBD_TYPE"])
for row in cursor:
    if row[0] not in dictionary.keys():
        dictionary[row[0]] = row[1]
    else:
        compare = dictionary[row[0]]
        if compare != row[1]:
            print row[0] + " has multiple roadbed types."
del cursor
del row

print "that's all folks!"