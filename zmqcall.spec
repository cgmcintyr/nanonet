# -*- mode: python -*-
import platform
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

block_cipher = None
system = platform.system()
binaries = [('nanonet*.so', '.')]
datas = [('nanonet/data/*', 'nanonet/data')]
hiddenimports = []
excludedimports = []

if system == 'Darwin':
    # there is a hook for this h5py but seems not to work (on OSX at least)
    hiddenimports += [
        'h5py.{}'.format(x) for x in ['_proxy', 'utils', 'defs', 'h5ac']
    ]
    hiddenimports += ['zmq.utils.garbage'] + collect_submodules('zmq.backend')
    binaries += collect_dynamic_libs('zmq')
    excludedimports += ['zmq.libzmq']

a = Analysis(['nanonet/zmq_server.py'],
             pathex=['.'],
             binaries=binaries,
             datas=datas,
             hiddenimports=hiddenimports,
             #excludedimports=excludedimports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='zmqcall',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='zmqcall')
