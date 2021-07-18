# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['monitor_liquidity.py'],
             pathex=['C:\\Users\\BOLDMAN\\Dev\\bama\\bamatool'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['matplotlib', 'scipy', 'setuptools', 'hook', 'distutils', 'site', 'hooks', 'tornado', 'PIL', 'PyQt4', 'PyQt5', 'pydoc', 'pythoncom', 'pytz', 'pywintypes', 'sqlite3', 'pyz', 'pandas', 'sklearn', 'scapy', 'scrapy', 'numpy', 'sympy', 'kivy', 'pyramid', 'opencv', 'tensorflow', 'pipenv', 'pattern', 'mechanize', 'beautifulsoup4', 'requests', 'wxPython', 'pygi', 'pillow', 'pygame', 'pyglet', 'flask', 'django', 'pylint', 'pytube', 'odfpy', 'mccabe', 'pilkit', 'six', 'wrapt', 'astroid', 'isort'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='monitor_liquidity',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
