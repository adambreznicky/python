
import os, arcpy, datetime


Output = "C:\\TxDOT\\Scratch\\results"
dbaseNAME = "Connection to Comanche.sde"

now = datetime.datetime.now()
suffix = now.strftime("%Y%m%d")
finalNM = "TotalPavedMileage"+suffix+".dbf"
final = Output+os.sep+finalNM
subfiles = "Database Connections\\"+dbaseNAME+"\\TPP_GIS.MCHAMB1.SUBFILES"
countyref = "Database Connections\\"+dbaseNAME+"\\TPP_GIS.MCHAMB1.County\\TPP_GIS.MCHAMB1.County"
where = """ "SUBFILE" = 2 AND "HIGHWAY_STATUS" = 4 AND "ADMIN_SYSTEM" = 3 """

if os.path.exists(final):
	os.remove(final)

dict1 = {}
swearer = arcpy.SearchCursor(countyref, "", "", "CNTY_NM; CNTY_NBR", "CNTY_NBR A")
for foul in swearer:
	number = foul.getValue("CNTY_NBR")
	name = foul.getValue("CNTY_NM")
	dict1[number] = name
print "dictionary 1 finished"
dict2 = {}
previous = ""
current = ""
totalmi = 0
pavedmi = 0
starter = 0
oldmilk = arcpy.MakeTableView_management(subfiles, "temper", where)
endAll = int(arcpy.GetCount_management(oldmilk).getOutput(0))
beAll = endAll - 1
pottymouth = arcpy.SearchCursor(subfiles, where, "", "COUNTY; LEN_OF_SECTION; SURFACE_TYPE", "COUNTY A")
for soapbar in pottymouth:
	current = soapbar.getValue("COUNTY")
	if starter == 0:
		totalmi += soapbar.getValue("LEN_OF_SECTION")
		previous = current
		starter += 1
		if soapbar.getValue("SURFACE_TYPE") == 51 or soapbar.getValue("SURFACE_TYPE") == 61:
			pavedmi += soapbar.getValue("LEN_OF_SECTION")
	if starter != 0  and previous == current and starter != beAll:
		totalmi += soapbar.getValue("LEN_OF_SECTION")
		starter += 1
		if soapbar.getValue("SURFACE_TYPE") == 51 or soapbar.getValue("SURFACE_TYPE") == 61:
			pavedmi += soapbar.getValue("LEN_OF_SECTION")
	if starter != 0 and previous != current and starter != beAll:
		val = [totalmi, pavedmi]
		dict2[previous] = val
		totalmi = soapbar.getValue("LEN_OF_SECTION")
		starter += 1
		if soapbar.getValue("SURFACE_TYPE") == 51 or soapbar.getValue("SURFACE_TYPE") == 61:
			pavedmi = soapbar.getValue("LEN_OF_SECTION")
		else:
			pavedmi = 0
		previous = current
	if starter == beAll and previous == current:
		totalmi += soapbar.getValue("LEN_OF_SECTION")
		if soapbar.getValue("SURFACE_TYPE") == 51 or soapbar.getValue("SURFACE_TYPE") == 61:
			pavedmi += soapbar.getValue("LEN_OF_SECTION")
		val = [totalmi, pavedmi]
		dict2[previous] = val
	if starter == beAll and previous != current:
		val = [totalmi, pavedmi]
		dict2[previous] = val
		totalmi = soapbar.getValue("LEN_OF_SECTION")
		if soapbar.getValue("SURFACE_TYPE") == 51 or soapbar.getValue("SURFACE_TYPE") == 61:
			pavedmi = soapbar.getValue("LEN_OF_SECTION")
		else:
			pavedmi = 0
		val = [totalmi, pavedmi]
		dict2[previous] = val
	print "finished row:" + str(starter)
print "dictionary 2 finished"
arcpy.CreateTable_management(Output, finalNM)
arcpy.AddField_management(final, "County", "TEXT", "", "", "30")
arcpy.AddField_management(final, "Number", "LONG")
arcpy.AddField_management(final, "Total_Mi", "DOUBLE")
arcpy.AddField_management(final, "Paved_Mi", "DOUBLE")
arcpy.AddField_management(final, "Unpaved_Mi", "DOUBLE")
arcpy.AddField_management(final, "test", "SHORT")
arcpy.DeleteField_management(final, "Field1")
print "table created, populating now..."

cursor = arcpy.InsertCursor(final)
for numba in dict1.keys():
	row = cursor.newRow()
	row.setValue("County", str(dict1[numba]))
	row.setValue("Number", numba)
	print "county: " + str(numba)
	tott = dict2[numba][0]
	pavv = dict2[numba][1]
	unpav = tott - pavv
	row.setValue("Total_Mi", tott)
	row.setValue("Paved_Mi", pavv)
	row.setValue("Unpaved_Mi", unpav)
	row.setValue("test", round(tott))
	cursor.insertRow(row)
del cursor

print "success!"



