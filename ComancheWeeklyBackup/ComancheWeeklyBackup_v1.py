__file__ = 'ComancheWeeklyBackup_v1'
__date__ = '7/1/2014'
__author__ = 'ABREZNIC'
import arcpy, datetime
from arcpy import env

connection = "Connection to Comanche.sde"
output = "C:\\TxDOT\\ComancheBackup"

now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + curMonth + curDay
print "Creating database..."
arcpy.CreateFileGDB_management(output, "Comanche" + today + ".gdb")
copy = output + "\\Comanche" + today + ".gdb"

comanche = "Database Connections\\" + connection + "\\"
env.workspace = comanche

print "Starting copies..."
datasetList = arcpy.ListDatasets()
for dataset in datasetList:
    print dataset
    name = dataset.split(".")[-1]
    try:
        arcpy.Copy_management(dataset, copy + "\\" + name)
        print "Success!"
    except:
        print "Could not copy this one."
        pass
    # name = dataset.split(".")[-1]
    # print name
    # arcpy.CreateFeatureDataset_management(copy, name)
    # fcList = arcpy.ListFeatureClasses("", "All", dataset)
    # for fc in fcList:
    #     print fc
    #     label = fc.split(".")[-1]
    #     arcpy.Copy_management(fc, copy + "\\" + name + "\\" + label)


tableList = arcpy.ListTables()
for table in tableList:
    print table
    name = table.split(".")[-1]
    try:
        arcpy.Copy_management(table, copy + "\\" + name)
        print "Success!"
    except:
        print "Could not copy this one."
        pass

print "that's all folks!"
print "started: " + str(now)
now = datetime.datetime.now()
print "ended: " + str(now)