@echo off
chcp 65001 >nul
REM Prueba de aceptacion funcional contra el despliegue. Ejecutar desde la carpeta que contiene "aceptacion\"
set BASE=http://verifacts-sistema-ju3vi7-444522-144-24-4-187.sslip.io
set OUT=evidencia-aceptacion.txt

echo ACEPTACION FUNCIONAL VERIFACTS > %OUT%
echo Base: %BASE% >> %OUT%
echo Inicio: %DATE% %TIME% >> %OUT%
echo. >> %OUT%

echo ===== C1 GET /health ===== >> %OUT%
curl -s -m 30 -w "\nHTTP %%{http_code}\n" %BASE%/health >> %OUT%

echo ===== C2 GET / (interfaz) ===== >> %OUT%
curl -s -m 30 -o NUL -w "HTTP %%{http_code} tipo %%{content_type}\n" %BASE%/ >> %OUT%

echo ===== C3 POST /analysis texto ===== >> %OUT%
curl -s -m 60 -w "\nHTTP %%{http_code}\n" -H "Content-Type: application/json" --data @aceptacion\texto.json %BASE%/analysis >> %OUT%

echo ===== C4 POST /analysis URL publica ===== >> %OUT%
curl -s -m 60 -w "\nHTTP %%{http_code}\n" -H "Content-Type: application/json" --data @aceptacion\url-valida.json %BASE%/analysis >> %OUT%

echo ===== C5 POST /analysis URL invalida (error controlado esperado) ===== >> %OUT%
curl -s -m 60 -w "\nHTTP %%{http_code}\n" -H "Content-Type: application/json" --data @aceptacion\url-invalida.json %BASE%/analysis >> %OUT%

echo ===== C6 POST /analysis contenido vacio (esperado 4xx) ===== >> %OUT%
curl -s -m 30 -w "\nHTTP %%{http_code}\n" -H "Content-Type: application/json" --data @aceptacion\vacio.json %BASE%/analysis >> %OUT%

echo ===== C7 GET /analysis?limit=5 (historial) ===== >> %OUT%
curl -s -m 30 -w "\nHTTP %%{http_code}\n" "%BASE%/analysis?limit=5&offset=0" >> %OUT%

echo ===== C8 GET /analysis/999999 (inexistente, esperado 404) ===== >> %OUT%
curl -s -m 30 -w "\nHTTP %%{http_code}\n" %BASE%/analysis/999999 >> %OUT%

echo. >> %OUT%
echo Fin: %DATE% %TIME% >> %OUT%
echo Listo. Revisa %OUT%
