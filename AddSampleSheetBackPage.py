from PyPDF2 import PdfFileMerger
import operator
import os


def fileMerge(district, sorted_fileDict):
    '''Creates a list of files to be exported for each district'''
    print "Creating Bound PDF for %s District" % district
    # Add path to the individual sample sheets
    sampleSheetPath = "T:\\DATAMGT\\HPMS-DATA\\2013Data\\2013 Sample Sheets\\PDFs\\PDFs"
    # Add the output path
    outputPath = sampleSheetPath + os.sep + "Combined"
    # Create an instance of the PdfFileMerger.merger class
    merger = PdfFileMerger()
    total = len(sorted_fileDict)
    counter = 0
    # Iterate through the sorted file dictionary view to export PDF's
    for sampleID, fileName in sorted_fileDict:

        counter += 1
        print "...adding sheet %i of %i" % (counter, total)

        input1 = open(sampleSheetPath + os.sep + fileName, "rb")
        input2 = open("T:\\DATAMGT\\HPMS-DATA\\2012Data\\Field Reviews\\Field Review Sample Selection\\SectionID_Maps\\assets\\HPMS Back Page Worksheet - Copy.pdf", "rb")

        # append entire input3 document to the end of the output document
        merger.append(input1, "Sample " + str(sampleID))
        merger.append(input2)

    # Write to an output PDF document
    output = open(outputPath + os.sep + district + "_District_Merged.pdf", "wb")
    print "Saving bound PDF for %s District" % district
    merger.write(output)
    del merger


def createSampleSheetList():
    '''Creates a list of files to be exported for each district'''
    sampleSheetPath = "T:\\DATAMGT\\HPMS-DATA\\2013Data\\2013 Sample Sheets\\PDFs\\PDFs"
    outputPath = sampleSheetPath + os.sep + "Combined"
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    sampleSheets = os.listdir(sampleSheetPath)
    counter = len(sampleSheets)
    if "Combined" in sampleSheets:
        sampleSheets.remove("Combined")
    district = ""
    previousDistrict = ""
    fileDict = {}
    for sheet in sampleSheets:
        district = str(sheet).split("_")[0]
        sampleKey = int(((str(sheet).split("_")[3])).split(".")[0])
        if district == previousDistrict or previousDistrict == "" or district is None:
            fileDict[sampleKey] = sheet
            previousDistrict = district
            counter -= 1
        elif counter == 1:
            sorted_fileDict = sorted(fileDict.iteritems(), key=operator.itemgetter(0))
            fileMerge(previousDistrict, sorted_fileDict)
            fileDict = {}
            fileDict[sampleKey] = sheet
        else:
            sorted_fileDict = sorted(fileDict.iteritems(), key=operator.itemgetter(0))
            fileMerge(previousDistrict, sorted_fileDict)
            fileDict = {}
            fileDict[sampleKey] = sheet
        previousDistrict = district


createSampleSheetList()