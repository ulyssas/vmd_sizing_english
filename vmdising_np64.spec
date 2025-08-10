# -*- coding: utf-8 -*-
# -*- mode: python -*-
# VMDサイジング 64bit版

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# jaraco.text のデータファイルを追加
datas = collect_data_files('jaraco.text')

a = Analysis(['src\\executor.py'],
             pathex=[],
             binaries=[],
             datas=datas,
             hiddenimports=['pkg_resources', 'wx._adv', 'wx._html', 'bezier', 'quaternion', 'module.MParams', 'importlib_resources._adapters'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['mkl','libopenblas', 'tkinter', 'win32comgenpy', 'traitlets', 'PIL', 'IPython', 'pydoc', 'lib2to3', 'pygments', 'matplotlib'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
a.datas += [('.\\src\\vmdsizing.ico','.\\src\\vmdsizing.ico', 'DATA')]
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='VmdSizing_5.01.08_64bit',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=False,
          icon='.\\src\\vmdsizing.ico')

