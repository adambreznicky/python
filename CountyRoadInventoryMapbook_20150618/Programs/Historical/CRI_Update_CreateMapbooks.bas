Attribute VB_Name = "CRI_Update_CreateMapbooks"
Sub ChangeElement(cnty_nm, north, south, east, west, map_id)
Dim pMxDoc As IMxDocument
Set pMxDoc = ThisDocument

Dim pLayout As IPageLayout
Set pLayout = pMxDoc.PageLayout

Dim pGraphics As IGraphicsContainer
Set pGraphics = pLayout

pGraphics.Reset

Dim pElementProp As IElementProperties2
Set pElementProp = pGraphics.Next

Dim pTextElement As ITextElement

Do Until pElementProp Is Nothing
    Select Case pElementProp.Name
        Case "CountyName"
            Set pTextElement = pElementProp
            pTextElement.Text = cnty_nm & " County"
        Case "North"
            Set pTextElement = pElementProp
            pTextElement.Text = north
        Case "South"
            Set pTextElement = pElementProp
            pTextElement.Text = south
        Case "East"
            Set pTextElement = pElementProp
            pTextElement.Text = east
        Case "West"
            Set pTextElement = pElementProp
            pTextElement.Text = west
        Case "PageNumber"
            Set pTextElement = pElementProp
            pTextElement.Text = "Page-" & map_id
        End Select
    Set pElementProp = pGraphics.Next
Loop

Dim pActiveView As IActiveView
Set pActiveView = pGraphics
pActiveView.PartialRefresh esriViewGraphics, Nothing, Nothing
End Sub
Sub ExportPDF()
  Dim pMxDoc As IMxDocument
  Set pMxDoc = ThisDocument
  
  Dim pMap As IMap
  Set pMap = pMxDoc.FocusMap

  'uses first layer in map
  Dim pFLayer As IFeatureLayer
  Set pFLayer = pMxDoc.FocusMap.Layer(0)

  Dim pFClass As IFeatureClass
  Set pFClass = pFLayer.FeatureClass

  Dim pFields As IFields
  Set pFields = pFClass.fields

  Dim pFCursor As IFeatureCursor
  Set pFCursor = pFClass.Search(Nothing, False)

  Dim pFeature As IFeature
  Set pFeature = pFCursor.NextFeature

  Dim pEnvelope As IEnvelope
  Dim pActiveView As IActiveView
  Dim pExporter As IExport
  Dim pExporter2 As IExportPDF
  Dim exportFrame As tagRECT
  Dim hdc As Long
  Dim dpi As Integer
  Dim dXmin As Double, dYmin As Double, dXmax As Double, dYmax As Double

  Set pExporter = New ExportPDF
  Set pExporter2 = pExporter
  pExporter2.EmbedFonts = True
  
  'Set pActiveView = pMxDoc.FocusMap
  
  Dim counter As Long
  counter = 1

   Dim cnty_nm
   Dim north
   Dim south
   Dim east
   Dim west
   Dim map_id
   
  Do Until pFeature Is Nothing
  'If counter > 11142 Then
   
    Set pMxDoc.ActiveView = pMxDoc.FocusMap
    Set pActiveView = pMxDoc.FocusMap
    
    cnty_nm = pFeature.Value(pFeature.fields.FindField("CNTY_NM"))
    north = pFeature.Value(pFeature.fields.FindField("NORTH"))
    south = pFeature.Value(pFeature.fields.FindField("SOUTH"))
    east = pFeature.Value(pFeature.fields.FindField("EAST"))
    west = pFeature.Value(pFeature.fields.FindField("WEST"))
    map_id = pFeature.Value(pFeature.fields.FindField("Map_ID"))
    
    If north = 0 Then north = ""
    If south = 0 Then south = ""
    If east = 0 Then east = ""
    If west = 0 Then west = ""
    
     Set pEnvelope = pFeature.Extent
     'pEnvelope.Expand 1.25, 1.25, True
     pMxDoc.ActiveView.Extent = pEnvelope
    
    Set pMxDoc.ActiveView = pMxDoc.PageLayout
    Set pActiveView = pMxDoc.PageLayout
    
    Call ChangeElement(cnty_nm, north, south, east, west, map_id)
    
    exportFrame = pActiveView.exportFrame
    pEnvelope.PutCoords exportFrame.Left, exportFrame.Top, exportFrame.Right, exportFrame.bottom
    dpi = 96 'default screen resolution is usually 96
    
    If Len(Dir("D:\CRI_2010_PDFs\" & cnty_nm, vbDirectory)) = 0 Then
        MkDir "D:\CRI_2010_PDFs\" & cnty_nm
    End If
    
    With pExporter
      .PixelBounds = pEnvelope
      .ExportFileName = "D:\CRI_2010_PDFs\" & cnty_nm & "\" & cnty_nm & " " & map_id & ".pdf"
      .Resolution = dpi
    End With

    hdc = pExporter.StartExporting
    pActiveView.Output hdc, dpi, exportFrame, Nothing, Nothing
    pExporter.FinishExporting
    pExporter.Cleanup
  'End If
    
    'If counter = 15647 Then Exit Do
    counter = counter + 1
    Debug.Print counter
    Set pFeature = pFCursor.NextFeature
  Loop
  MsgBox "Last record " & counter
End Sub

