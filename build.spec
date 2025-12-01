# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        # Добавьте другие файлы здесь
        # ('assets/*', 'assets'),
    ],
    hiddenimports=[
        'tkinter',
        'pynput.keyboard',
        'pynput.mouse',
        'pyautogui',
        'PIL',
        'PIL._tkinter_finder',
        'pytesseract',
        'cv2',
        'numpy',
        'keyboard',
        'json',
        'threading',
        'time',
        'random',
        'os',
        'sys',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PoE_Craft_Bot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Сжатие - установите UPX отдельно
    console=False,  # False для GUI приложений
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)