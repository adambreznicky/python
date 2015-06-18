#
#reads the current date and creates a new folder structure for each district/county
#Adam Breznicky, created January 2014
#
import arcpy, os, datetime, shutil
#variables; adjust as necessary
cntyflder = "T:\\DATAMGT\\MAPPING\\Data Collection\\Core Projects\\CountyRoad\\"
#
now = datetime.datetime.now()
year = now.strftime("%Y")
if int(year)%2==0:
	counties = "C:\\TxDOT\\County Road Inventory Mapbooks\\Resources\\South and North County Shapefiles\\NorthCounties.shp"
elif int(year)%2!=0:
	counties = "C:\\TxDOT\\County Road Inventory Mapbooks\\Resources\\South and North County Shapefiles\\SouthCounties.shp"

if not os.path.exists(cntyflder + year):
	os.makedirs(cntyflder + year)
else:
	print "Folder already exists for this year."

newdir = cntyflder + year
os.makedirs(newdir + os.sep + "_Progress Maps")
lastyear = int(year) - 1
shutil.copytree(cntyflder + str(lastyear) + os.sep + "_Resources", cntyflder + year + os.sep + "_Resources")


cursor = arcpy.SearchCursor(counties, "", "", "CNTY_NM; DIST_NM", "DIST_NM A; CNTY_NM A")
prev = ""
curr = ""

for row in cursor:
	curr = row.DIST_NM
	if curr != prev:
		os.makedirs(newdir + os.sep + curr)
		os.makedirs(newdir + os.sep + curr + os.sep + str(row.CNTY_NM))
		os.makedirs(newdir + os.sep + curr + os.sep + str(row.CNTY_NM) + os.sep + "Response from County")
		os.makedirs(newdir + os.sep + curr + os.sep + str(row.CNTY_NM) + os.sep + "Field Collected Data")
		os.makedirs(newdir + os.sep + curr + os.sep + str(row.CNTY_NM) + os.sep + "PreCollection Markup")
		prev = curr
	elif curr == prev:
		os.makedirs(newdir + os.sep + curr + os.sep + str(row.CNTY_NM))
		os.makedirs(newdir + os.sep + curr + os.sep + str(row.CNTY_NM) + os.sep + "Response from County")
		os.makedirs(newdir + os.sep + curr + os.sep + str(row.CNTY_NM) + os.sep + "Field Collected Data")
		os.makedirs(newdir + os.sep + curr + os.sep + str(row.CNTY_NM) + os.sep + "PreCollection Markup")

