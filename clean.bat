@echo off
for /d /r %%d in (__pycache__) do (
    if exist "%%d" (
        echo Excluindo pasta: %%d
        rd /s /q "%%d"
    )
)
