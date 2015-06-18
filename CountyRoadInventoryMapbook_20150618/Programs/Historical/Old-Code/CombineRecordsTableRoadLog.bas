Attribute VB_Name = "CombineRecordsTableRoadLog"

Public Sub CombineRecordsTableRoadLog()
  Dim pMxDoc As IMxDocument
  Dim pMap As IStandaloneTableCollection
  Dim pStdAloneTbl As IStandaloneTable
  Dim pTableSel As ITableSelection
  Dim pQueryFilt As IQueryFilter
  Dim pSelSet As ISelectionSet
  ' Get the standalone table from the map
  Set pMxDoc = Application.document
  Set pMap = pMxDoc.FocusMap
  Set pStdAloneTbl = pMap.StandaloneTable(0)
  Set pTableSel = pStdAloneTbl
' Make the query filter
  Set pQueryFilt = New QueryFilter
  pQueryFilt.WhereClause = "OBJECTID >= 0"
' Perform the selection
  pTableSel.SelectRows pQueryFilt, esriSelectionResultNew, False
' Report how many rows were selected
  Set pSelSet = pTableSel.SelectionSet
  
  Dim sTextFileName As String
  Dim fileid As Integer
  fileid = FreeFile()
  
  Dim current As String
  Dim previous As String
  
  Dim counter As Long
  counter = 0
  
  Dim secondaryCounter As Integer
  secondaryCounter = 1
  
  Dim pTable As ITable
  Set pTable = pMap.StandaloneTable(0)

  Dim folderName As String
    
  sTextFileName = "D:\Grids.txt"
  Open sTextFileName For Output As fileid

  Dim multPage As String
  multPage = ""
    
  Dim currPAGE As String
  currPAGE = ""
   
  Dim i As Long
  Dim pRow As IRow
  For i = 0 To pSelSet.Count - 1
        Set pRow = pTable.GetRow(i)
            current = pRow.Value(pRow.fields.FindField("First_Flag"))
            currPAGE = pRow.Value(pRow.fields.FindField("Min_Map_ID"))
            
            If counter = 0 Then
              previous = current
            End If
      
            If previous = current Then
               multPage = multPage & "," & currPAGE
            Else
               Print #fileid, previous & "*" & multPage
               multPage = ""
               multPage = "," & currPAGE
            End If
        
            previous = current
            counter = counter + 1

        Debug.Print i

  Next i
  Close #fileid
  MsgBox "Complete"
End Sub




