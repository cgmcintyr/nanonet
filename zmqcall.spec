# -*- mode: python -*-
import os
import platform
import subprocess
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_submodules

block_cipher = None
system = platform.system()
pathex = ['.']
binaries = [('nanonet*.so', '.')]
datas = [('nanonet/data/*', 'nanonet/data')]
hiddenimports = []
excludedimports = []

def scrape_package(package):
    def decode(bytes_or_string):
        if isinstance(bytes_or_string, bytes):
            return bytes_or_string.decode()
        else:
            return bytes_or_string

    def is_binary(file):
        return file.endswith((
            '.so',
            '.pyd',
            '.dll',
        ))

    location_string = 'Location: '
    files_string = 'Files:'
    module_files = set()
    binary_files = set()

    in_header = True
    root = None
    for line in decode(subprocess.check_output(['pip', 'show', '-f', package])).splitlines():
        line = line.strip()
        if in_header and line.startswith(location_string):
            root = line[len(location_string):]
        if in_header and line.startswith(files_string):
            assert root is not None
            in_header = False
            continue
        elif not in_header:
            full_path = os.path.abspath(os.path.join(root, line.strip()))
            if line.endswith('.py') or line.endswith('.pyc'):
                module_files.add(full_path)
            if is_binary(line):
                print(line)
                binary_files.add(full_path)
    return list(binary_files)


if system == 'Darwin':
    # there is a hook for this h5py but seems not to work (on OSX at least)
    hiddenimports += [
        'h5py.{}'.format(x) for x in ['_proxy', 'utils', 'defs', 'h5ac']
    ]
    hiddenimports += ['zmq.utils.garbage'] + collect_submodules('zmq.backend')
    binaries += collect_dynamic_libs('zmq')
    excludedimports += ['zmq.libzmq']
elif system == 'Windows':
    hiddenimports += [
        'h5py.{}'.format(x) for x in ['_proxy', 'utils', 'defs', 'h5ac']
    ]
    hiddenimports += ['zmq.utils.garbage'] + collect_submodules('zmq.backend')
    pyzmq_gumph = [(x, '.') for x in scrape_package('pyzmq') if x.endswith('libzmq.pyd')]
    binaries = [('nanonet*.pyd', '.')] + collect_dynamic_libs('zmq') + pyzmq_gumph
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
