# ---------------------------------------------------------------------------
# in_memory.py
# Created on: 2013-05-21 10:51:51.00000
#   (generated by ArcGIS/ModelBuilder)
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy


# Local variables:
Geocoding_DistOffices_shp = "C:\\TxDOT\\Scratch\\Geocoding_DistOffices.shp"
Geocoding_DistOffices_Dis = "in_memory\\Geocoding_DistOffices_Dis"

# Process: Dissolve
arcpy.Dissolve_management(Geocoding_DistOffices_shp, Geocoding_DistOffices_Dis, "FID", "", "MULTI_PART", "DISSOLVE_LINES")
