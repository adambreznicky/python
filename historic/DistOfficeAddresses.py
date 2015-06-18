import arcpy
offices = "C:\\TxDOT\\Shapefiles\\District_Offices.shp"
cursor = arcpy.UpdateCursor(offices)
for row in cursor:
	address = row.getValue("Address")
	addressList = address.split(",")
	for item in addressList:
		Add_Num = str(addressList[0]).strip()
		City = str(addressList[1]).strip()
		ZipCode = str(addressList[2]).strip(" TX ")
		row.setValue("Add_Num",Add_Num)
		row.setValue("City",City)
		row.setValue("ZipCode",ZipCode)
		cursor.updateRow(row)
		print address
		

