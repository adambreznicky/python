__file__ = 'dictionaryTime'
__date__ = '3/19/2015'
__author__ = 'ABREZNIC'
import arcpy
roads = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"

dictionary = {}

cursor = arcpy.da.SearchCursor(roads, ["RTE_ID", "RTE_LEN", "RDBD_TYPE"])
for row in cursor:
    id = row[0]
    len = row[1]
    rdbd = row[2]

    list = [len, rdbd]
    dictionary[id] = list
    #
    # dictionary[row[0]] = [row[1], row[2]]
    # print dictionary[row[0]]

cursor = arcpy.da.UpdateCursor(featureClaSSTOuPDATE, ["ID", "LENGTH", "RDBD"])
for row in cursor:
    id = row[0]
    len = row[1]
    rdbd = row[2]

    valuesList = dictionary[id]
    newLen = valuesList[0]
    newRDBD = valuesList[1]

    row[1] = newLen
    row[2] = newRDBD
    cursor.updateRow(row)