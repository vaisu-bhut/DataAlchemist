@echo off
REM Test Docker builds locally before pushing

echo Testing Docker builds...
echo.

echo Building pubsub...
docker build -t pubsub:test -f pubsub/Dockerfile .
if errorlevel 1 goto :error
echo Pub/Sub build successful
echo.

echo Building master-agent...
docker build -t master-agent:test -f agents/master/Dockerfile .
if errorlevel 1 goto :error
echo Master Agent build successful
echo.

echo Building ingest-agent...
docker build -t ingest-agent:test -f agents/ingest/Dockerfile .
if errorlevel 1 goto :error
echo Ingest Agent build successful
echo.

echo Building chat-agent...
docker build -t chat-agent:test -f agents/chat/Dockerfile .
if errorlevel 1 goto :error
echo Chat Agent build successful
echo.

echo All builds successful!
echo.
echo Clean up test images:
echo   docker rmi pubsub:test master-agent:test ingest-agent:test chat-agent:test
goto :end

:error
echo Build failed!
exit /b 1

:end
