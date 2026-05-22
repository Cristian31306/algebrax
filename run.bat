@echo off
title AlgebraX - Iniciar Proyecto
echo ==========================================
echo           INICIANDO ALGEBRAX
echo ==========================================
echo.

echo [1/2] Iniciando Backend (FastAPI) en una nueva ventana...
start "AlgebraX Backend" cmd /k "cd backend && venv\Scripts\activate && uvicorn main:app --reload"

echo [2/2] Iniciando Frontend (Vite + Vue) en una nueva ventana...
start "AlgebraX Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ==========================================
echo ¡Proceso de inicio completado con el script!
echo Se han abierto dos ventanas adicionales con los servidores.
echo ==========================================
pause
