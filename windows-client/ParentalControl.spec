# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec cho Parental Control Client.

Build:
    pyinstaller ParentalControl.spec --noconfirm

Kết quả: dist/ParentalControl.exe - một file duy nhất, chạy độc lập, KHÔNG cần
cài Python trên máy đích.

Vì sao cần nhiều hidden import: pyrebase4 nạp các module con qua chuỗi
(oauth2client, gcloud, Crypto, requests_toolbelt...) mà PyInstaller không tự dò
ra được từ phân tích tĩnh. Thiếu bất kỳ cái nào thì .exe build xong vẫn crash
lúc chạy với "ModuleNotFoundError".
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# pyrebase và họ hàng
hidden = []
for pkg in (
    "pyrebase",
    "requests",
    "requests_toolbelt",
    "gcloud",
    "oauth2client",
    "Crypto",            # pycryptodome
    "jwt",               # python-jwt
    "google",
):
    hidden += collect_submodules(pkg)

# Một số module hay bị sót thêm
hidden += [
    "google.cloud",
    "google.auth",
    "pkg_resources.py2_warn",
    "engineio.async_drivers.threading",
]

# gcloud đóng gói vài file JSON (danh sách API) - phải kèm theo
datas = collect_data_files("gcloud")

block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Cắt bớt cho nhẹ - không dùng tới
        "tkinter",
        "matplotlib",
        "numpy",
        "PIL",
        "PySide2",
        "PySide6",
        "PyQt6",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="ParentalControl",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    # console=False -> chạy ngầm, không cửa sổ đen. Tương đương pythonw.exe.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="icon.ico",   # bỏ comment nếu có file icon
)
