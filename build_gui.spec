import gooey
gooey_root = os.path.dirname(gooey.__file__)
gooey_languages = Tree(os.path.join(gooey_root, 'languages'), prefix = 'gooey/languages')
gooey_images = Tree(os.path.join(gooey_root, 'images'), prefix = 'gooey/images')

from PyInstaller.utils.hooks import copy_metadata

a = Analysis(['nanonet/nanonetgui.py'],
             pathex=['c:\\Python27\\Scripts'],
             hiddenimports=['pyopencl'],
             hookspath=None,
             runtime_hooks=None,
             binaries=[
                 ('nanonetdecode.*', '.'),
                 ('nanonetfilters.*', '.'),
             ],
             datas=[
                 ('nanonet/data/*', 'nanonet/data')
             ] + copy_metadata('pyopencl') 
             )
pyz = PYZ(a.pure)

options = [('u', None, 'OPTION'), ('u', None, 'OPTION'), ('u', None, 'OPTION')]

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          options,
          gooey_languages, # Add them in to collected files
          gooey_images, # Same here.
          name='nanonet',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          windowed=False,
          icon=os.path.join(gooey_root, 'images', 'program_icon.ico'))
