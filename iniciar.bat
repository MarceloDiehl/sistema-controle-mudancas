@echo off
rem Inicia o Controle de Demandas de Mudancas. Enquanto esta janela estiver aberta, o sistema fica no ar.
rem Para parar: feche a janela ou aperte Ctrl+C.
rem Deixe este arquivo na mesma pasta do controle-mudancas-1.0.0.jar.
rem (Arquivo sem acentos de proposito: o cmd do Windows le errado um .bat acentuado depois do chcp 65001.)
chcp 65001 >nul
title Controle de Demandas de Mudancas
cd /d "%~dp0"

rem ---------------------------------------------------------------- ajustes
rem Senha inicial do coordenador "admin": so vale na primeira vez, quando o admin ainda nao existe no banco
rem (no primeiro acesso ele cria a senha pessoal). Preencha so na copia que vai para a maquina; NUNCA no Git.
set "SENHA_INICIAL_ADMIN="
rem Porta do site (http://localhost:PORTA)
set "PORTA=8088"
rem Banco (MySQL desta maquina, porta 3306). Senha em branco quando o usuario nao tem senha.
rem Preencha a senha so na copia da maquina; NUNCA no Git.
set "USUARIO_BANCO=ditic_admin"
set "SENHA_BANCO="
rem ------------------------------------------------------------------------

where java >nul 2>nul
if errorlevel 1 (
    echo Java nao encontrado. Instale o Java 17 ou mais novo e abra este arquivo de novo.
    pause
    exit /b 1
)

set "JAR="
for %%f in (controle-mudancas-*.jar) do set "JAR=%%f"
if not defined JAR (
    echo Nao achei o controle-mudancas-*.jar nesta pasta: %CD%
    pause
    exit /b 1
)

if defined SENHA_INICIAL_ADMIN set "MUDANCAS_ADMIN_SENHA=%SENHA_INICIAL_ADMIN%"
set "DB_USER=%USUARIO_BANCO%"
set "DB_PASSWORD=%SENHA_BANCO%"

echo Iniciando o sistema (%JAR%)...
echo Quando aparecer "Started ControleMudancasApplication", o site estara em http://localhost:%PORTA%
echo Para parar, feche esta janela.
echo.

rem abre o navegador sozinho depois de alguns segundos
start "" /b cmd /c "timeout /t 15 /nobreak >nul & start "" http://localhost:%PORTA%"

java -Dfile.encoding=UTF-8 -Dstdout.encoding=UTF-8 -Dstderr.encoding=UTF-8 -jar "%JAR%" --server.port=%PORTA%

echo.
echo O sistema parou. Se foi um erro, veja as mensagens acima.
pause
