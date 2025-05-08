@echo off
echo Pushing Commodity-price-dashboard to GitHub (master branch)
echo ========================================================
echo.

REM Navigate to the repository directory
cd /d "%~dp0"

REM Display current status
echo Current Git Status:
git status
echo.

REM Push to GitHub
echo Pushing to GitHub master branch...
git push -u origin master

echo.
echo If you encounter authentication issues, please:
echo 1. Use GitHub Desktop instead (recommended)
echo 2. Generate a personal access token at https://github.com/settings/tokens
echo 3. Use the token as your password when prompted

pause