Option Compare Database

' Sample:
'        DirName = Left(CurrentDb.Name, Len(CurrentDb.Name) - Len(Dir(CurrentDb.Name)))
'        RunReportAsPDF "SampleReport", DirName & "SampleReport.pdf"


Private Declare Sub CopyMemory Lib "kernel32" _
              Alias "RtlMoveMemory" (dest As Any, _
                                     source As Any, _
                                     ByVal numBytes As Long)

Private Declare Function RegOpenKeyEx Lib "advapi32.dll" _
                  Alias "RegOpenKeyExA" (ByVal hKey As Long, _
                                         ByVal lpSubKey As String, _
                                         ByVal ulOptions As Long, _
                                         ByVal samDesired As Long, _
                                         phkResult As Long) As Long

Private Declare Function RegCloseKey Lib "advapi32.dll" (ByVal hKey As Long) As Long

Private Declare Function RegCreateKeyEx Lib "advapi32.dll" _
                   Alias "RegCreateKeyExA" (ByVal hKey As Long, _
                                            ByVal lpSubKey As String, _
                                            ByVal Reserved As Long, _
                                            ByVal lpClass As String, _
                                            ByVal dwOptions As Long, _
                                            ByVal samDesired As Long, _
                                            ByVal lpSecurityAttributes As Long, _
                                            phkResult As Long, _
                                            lpdwDisposition As Long) As Long

Private Declare Function RegQueryValueEx Lib "advapi32.dll" _
                   Alias "RegQueryValueExA" (ByVal hKey As Long, _
                                             ByVal lpValueName As String, _
                                             ByVal lpReserved As Long, _
                                             lpType As Long, _
                                             lpData As Any, _
                                             lpcbData As Long) As Long

Private Declare Function RegSetValueEx Lib "advapi32.dll" _
                   Alias "RegSetValueExA" (ByVal hKey As Long, _
                                           ByVal lpValueName As String, _
                                           ByVal Reserved As Long, _
                                           ByVal dwType As Long, _
                                           lpData As Any, _
                                           ByVal cbData As Long) As Long

Private Declare Function apiFindExecutable Lib "shell32.dll" _
                  Alias "FindExecutableA" (ByVal lpFile As String, _
                                           ByVal lpDirectory As String, _
                                           ByVal lpResult As String) As Long

Const REG_SZ = 1
Const REG_EXPAND_SZ = 2
Const REG_BINARY = 3
Const REG_DWORD = 4
Const REG_MULTI_SZ = 7
Const ERROR_MORE_DATA = 234

Public Const HKEY_CLASSES_ROOT = &H80000000
Public Const HKEY_CURRENT_USER = &H80000001
Public Const HKEY_LOCAL_MACHINE = &H80000002

Const KEY_READ = &H20019  ' ((READ_CONTROL Or KEY_QUERY_VALUE Or
                          ' KEY_ENUMERATE_SUB_KEYS Or KEY_NOTIFY) And (Not
                          ' SYNCHRONIZE))

Const KEY_WRITE = &H20006  '((STANDARD_RIGHTS_WRITE Or KEY_SET_VALUE Or
                           ' KEY_CREATE_SUB_KEY) And (Not SYNCHRONIZE))

Public Function RunReportAsPDF(prmRptName As String, _
                               prmPdfName As String) As Boolean

' Returns TRUE if a PDF file has been created

Dim AdobeDevice As String
Dim strDefaultPrinter As String

'Find the Acrobat PDF device

AdobeDevice = GetRegistryValue(HKEY_CURRENT_USER, _
                               "Software\Microsoft\WIndows NT\CurrentVersion\Devices", _
                               "Adobe PDF")


If AdobeDevice = "" Then    ' The device was not found
    MsgBox "You must install Acrobat Writer before using this feature"
    RunReportAsPDF = False
    Exit Function
End If

' get current default printer.
strDefaultPrinter = Application.Printer.DeviceName

Set Application.Printer = Application.Printers("Adobe PDF")


'Create the Registry Key where Acrobat looks for a file name
CreateNewRegistryKey HKEY_CURRENT_USER, _
                     "Software\Adobe\Acrobat Distiller\PrinterJobControl"

'Put the output filename where Acrobat could find it
SetRegistryValue HKEY_CURRENT_USER, _
                 "Software\Adobe\Acrobat Distiller\PrinterJobControl", _
                 Find_Exe_Name(CurrentDb.Name, CurrentDb.Name), _
                 prmPdfName

On Error GoTo Err_handler

DoCmd.OpenReport prmRptName, acViewNormal   'Run the report

While Len(Dir(prmPdfName)) = 0              ' Wait for the PDF to actually exist
    DoEvents
Wend

RunReportAsPDF = True       ' Mission accomplished!

Normal_Exit:

Set Application.Printer = Application.Printers(strDefaultPrinter)   ' Restore default printer


On Error GoTo 0

Exit Function

Err_handler:

If Err.Number = 2501 Then       ' The report did not run properly (ex NO DATA)
    RunReportAsPDF = False
    Resume Normal_Exit
Else
    RunReportAsPDF = False      ' The report did not run properly (anything else!)
    MsgBox "Unexpected error #" & Err.Number & " - " & Err.Description
    Resume Normal_Exit
End If

End Function

Public Function Find_Exe_Name(prmFile As String, _
                              prmDir As String) As String

Dim Return_Code As Long
Dim Return_Value As String

Return_Value = Space(260)
Return_Code = apiFindExecutable(prmFile, prmDir, Return_Value)

If Return_Code > 32 Then
    Find_Exe_Name = Return_Value
Else
    Find_Exe_Name = "Error: File Not Found"
End If

End Function

