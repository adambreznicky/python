import arcpy, datetime, os

roadways = "C:\\TxDOT\\FederalRoads\\subfileupdate_2010114.gdb\\subfile_events_4"
now = datetime.datetime.now()
suffix = now.strftime("%Y%m%d")

rows = arcpy.SearchCursor(roadways, "", "", "", "RTE_ID A")
if os.path.exists("C:\\TxDOT\\FederalRoads\\QC\\MultipartErrors_" + suffix + ".txt"):
	os.remove("C:\\TxDOT\\FederalRoads\\QC\\MultipartErrors_" + suffix + ".txt")
output = open("C:\\TxDOT\\FederalRoads\\QC\\MultipartErrors_" + suffix + ".txt", "w")
output.write("The following RTE_ID's list multipart features:\n")
for row in rows:
	geom = row.shape
	rteID = row.getValue("RTE_ID")
	if geom.isMultipart:
		output.write(rteID + "\n")
output.close()
del rows
print "done"