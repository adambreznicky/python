import datetime
import arcpy
import time

# Establish Start Time (put at the beginning of the script
start_time = time.time()

currentDay = datetime.datetime.now().day
currentMonth = datetime.datetime.now().month
currentYear = datetime.datetime.now().year
fileName = "Measure Errors " + str(currentMonth) + "-" + str(currentDay) + "-" + str(currentYear)

#Statewide Measures do not increase
#print "Opening Map..."
mxd = arcpy.mapping.MapDocument("C:\\TxDOT\\QC\\OffSystem\\tester\\MeasureErrors.mxd")

print "Exporting Map..."
arcpy.mapping.ExportToPNG(mxd,"C:\\TxDOT\\Scripts\\QC\\Error Checks\\PNG\\" + str(fileName) + ".png")
#arcpy.mapping.ExportToPNG(mxd,"C:\\TxDOT\\Projects\\_Data_Quality_Checks\\" + str(fileName) + ".png")
del mxd


print "number 2"
#Statewide LG XG Measures Should not increase with the digitized direction
fileName = "Measure LG XG Red is Bad " + str(currentMonth) + "-" + str(currentDay) + "-" + str(currentYear)

#print "Opening Map..."
mxd = arcpy.mapping.MapDocument("C:\\TxDOT\\QC\\OffSystem\\tester\\MeasureErrors_LG_XG.mxd")

#print "Exporting Map..."
arcpy.mapping.ExportToPNG(mxd,"C:\\TxDOT\\Scripts\\QC\\Error Checks\\PNG\\" + str(fileName) + ".png")
#arcpy.mapping.ExportToPNG(mxd,"C:\\TxDOT\\Projects\\_Data_Quality_Checks\\" + str(fileName) + ".png")
del mxd


print "number 3"
#Statewide RG and AG Measures Should increase with the digitized direction
fileName = "Measure RG AG Red is Bad " + str(currentMonth) + "-" + str(currentDay) + "-" + str(currentYear)

#print "Opening Map..."
mxd = arcpy.mapping.MapDocument("C:\\TxDOT\\QC\\OffSystem\\tester\\MeasureErrors_Not_LG_XG.mxd")

#print "Exporting Map..."
arcpy.mapping.ExportToPNG(mxd,"C:\\TxDOT\\Scripts\\QC\\Error Checks\\PNG\\" + str(fileName) + ".png")
#arcpy.mapping.ExportToPNG(mxd,"C:\\TxDOT\\Projects\\_Data_Quality_Checks\\" + str(fileName) + ".png")
del mxd

print "Done"

# Establish End Time and Report Total Run Time (put at the end of script)
end_time = time.time()
print "Elapsed time: {0}".format(time.strftime('%H:%M:%S', time.gmtime(end_time - start_time)))


