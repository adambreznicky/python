Attribute VB_Name = "VB_Class_Road_Log_Intersect"
Dim theValues As String
Dim theMatch As Integer

Private Sub editRecordBySpatialQuery()
  Dim pMxDoc As IMxDocument
  Set pMxDoc = ThisDocument
  
  Dim pMap As IMap
  Set pMap = pMxDoc.FocusMap

  Dim pFLayer As IFeatureLayer
  Set pFLayer = pMxDoc.FocusMap.layer(0) 'the first layer

  Dim pFClass As IFeatureClass
  Set pFClass = pFLayer.featureclass

  Dim pFields As IFields
  Set pFields = pFClass.Fields

  Dim pFCursor As IFeatureCursor
  Set pFCursor = pFClass.Update(Nothing, False)

  Dim pFeature As IFeature
  Set pFeature = pFCursor.NextFeature
  
  Dim counter As Long
  counter = 0
  
  Dim theID As Long
  
  Do Until pFeature Is Nothing
    theID = pFeature.Value(pFeature.Fields.FindField("FID"))
    theMatch = pFeature.Value(pFeature.Fields.FindField("CNTY_NBR"))
    
    Call spatialQuery(pFeature.ShapeCopy)
    
    If Len(theValues) > 0 Then
       pFeature.Value(pFeature.Fields.FindField("MAP_ID")) = Right(theValues, Len(theValues) - 1) 'storing in the first layer
       pFeature.Store
    End If
        
    theValues = ""
    Set pFeature = pFCursor.NextFeature
    counter = counter + 1
    Debug.Print counter
  Loop
  
  pMxDoc.FocusMap.ClearSelection
  pMxDoc.ActiveView.Refresh
  MsgBox "Complete!"
End Sub

Private Sub spatialQuery(featureGeometry As IGeometry)
  Dim pMxDoc As IMxDocument
  Dim pMap As IMap
  Set pMxDoc = ThisDocument
  Set pMap = pMxDoc.FocusMap
  
  Dim pFeatureClass As IFeatureClass
  Dim pFeatLayer As IFeatureLayer
  Set pFeatLayer = pMap.layer(1) 'the second layer
  Set pFeatureClass = pFeatLayer.featureclass
  
  Dim pFilter As ISpatialFilter
  Set pFilter = New SpatialFilter

  With pFilter
    Set .geometry = featureGeometry
    .GeometryField = "Shape"
    .SpatialRel = esriSpatialRelIntersects
  End With
  
  Dim pFeatureCursor As IFeatureCursor
  Set pFeatureCursor = pFeatureClass.Search(pFilter, False)
  
  Dim pFeature As IFeature
  Set pFeature = pFeatureCursor.NextFeature
  
  Dim intersectMatch As Integer
  
  Do While (Not pFeature Is Nothing)
     intersectMatch = pFeature.Value(pFeature.Fields.FindField("CNTY_NBR"))
     
     If intersectMatch = theMatch Then
        theValues = theValues & "," & pFeature.Value(pFeature.Fields.FindField("MAP_ID")) 'data from the field in the second layer
     End If
     Set pFeature = pFeatureCursor.NextFeature
  Loop
End Sub


