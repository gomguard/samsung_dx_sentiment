@echo off
REM YouTube Batch Collection - Scheduled Task
REM This script runs the batch collection pipeline

cd /d D:\Gomguard\program\samsung_crawl\youtube_brand_analyzer

REM Create log filename with timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set LOG_FILE=batch_collect_scheduled_%datetime:~0,8%_%datetime:~8,6%.log

echo ======================================== >> %LOG_FILE%
echo Batch Collection Started >> %LOG_FILE%
echo Date/Time: %date% %time% >> %LOG_FILE%
echo ======================================== >> %LOG_FILE%

REM Run the batch collection script
"C:\Program Files\Python311\python.exe" batch_collect.py >> %LOG_FILE% 2>&1

echo ======================================== >> %LOG_FILE%
echo Batch Collection Completed >> %LOG_FILE%
echo Date/Time: %date% %time% >> %LOG_FILE%
echo ======================================== >> %LOG_FILE%

exit /b 0
