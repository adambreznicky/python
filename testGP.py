__file__ = 'test'
__date__ = '5/26/2015'
__author__ = 'ABREZNIC'
import arcpy, os

input = arcpy.GetParameterAsText(0)

rteclass = arcpy.GetParameterAsText(1)

output = arcpy.env.scratchFolder

output2 = output + os.sep + "RoadwaysClass" + rteclass + ".shp"
where = "RTE_CLASS = '" + rteclass + "'"
arcpy.Select_analysis(input, output2, where)


arcpy.AddMessage("that's all folks!")
print "that's all folks!"