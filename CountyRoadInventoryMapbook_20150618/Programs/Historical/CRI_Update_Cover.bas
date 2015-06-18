Attribute VB_Name = "CRI_Update_Cover"
Sub ChangeElement(sheet_name)
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
        Case "Sheet"
            Set pTextElement = pElementProp
            pTextElement.Text = sheet_name & " - 2009"
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
  
  Dim iOutputResolution As Integer
  Dim iScreenResolution As Integer
  
  iScreenResolution = 96  'default screen resolution is usually 96dpi
  iOutputResolution = 300
  pExporter.Resolution = iOutputResolution
  
  Dim counter As Long
  counter = 1
 
  Dim sheet_nm
  Dim cycle
  
  Do Until pFeature Is Nothing
    Set pMxDoc.ActiveView = pMxDoc.FocusMap
    Set pActiveView = pMxDoc.FocusMap
    
    sheet_nm = pFeature.VALUE(pFeature.fields.FindField("CNTY_NM"))
    
    Set pMxDoc.ActiveView = pMxDoc.PageLayout
    Set pActiveView = pMxDoc.PageLayout
    
    Call ChangeElement(sheet_nm)
    
    With exportFrame
    .Left = 0
    .Top = 0
    .Right = pActiveView.exportFrame.Right * (iOutputResolution / iScreenResolution)
    .bottom = pActiveView.exportFrame.bottom * (iOutputResolution / iScreenResolution)
    End With
    
    'Set up the PixelBounds envelope to match the exportRECT
    Set pEnvelope = New Envelope
    pEnvelope.PutCoords exportFrame.Left, exportFrame.Top, exportFrame.Right, exportFrame.bottom
    pExporter.PixelBounds = pEnvelope
    pExporter.ExportFileName = "T:\DATAMGT\MAPPING\Mapping Products\County Road Update Mapbooks\Common Mapping Items\Cover\PDF\" & sheet_nm & ".pdf"

    hdc = pExporter.StartExporting
    pActiveView.Output hdc, pExporter.Resolution, exportFrame, Nothing, Nothing
    pExporter.FinishExporting
    pExporter.Cleanup
        
    counter = counter + 1
    Set pFeature = pFCursor.NextFeature
  Loop
  MsgBox "Last record " & counter - 1
End Sub

