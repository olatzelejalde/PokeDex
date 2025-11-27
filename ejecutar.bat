@echo off
echo ===============================
echo    POKEDEX - ABIAZTAPENA
echo ===============================
echo.

echo 1. Backend-a martxan jartzen...
start cmd /k "cd backend && echo [BACKEND] Karpeta: %CD%\backend && python -c "import sys; print('Python bertsioa:', sys.version)" && venv\Scripts\activate && python app.py"

echo.
echo 2. Itxaron 5 segundo backend-a abiarazteko...
timeout /t 5

echo.
echo 3. Frontend-a martxan jartzen...
start cmd /k "cd frontend && echo [FRONTEND] Karpeta: %CD%\frontend && python -m http.server 8000"

echo.
echo 4. Itxaron 3 segundo...
timeout /t 3

echo.
echo ✅ ABIARAZTEA BUKATUTA
echo.
echo 📍 Backend:  http://localhost:5000
echo 📍 Frontend: http://localhost:8000
echo.
echo 🎮 Jarraibideak:
echo    1. Egiaztatu backend-a funtzionatzen ari dela: http://localhost:5000/api/pokemon
echo    2. Ireki frontend-a: http://localhost:8000
echo    3. Egiaztatu konsolako erroreak (F12)
echo.

pause