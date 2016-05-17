__file__ = 'CR_AdjacentOverlap_v1'
__date__ = '2/4/14'
__author__ = 'ABREZNIC'
import arcpy, datetime
from arcpy import mapping
now = datetime.datetime.now()
suffixDate = now.strftime("%Y%m%d")

dbaseNAME = "Connection to Comanche.sde"
output = "C:\\TxDOT\\QC\\CountyRoad\\"
counties = "Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.County\\TPP_GIS.MCHAMB1.County"
roads = "Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.Roadways\\TPP_GIS.MCHAMB1.TXDOT_Roadways"
subfiles = "Database Connections\\" + dbaseNAME + "\\TPP_GIS.MCHAMB1.SUBFILES"
routedEvents = "routedEvents"
arcpy.AddMessage("Variables secured.")

arcpy.MakeRouteEventLayer_lr(roads, "RTE_ID", subfiles, "RTE_ID LINE BMP EMP", routedEvents)
lyr = mapping.Layer(routedEvents)
lyr.definitionQuery = """ "SUBFILE" = 2 AND "HIGHWAY_STATUS" = 4 AND "ADMIN_SYSTEM" = 3 AND "CONTROLSEC" NOT LIKE 'TOL%' AND "CONTROLSEC" NOT LIKE 'C%' AND "CONTROLSEC" NOT LIKE 'M%' """
intersected = output + "QC_AdjacentOverlap_" + suffixDate + ".shp"
arcpy.Intersect_analysis([lyr, counties], intersected)
arcpy.AddMessage("Intersect complete.")

#intersected = output + "QC_AdjacentOverlap_" + "20140204" + ".shp"

desc = arcpy.Describe(intersected)
shapefieldname = desc.ShapeFieldName

cursor = arcpy.UpdateCursor(intersected)
for row in cursor:
    if row.COUNTY == row.CNTY_NBR:
        cursor.deleteRow(row)
    else:
        feat = row.getValue(shapefieldname)
        fixedlen = round((feat.length*.000621371), 3)
        row.setValue("LEN_OF_SEC", fixedlen)
        cursor.updateRow(row)
del cursor

arcpy.AddMessage("Finished.\n" + str(intersected))


