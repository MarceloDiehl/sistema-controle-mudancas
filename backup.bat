@echo off
rem Backup do banco do Controle de Demandas de Mudancas.
rem Gera, na pasta deste arquivo, backup_ditic_mudancas_AAAA-MM-DD_HHMM.sql com as tabelas e todos os dados.
rem Pode rodar com o sistema no ar: o backup sai como uma foto do banco naquele instante.
rem
rem Para restaurar (no MySQL Workbench, como root): File > Open SQL Script, abra o arquivo do backup e execute.
rem O arquivo recria o banco ditic_mudancas_db e as tabelas (apaga o que estiver nelas) com os dados do backup.
rem (Arquivo sem acentos de proposito: o cmd do Windows le errado um .bat acentuado.)
title Backup do banco - Controle de Demandas de Mudancas
cd /d "%~dp0"

rem ---------------------------------------------------------------- ajustes
set "BANCO=ditic_mudancas_db"
set "USUARIO=ditic_admin"
rem Senha do MySQL: em branco quando o usuario nao tem senha. Preencha so na copia da maquina; NUNCA no Git.
set "SENHA_BANCO="
set "SERVIDOR=localhost"
set "PORTA_BANCO=3306"
rem ------------------------------------------------------------------------

rem procura o mysqldump: no PATH ou nas pastas de instalacao do MySQL Server, do Workbench e do XAMPP
set "DUMP="
for %%x in (mysqldump.exe) do if not "%%~$PATH:x"=="" set "DUMP=%%~$PATH:x"
if not defined DUMP for /d %%d in ("%ProgramFiles%\MySQL\MySQL Server*") do if exist "%%d\bin\mysqldump.exe" set "DUMP=%%d\bin\mysqldump.exe"
if not defined DUMP for /d %%d in ("%ProgramFiles%\MySQL\MySQL Workbench*") do if exist "%%d\mysqldump.exe" set "DUMP=%%d\mysqldump.exe"
if not defined DUMP for /d %%d in ("%ProgramFiles(x86)%\MySQL\MySQL Server*") do if exist "%%d\bin\mysqldump.exe" set "DUMP=%%d\bin\mysqldump.exe"
if not defined DUMP for /d %%d in ("%ProgramFiles(x86)%\MySQL\MySQL Workbench*") do if exist "%%d\mysqldump.exe" set "DUMP=%%d\mysqldump.exe"
if not defined DUMP if exist "C:\xampp\mysql\bin\mysqldump.exe" set "DUMP=C:\xampp\mysql\bin\mysqldump.exe"
if not defined DUMP (
    echo Nao achei o mysqldump. Ele vem com o MySQL Server ou com o MySQL Workbench.
    echo Se estiver em outra pasta, coloque o caminho completo na linha set "DUMP=" deste arquivo.
    pause
    exit /b 1
)

rem data e hora no nome do arquivo (o mesmo formato em qualquer configuracao regional do Windows)
for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyy-MM-dd_HHmm"') do set "QUANDO=%%i"
set "ARQUIVO=backup_ditic_mudancas_%QUANDO%.sql"

if defined SENHA_BANCO (set "MYSQL_PWD=%SENHA_BANCO%") else (set "MYSQL_PWD=")

echo Gerando o backup do banco %BANCO%...
echo Programa: %DUMP%
"%DUMP%" --host=%SERVIDOR% --port=%PORTA_BANCO% --user=%USUARIO% --default-character-set=utf8mb4 --single-transaction --no-tablespaces --skip-triggers --set-gtid-purged=OFF --add-drop-table --databases %BANCO% --result-file="%ARQUIVO%"
set "ERRO=%errorlevel%"
set "MYSQL_PWD="

echo.
if not "%ERRO%"=="0" (
    if exist "%ARQUIVO%" del "%ARQUIVO%"
    echo O backup FALHOU. Veja a mensagem acima: o MySQL esta ligado? O usuario e a senha estao certos?
    pause
    exit /b 1
)
for %%a in ("%ARQUIVO%") do echo Backup pronto: %%~fa  (%%~za bytes)
rem deu certo: a janela fecha sozinha depois de 3 segundos (com erro, ela espera uma tecla)
timeout /t 3 /nobreak >nul
exit /b 0