Public Sub CreateNewRegistryKey(prmPredefKey As Long, _
                                prmNewKey As String)

' Example #1:  CreateNewRegistryKey HKEY_CURRENT_USER, "TestKey"
'
'              Create a key called TestKey immediately under HKEY_CURRENT_USER.
'
' Example #2:  CreateNewRegistryKey HKEY_LOCAL_MACHINE, "TestKey\SubKey1\SubKey2"
'
'              Creates three-nested keys beginning with TestKey immediately under
'              HKEY_LOCAL_MACHINE, SubKey1 subordinate to TestKey, and SubKey3 under SubKey2.
'
Dim hNewKey As Long         'handle to the new key
Dim lRetVal As Long         'result of the RegCreateKeyEx function

lRetVal = RegOpenKeyEx(prmPredefKey, prmNewKey, 0, KEY_ALL_ACCESS, hKey)

If lRetVal <> 5 Then
    lRetVal = RegCreateKeyEx(prmPredefKey, prmNewKey, 0&, _
                             vbNullString, REG_OPTION_NON_VOLATILE, _
                             KEY_ALL_ACCESS, 0&, hNewKey, lRetVal)
End If

RegCloseKey (hNewKey)

End Sub

Function GetRegistryValue(ByVal hKey As Long, _
                          ByVal KeyName As String, _
                          ByVal ValueName As String, _
                          Optional DefaultValue As Variant) As Variant

Dim handle As Long
Dim resLong As Long
Dim resString As String
Dim resBinary() As Byte
Dim Length As Long
Dim retVal As Long
Dim valueType As Long
    
' Read a Registry value
'
' Use KeyName = "" for the default value
' If the value isn't there, it returns the DefaultValue
' argument, or Empty if the argument has been omitted
'
' Supports DWORD, REG_SZ, REG_EXPAND_SZ, REG_BINARY and REG_MULTI_SZ
' REG_MULTI_SZ values are returned as a null-delimited stream of strings
' (VB6 users can use SPlit to convert to an array of string)

    
' Prepare the default result
GetRegistryValue = IIf(IsMissing(DefaultValue), Empty, DefaultValue)

' Open the key, exit if not found.
If RegOpenKeyEx(hKey, KeyName, 0, KEY_READ, handle) Then
    Exit Function
End If

' prepare a 1K receiving resBinary
Length = 1024
ReDim resBinary(0 To Length - 1) As Byte

' read the registry key
retVal = RegQueryValueEx(handle, ValueName, 0, valueType, resBinary(0), Length)

' if resBinary was too small, try again
If retVal = ERROR_MORE_DATA Then
    ' enlarge the resBinary, and read the value again
    ReDim resBinary(0 To Length - 1) As Byte
    retVal = RegQueryValueEx(handle, ValueName, 0, valueType, resBinary(0), _
        Length)
End If

' return a value corresponding to the value type
Select Case valueType
    Case REG_DWORD
        CopyMemory resLong, resBinary(0), 4
        GetRegistryValue = resLong
    Case REG_SZ, REG_EXPAND_SZ
        ' copy everything but the trailing null char
        resString = Space$(Length - 1)
        CopyMemory ByVal resString, resBinary(0), Length - 1
        GetRegistryValue = resString
    Case REG_BINARY
        ' resize the result resBinary
        If Length <> UBound(resBinary) + 1 Then
            ReDim Preserve resBinary(0 To Length - 1) As Byte
        End If
        GetRegistryValue = resBinary()
    Case REG_MULTI_SZ
        ' copy everything but the 2 trailing null chars
        resString = Space$(Length - 2)
        CopyMemory ByVal resString, resBinary(0), Length - 2
        GetRegistryValue = resString
    Case Else
        GetRegistryValue = ""
'        RegCloseKey handle
'        Err.Raise 1001, , "Unsupported value type"
End Select

RegCloseKey handle  ' close the registry key
    
End Function

Function SetRegistryValue(ByVal hKey As Long, _
                          ByVal KeyName As String, _
                          ByVal ValueName As String, _
                          Value As Variant) As Boolean
                          
' Write or Create a Registry value
' returns True if successful
'
' Use KeyName = "" for the default value
'
' Value can be an integer value (REG_DWORD), a string (REG_SZ)
' or an array of binary (REG_BINARY). Raises an error otherwise.

Dim handle As Long
Dim lngValue As Long
Dim strValue As String
Dim binValue() As Byte
Dim byteValue As Byte
Dim Length As Long
Dim retVal As Long

' Open the key, exit if not found
If RegOpenKeyEx(hKey, KeyName, 0, KEY_WRITE, handle) Then
    Exit Function
End If

' three cases, according to the data type in Value
Select Case VarType(Value)
    Case vbInteger, vbLong
        lngValue = Value
        retVal = RegSetValueEx(handle, ValueName, 0, REG_DWORD, lngValue, 4)
    Case vbString
        strValue = Value
        retVal = RegSetValueEx(handle, ValueName, 0, REG_SZ, ByVal strValue, Len(strValue))
    Case vbArray
        binValue = Value
        Length = UBound(binValue) - LBound(binValue) + 1
        retVal = RegSetValueEx(handle, ValueName, 0, REG_BINARY, binValue(LBound(binValue)), Length)
    Case vbByte
        byteValue = Value
        Length = 1
        retVal = RegSetValueEx(handle, ValueName, 0, REG_BINARY, byteValue, Length)
    Case Else
        RegCloseKey handle
        Err.Raise 1001, , "Unsupported value type"
End Select

RegCloseKey handle  ' Close the key and signal success

SetRegistryValue = (retVal = 0)     ' signal success if the value was written correctly

End Function
