@echo off
REM ============================================================
REM  run.bat — jalankan SELAMET cukup dengan DOUBLE KLIK.
REM  Taruh file ini SEJAJAR dengan app.py (di dalam folder SELAMET).
REM ============================================================

cd /d "%~dp0"

echo ============================================
echo   SELAMET - Dashboard Peternakan Lebah Pintar
echo ============================================
echo.

REM Buat virtual environment kalau belum ada (hanya sekali, otomatis)
if not exist venv (
    echo [1/3] Menyiapkan environment Python pertama kali...
    python -m venv venv
)

echo [2/3] Mengaktifkan environment...
call venv\Scripts\activate.bat

echo [3/3] Memastikan semua library terpasang...
pip install -r requirements.txt --quiet --disable-pip-version-check

echo.
echo ============================================
echo   Server berjalan di: http://localhost:5000
echo   Biarkan window ini TERBUKA selama pakai web.
echo   Tutup window ini untuk mematikan server.
echo ============================================
echo.

python app.py

pause
