Attribute VB_Name = "ReNameFiles"
Public Sub RenameFiles()
    Dim FSys As Object
    Dim ThisFolder As Object
    Dim SubFolders As Object
    Dim AllFiles As Object
    Dim file As Object
    Dim folder As Object
    
    Dim counter As Integer
    counter = 0
    
    Dim newFileName As String
    
    On Error Resume Next
    Set FSys = CreateObject("Scripting.FileSystemObject")
    Set ThisFolder = FSys.GetFolder("T:\DATAMGT\MAPPING\Mapping Products\County Road Update Mapbooks\2008\Mapbook Pages\CRI_2009_PDFs")
    Set SubFolders = ThisFolder.SubFolders
    'Set AllFiles = ThisFolder.Files
    
    For Each folder In SubFolders
      Set AllFiles = folder.Files
      For Each file In AllFiles
        newFileName = formatFileName(file.Name)
        file.Name = newFileName
        'Debug.Print file.Name
      Next
      'Debug.Print folder.Name
      counter = counter + 1
      Debug.Print counter
    Next
End Sub

Public Function formatFileName(theName)
Dim theLeft As String
Dim theRight As String
Dim newName As String

theLeft = Left(theName, Len(theName) - 7)
theRight = Right(theName, 7)

If Left(theRight, 1) = " " Then
   newName = theLeft & " 0" & Right(theRight, 6)
End If

If Mid(theRight, 2, 1) = " " Then
   newName = theLeft & Left(theRight, 1) & " 00" & Right(theRight, 5)
End If

If Left(theRight, 1) = "1" Then
   newName = theLeft & theRight
End If

If Left(theRight, 1) = "2" Then
   newName = theLeft & theRight
End If

If Left(theRight, 1) = "3" Then
   newName = theLeft & theRight
End If

If Left(theRight, 1) = "4" Then
   newName = theLeft & theRight
End If

If Left(theRight, 1) = "5" Then
   newName = theLeft & theRight
End If

If Left(theRight, 1) = "6" Then
   newName = theLeft & theRight
End If

If Left(theRight, 1) = "7" Then
   newName = theLeft & theRight
End If

'Debug.Print newName
formatFileName = newName
End Function
