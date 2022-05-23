# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
  ['espresso.py'],
  pathex=[],
  binaries=[],
  datas=[
    ("./venv/Lib/site-packages/eunjeon/", "./eunjeon"),
    ("./images/", "./images"),
  ],
  hiddenimports=[],
  hookspath=[],
  hooksconfig={},
  runtime_hooks=[],
  excludes=[],
  win_no_prefer_redirects=False,
  win_private_assemblies=False,
  cipher=block_cipher,
  noarchive=False
)

pyz = PYZ(
  a.pure,
  a.zipped_data,
  cipher=block_cipher
)

# avoid warning
for d in a.datas:
  if '_MeCab.cp310-win_amd64.pyd' in d[0]:
    a.datas.remove(d)
    break

exe = EXE(
  pyz,
  a.scripts,
  a.binaries,
  a.zipfiles,
  a.datas,  
  [],
  name='Espresso_1_1_5.exe',
  debug=False,
  bootloader_ignore_signals=False,
  strip=False,
  upx=True,
  upx_exclude=[],
  runtime_tmpdir=None,
  console=False,
  disable_windowed_traceback=False,
  target_arch=None,
  codesign_identity=None,
  entitlements_file=None,
  icon='./images/Espresso.ico',
  version='./version.rc'
)
