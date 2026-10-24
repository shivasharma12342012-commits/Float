Option Explicit

' Float Stop launcher
' Stops the running Float server silently.

Dim fso, shell, folder, batPath
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

folder = fso.GetParentFolderName(WScript.ScriptFullName)
batPath = folder & "\Stop Float.bat"

If Not fso.FileExists(batPath) Then
    MsgBox "Float can't find 'Stop Float.bat'.", vbCritical, "Float"
    WScript.Quit 1
End If

shell.Run "cmd /c """"" & batPath & """""", 0, True

Set shell = Nothing
Set fso = Nothing
