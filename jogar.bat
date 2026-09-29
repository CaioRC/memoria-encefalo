@echo off
rem Abre o jogo num servidor local (o navegador bloqueia ler o JSON direto do disco).
cd /d "%~dp0"
echo.
echo  Memoria do Encefalo
echo  -------------------
echo  Neste PC:   http://localhost:8000/
echo  No celular (mesmo Wi-Fi), abra um destes enderecos:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do for /f "tokens=*" %%b in ("%%a") do echo              http://%%b:8000/
echo.
echo  Deixe esta janela aberta enquanto joga. Feche para desligar.
echo.
start "" http://localhost:8000/
python -m http.server 8000
