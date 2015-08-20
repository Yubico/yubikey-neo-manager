# Copyright (c) 2013 Yubico AB
# All rights reserved.
#
#   Redistribution and use in source and binary forms, with or
#   without modification, are permitted provided that the following
#   conditions are met:
#
#    1. Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#    2. Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
from neoman.yubicommon.setup.exe import executable
from neoman.yubicommon.setup.qt import qt_resources
from neoman.yubicommon.setup import setup


setup(
    name='yubikey-neo-manager',
    long_name='YubiKey NEO Manager',
    author='Dain Nilsson',
    author_email='dain@yubico.com',
    maintainer='Yubico Open Source Maintainers',
    maintainer_email='ossmaint@yubico.com',
    url='https://github.com/Yubico/yubikey-neo-manager',
    description='Tool for managing your YubiKey NEO configuration.',
    long_description='This is the long description',
    license='BSD 2 clause',
    package_data={'neoman': ['appletdb.json', 'js_api.js']},
    entry_points={
        'gui_scripts': ['neoman=neoman.__main__:main']
    },
    install_requires=['PySide', 'pycrypto'],
    yc_requires=['ctypes', 'qt'],
    cmdclass={'executable': executable, 'qt_resources': qt_resources('neoman')},
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Security :: Cryptography',
        'Topic :: Utilities'
    ]
)
