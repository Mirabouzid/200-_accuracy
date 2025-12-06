@echo off
echo ============================================================
echo    REDEMARRAGE DU BACKEND - BlockStat Pro
echo ============================================================
echo.

cd backend

echo [1/3] Verification du fichier .env...
if exist .env (
    echo     ✓ Fichier .env trouve
) else (
    echo     ✗ ERREUR: Fichier .env manquant!
    echo.
    echo     Creation du fichier .env...
    echo PORT=5000 > .env
    echo NODE_ENV=development >> .env
    echo GRAPH_AGENT_URL=http://localhost:8000 >> .env
   echo GROQ_API_KEY=%GROQ_API_KEY% >> .env
    echo     ✓ Fichier .env cree
)
echo.

echo [2/3] Installation des dependances...
call npm install
echo.

echo [3/3] Demarrage du backend...
echo.
echo ============================================================
echo    Backend demarre sur http://localhost:5000
echo    Appuyez sur Ctrl+C pour arreter
echo ============================================================
echo.

call npm run dev

pause
