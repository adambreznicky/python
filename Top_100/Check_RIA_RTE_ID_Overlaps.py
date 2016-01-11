import arcpy, os

def top100():
    locals = r"C:\\Users\\JSYLVES\\Desktop\\Top100\\Top_100_Jenn.gdb\\Top100_9_10"
    #roads = r"C:\_Local_Streets_2015\Final\Local_Streets.gdb\\Local_Streets"
    print "Top 100 overlaps."
    dictionary = {}
    cursor = arcpy.da.SearchCursor(locals, [ "NEW_FROM", "NEW_TO", "RIA_RTE_ID"], "FIXED <> 'D'", "", "", (None, "ORDER BY RIA_RTE_ID ASC, NEW_FROM ASC"))
    for row in cursor:
        bmp = int(row[0] * 1000)
        emp = int(row[1] * 1000)
        key = row[2]
        if key in dictionary.keys():
            current = dictionary[key]
            for record in current:
                if bmp in record:
                    print "Overlap Measure, " + str(row[0]) + ","  + "RIA_RTE_ID, " + row[2]
                elif emp in record:
                    print "Overlap Measure, " + str(row[0]) + ","  + "RIA_RTE_ID, " + row[2]
            ranger = range(bmp, emp)
            current.append(ranger)
            dictionary[key] = current
        else:
            ranger = range(bmp, emp)
            dictionary[key] = [ranger]

top100()
