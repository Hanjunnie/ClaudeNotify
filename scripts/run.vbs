Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' scripts 폴더에서 상위 폴더(프로젝트 루트)로 이동
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
projectRoot = fso.GetParentFolderName(scriptDir) & "\"

If fso.FileExists(projectRoot & ".venv\Scripts\python.exe") Then
    pythonPath = projectRoot & ".venv\Scripts\python.exe"
ElseIf fso.FileExists(projectRoot & "venv\Scripts\python.exe") Then
    pythonPath = projectRoot & "venv\Scripts\python.exe"
Else
    MsgBox "Virtual environment not found. Please run scripts/install.bat first.", vbCritical, "Error"
    WScript.Quit
End If

mainPath = projectRoot & "src\main.py"
WshShell.CurrentDirectory = projectRoot
WshShell.Run """" & pythonPath & """ """ & mainPath & """", 0, False
