__file__ = 'ErrorChecks_EOY_v1'
__date__ = '1/8/2015'
__author__ = 'ABREZNIC'
import arcpy, datetime, os
now = datetime.datetime.now()
curMonth = now.strftime("%m")
curDay = now.strftime("%d")
curYear = now.strftime("%Y")
today = curYear + "_" + curMonth + "_" + curDay

roadways = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways\\TPP_GIS.APP_TPP_GIS_ADMIN.TXDOT_Roadways"
localstreets = "Database Connections\\Connection to Comanche.sde\\TPP_GIS.APP_TPP_GIS_ADMIN.Local_Streets\\TPP_GIS.APP_TPP_GIS_ADMIN.Local_Streets"
bucket = "C:\\TxDOT\\QC\\EOY"

def identical():
    arcpy.CreateFileGDB_management(bucket, "Identical_" + today + ".gdb")
    print "Database created."
    dbase = bucket + os.sep + "Identical_" + today + ".gdb"
    allroads = dbase + os.sep + "Merged"
    arcpy.Merge_management([roadways, localstreets], allroads)
    print "Feature classes merged."
    arcpy.FindIdentical_management(allroads, dbase + os.sep + "Merged_FindIdentical", ["Shape"], "", "", "ONLY_DUPLICATES")

print "and away we go..."

identical()

print "that's all folks!"