@echo off
setlocal

:: Set the target directory to the current directory
set "TARGET_DIR=%cd%"

:: Check if the .exe file exists
if not exist "%TARGET_DIR%\main.exe" (
    echo .exe file not found. Make sure the executable is in the current directory.
) else (
    echo .exe file exists.
)

:: Check if art_styles.json exists, if not, create it and add the content
if not exist "%TARGET_DIR%\art_styles.json" (
    echo Creating art_styles.json...
    echo [ > "%TARGET_DIR%\art_styles.json"
    echo     { >> "%TARGET_DIR%\art_styles.json"
    echo         "name": "Hand Drawn", >> "%TARGET_DIR%\art_styles.json"
    echo         "description": "Apply a hand-drawn art style to the image, emphasizing bold, visible brushstrokes and rich textures to enhance artistic qualities." >> "%TARGET_DIR%\art_styles.json"
    echo     } >> "%TARGET_DIR%\art_styles.json"
    echo ] >> "%TARGET_DIR%\art_styles.json"
    echo art_styles.json created.
) else (
    echo art_styles.json already exists.
)

:: Check if image_restyle_description.txt exists, if not, create it as an empty file
if not exist "%TARGET_DIR%\image_restyle_description.txt" (
    echo Creating image_restyle_description.txt...
    type nul > "%TARGET_DIR%\image_restyle_description.txt"
    echo image_restyle_description.txt created.
) else (
    echo image_restyle_description.txt already exists.
)

:: Check if storage.txt exists, if not, create it and add the placeholder API key
if not exist "%TARGET_DIR%\storage.txt" (
    echo Creating storage.txt with DeepAI key placeholder...
    echo deepai-key: "Yourkeyhere" > "%TARGET_DIR%\storage.txt"
    echo storage.txt created.
) else (
    echo storage.txt already exists.
)

echo All files are set up in the current directory.

endlocal
pause
