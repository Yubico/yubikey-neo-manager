__requires__ = ['pyinstaller >= 2.1']

import os
import sys
import glob
import pkg_resources
from distutils import log
from distutils.core import Command
from shutil import copy2 as copy

NAME = "YubiKey NEO Manager"
LIB_LOCATION = "lib"


def is_win():
    return sys.platform in ['win32', 'cygwin']


def is_mac():
    return sys.platform in ['darwin']


class pyinstaller(Command):
    description = "create a binary distribution."
    user_options = []

    def initialize_options(self):
        self.opts = [
            '-n', NAME,
            '-w',
            os.path.join('scripts', 'neoman')
        ]

        if is_win():
            self.opts.extend([
                '-i', os.path.join('resources', 'neoman.ico')
            ])
        elif is_mac():
            self.opts.extend([
                '-i', os.path.join('resources', 'neoman.icns')
            ])

    def finalize_options(self):
        pass

    def copy_files(self):
        output_dir = 'dist/%s' % NAME
        if is_mac():
            output_dir = ".app/Contents/MacOS"

        copy('neoman/neoman.png', output_dir)

        if not os.path.isdir(LIB_LOCATION):
            raise Exception("./lib doesn't exist! Create it and place any "
                            "required libraries there.")

        if is_win():
            for filename in glob.glob(r'../*.dll'):
                copy(filename, output_dir)
        elif is_mac():
            for filename in glob.glob(r'../*.dylib'):
                copy(filename, output_dir)

    def run(self):
        self.distribution.fetch_build_eggs(__requires__)
        import PyInstaller.main
        PyInstaller.main.run(self.opts)

        self.copy_files()
        self.announce("Binary distribution created!")
