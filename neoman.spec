# -*- mode: python -*-
import os
import sys
from shutil import copy2 as copy

NAME = "YubiKey NEO Manager"

WIN = sys.platform in ['win32', 'cygwin']
OSX = sys.platform in ['darwin']

ICON = os.path.join('neoman', 'neoman.png')
if WIN:
    ICON = os.path.join('resources', 'neoman.ico')

elif OSX:
    ICON = os.path.join('resources', 'neoman.icns')

a = Analysis(['scripts/neoman'],
             pathex=[''],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='%s.exe' % NAME,
          debug=False,
          strip=None,
          upx=True,
          console=False , icon=ICON)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=None,
               upx=True,
               name=NAME)

output_dir = os.path.join(DISTPATH, NAME)
if OSX:
    output_dir += '.app/Content/MacOS/'
else:
    output_dir += os.path.sep

copy('neoman/neoman.png', output_dir)
    
if WIN:
    for filename in glob.glob(r'lib/*.dll'):
        copy(filename, output_dir)
elif MAC:
    for filename in glob.glob(r'lib/*.dylib'):
        copy(filename, output_dir)
