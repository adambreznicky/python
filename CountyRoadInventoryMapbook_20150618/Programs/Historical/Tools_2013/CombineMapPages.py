import arcpy, os, string

Counties = arcpy.GetParameterAsText(0)
fc = Counties
rows = arcpy.SearchCursor(fc) 
DataYear = arcpy.GetParameterAsText(1)


x = 1
pagevalue = "000"
for row in rows:
    print row.CNTY_NM
    print "T:\\DATAMGT\\MAPPING\\Mapping Products\\County Road Update Mapbooks\\" + DataYear + "\\Combined PDF\\PDF\\" + row.CNTY_U + "_MAPBOOK_" + DataYear + ".pdf"
    #Set file name and remove if it already exists
    pdfPath = "T:\\DATAMGT\\MAPPING\\Mapping Products\\County Road Update Mapbooks\\" + DataYear + "\\Combined PDF\\PDF\\" + row.CNTY_U  + "_MAPBOOK_" + DataYear + ".pdf"
    if os.path.exists(pdfPath):
        os.remove(pdfPath)

    #Create the file and append pages
    pdfDoc = arcpy.mapping.PDFDocumentCreate(pdfPath)
    pdfDoc.appendPages("T:\\DATAMGT\\MAPPING\\Mapping Products\\County Road Update Mapbooks\\" + DataYear + "\\Mapbook Covers\\" + row.CNTY_NM + ".pdf")
    print "T:\\DATAMGT\\MAPPING\\Mapping Products\\County Road Update Mapbooks\\" + DataYear + "\\Mapbook Covers\\" + row.CNTY_NM + ".pdf"
    pdfDoc.appendPages("T:\\DATAMGT\\MAPPING\\Mapping Products\\County Road Update Mapbooks\\Common Mapping Items\\County Grid Index\\" + row.CNTY_NM + " County Mapbook Index.pdf")
    print "T:\\DATAMGT\\MAPPING\\Mapping Products\\County Road Update Mapbooks\\Common Mapping Items\\County Grid Index\\" + row.CNTY_NM + " County Mapbook Index.pdf"
    pdfDoc.appendPages("T:\\DATAMGT\\MAPPING\\Mapping Products\\County Road Update Mapbooks\\" + DataYear + "\\Legend\\Legend_" + DataYear + ".pdf")
    print "T:\\DATAMGT\\MAPPING\\Mapping Products\\County Road Update Mapbooks\\" + DataYear + "\\Legend\\Legend_\\" + DataYear + ".pdf"

    x = 1 
    while x <= row.Max_Pages:
        currentpage = x
        pagevalue = str(currentpage)
        print "T:\\DATAMGT\\MAPPING\\Mapping Products\\County Road Update Mapbooks\\" + DataYear + "\\Mapbook Pages\\" + row.CNTY_NM + " "+ pagevalue + ".pdf"
        pdfDoc.appendPages("T:\\DATAMGT\\MAPPING\\Mapping Products\\County Road Update Mapbooks\\" + DataYear + "\\Mapbook Pages\\" + row.CNTY_NM + " " + pagevalue + ".pdf")
        x += 1
                           
#Commit changes and delete variable reference
pdfDoc.saveAndClose()
del pdfDoc