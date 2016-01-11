import arcpy, os, csv

def top100():
    locals = "C:\\Users\\JSYLVES\\Desktop\\Top100\\Top_100_Jenn.gdb\\Top100_9_10"
    path = "C:\\somehwere\\notHere"
    #roads = r"C:\_Local_Streets_2015\Final\Local_Streets.gdb\Local_Streets"
    print "Top 100 gaps."

    lastID = ""
    lastEMP = 0
    issues = [["GAP_SIZE", "RIA_RTE_ID"]]
    cursor = arcpy.da.SearchCursor(locals, ["NEW_FROM", "NEW_TO", "RIA_RTE_ID"], "FIXED <> 'D'", "", "", (None, "ORDER BY RIA_RTE_ID ASC, NEW_FROM ASC"))
    for row in cursor:
        bmp = row[0]
        emp = row[1]
        id = row[2]
        if id == lastID:
            diff = abs(lastEMP - bmp)
            if 0 < diff < .01:
                print "Gap Size, " + str(diff) + ", RIA_RTE_ID, " + id
                this = [id, diff]
                issues.append(this)

        lastID = id
        lastEMP = emp

    outputFile = open(path + "\\top100_Gaps.csv", 'wb')
    writer = csv.writer(outputFile)
    writer.writerows(issues)
    outputFile.close()


top100()
print "that's all folks!!"