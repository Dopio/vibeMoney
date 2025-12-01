@echo off
chcp 65001 >nul
title Сборка PoE Craft Bot

echo 📦 Подготовка к сборке PoE Craft Bot...
echo.

:: Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден! Установите Python и добавьте в PATH.
    pause
    exit /b 1
)

:: Проверка PyInstaller
python -c "import pyinstaller" 2>nul
if errorlevel 1 (
    echo ❌ PyInstaller не установлен!
    echo Устанавливаем PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Не удалось установить PyInstaller!
        pause
        exit /b 1
    )
)

:: Проверка основных файлов
if not exist "main.py" (
    echo ❌ Файл main.py не найден!
    pause
    exit /b 1
)

if not exist "config.json" (
    echo ⚠️ Файл config.json не найден, создаем пустой...
    echo {} > config.json
)

:: Запуск сборки
echo 🚀 Запуск сборки...
python build.py

echo.
echo 🔍 Проверка результата...
if exist "dist\PoE_Craft_Bot.exe" (
    echo ✅ Сборка успешно завершена!
    echo 📁 Файл: dist\PoE_Craft_Bot.exe
    echo.
    echo 🎯 Размер файла:
    for %%F in ("dist\PoE_Craft_Bot.exe") do echo    %%~zF байт
) else (
    echo ❌ Сборка не удалась!
)

echo.
pause
