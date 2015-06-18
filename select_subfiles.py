__file__ = 'select_subfiles'
__date__ = '9/25/2014'
__author__ = 'ABREZNIC'
import arcpy

mxd = arcpy.mapping.MapDocument("CURRENT")
layers = arcpy.mapping.ListLayers(mxd)
for lyr in layers:
    if lyr.name == "TXDOT_Roadways":
        arcpy.AddMessage("Accessing " + lyr.name)
        desc = arcpy.Describe(lyr)
        anything = len(desc.FIDSet)
        selection = len(desc.FIDSet.split(";"))
        if anything > 0:
            arcpy.AddMessage(str(selection) + " records selected.")
            roads = lyr
            tables = arcpy.mapping.ListTableViews(mxd)
            for tbl in tables:
                if tbl.name == "TPP_GIS.APP_TPP_GIS_ADMIN.SUBFILES":
                    subs = tbl
            id = []
            cursor = arcpy.da.SearchCursor(roads, ["RTE_ID"])
            for row in cursor:
                id.append(row[0])
            first = 0
            query = ""
            for i in id:
                if first == 0:
                    query += " RTE_ID = '" + i + "'"
                    first += 1
                else:
                    query += " OR RTE_ID = '" + i + "'"
            arcpy.SelectLayerByAttribute_management(subs, "NEW_SELECTION", query)
        else:
            arcpy.AddMessage("There are no features selected in " + lyr.name)
