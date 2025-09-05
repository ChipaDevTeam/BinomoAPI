@echo off
REM BinomoAPI PyPI Deployment Script for Windows
REM Usage: deploy.bat [test|prod]

if "%1"=="" (
    echo Usage: deploy.bat [test^|prod]
    echo   test: Upload to Test PyPI
    echo   prod: Upload to production PyPI
    exit /b 1
)

if "%1" NEQ "test" if "%1" NEQ "prod" (
    echo Invalid argument. Use 'test' or 'prod'
    exit /b 1
)

echo BinomoAPI PyPI Deployment Script
echo Target: %1
echo.

python deploy.py %1
