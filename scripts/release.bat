@echo off
REM BuildScan 3D — Release Script
REM Usage: scripts\release.bat 0.3.0
REM   Bumps the version, commits, tags, and pushes. GitHub Actions builds the APK.

setlocal enabledelayedexpansion
cd /d %~dp0..

if "%~1"=="" (
    echo.
    echo  Usage: scripts\release.bat ^<version^>
    echo  Example: scripts\release.bat 0.3.0
    echo.
    echo  This will:
    echo    1. Update versionName in build.gradle
    echo    2. Increment versionCode
    echo    3. Commit and tag as v^<version^>
    echo    4. Push to GitHub ^(triggers APK build + GitHub Release^)
    echo.
    exit /b 1
)

set "VERSION=%~1"
set "GRADLE=googleARCore\samples\hello_ar_java\app\build.gradle"

REM Get current versionCode
for /f "tokens=2" %%A in ('findstr /C:"versionCode" "%GRADLE%"') do set "OLD_CODE=%%A"
set /a NEW_CODE=%OLD_CODE%+1

echo.
echo  BuildScan 3D Release
echo  ====================
echo  Version: %VERSION% (v%VERSION%)
echo  versionCode: %OLD_CODE% -^> %NEW_CODE%
echo.

REM Update build.gradle
powershell -Command "(Get-Content '%GRADLE%') -replace 'versionCode \d+', 'versionCode %NEW_CODE%' -replace \"versionName '.*'\", \"versionName '%VERSION%'\" | Set-Content '%GRADLE%' -Encoding utf8"

REM Commit
git add "%GRADLE%"
git commit -m "release: v%VERSION% (versionCode %NEW_CODE%)"
if errorlevel 1 (
    echo  ERROR: Commit failed
    exit /b 1
)

REM Tag
git tag "v%VERSION%"
if errorlevel 1 (
    echo  ERROR: Tag v%VERSION% already exists
    exit /b 1
)

REM Push commit and tag
echo  Pushing to GitHub...
git push origin master
git push origin "v%VERSION%"

echo.
echo  Done! GitHub Actions will now:
echo    1. Run CI tests
echo    2. Build the APK
echo    3. Create GitHub Release at:
echo       https://github.com/Umairishuman/FYP/releases/tag/v%VERSION%
echo.
echo  Users with the old app will see an update prompt on next launch.
echo.
