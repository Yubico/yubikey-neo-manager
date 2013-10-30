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
from ctypes import (Structure, POINTER,
                    c_int, c_uint, c_uint8, c_char_p, c_size_t)
from neoman.libloader import load_library

_lib = load_library('ykneomgr', '0')


ykneomgr_rc = c_int
ykneomgr_initflags = c_uint


def define(name, args, res=None):
    fn = getattr(_lib, name)
    fn.argtypes = args
    fn.restype = res
    return fn


ykneomgr_dev = type('ykneomgr_dev', (Structure,), {})

ykneomgr_global_init = define('ykneomgr_global_init', [ykneomgr_initflags],
                              ykneomgr_rc)
ykneomgr_init = define('ykneomgr_init', [
                       POINTER(POINTER(ykneomgr_dev))], ykneomgr_rc)
ykneomgr_done = define('ykneomgr_done', [POINTER(ykneomgr_dev)])
ykneomgr_discover = define('ykneomgr_discover', [POINTER(ykneomgr_dev)],
                           ykneomgr_rc)
ykneomgr_authenticate = define('ykneomgr_authenticate',
                               [POINTER(ykneomgr_dev), c_char_p],
                               ykneomgr_rc)
ykneomgr_modeswitch = define('ykneomgr_modeswitch',
                             [POINTER(ykneomgr_dev), c_uint8], ykneomgr_rc)
ykneomgr_applet_list = define('ykneomgr_applet_list',
                              [POINTER(ykneomgr_dev), c_char_p,
                               POINTER(c_size_t)],
                              ykneomgr_rc)
ykneomgr_applet_delete = define('ykneomgr_applet_delete',
                                [POINTER(ykneomgr_dev), c_char_p, c_size_t],
                                ykneomgr_rc)
ykneomgr_applet_install = define('ykneomgr_applet_install',
                                 [POINTER(ykneomgr_dev), c_char_p],
                                 ykneomgr_rc)

ykneomgr_get_serialno = define('ykneomgr_get_serialno',
                               [POINTER(ykneomgr_dev)], c_uint)
ykneomgr_get_mode = define('ykneomgr_get_mode', [POINTER(ykneomgr_dev)],
                           c_uint8)
ykneomgr_get_version_major = define('ykneomgr_get_version_major',
                                    [POINTER(ykneomgr_dev)], c_uint8)
ykneomgr_get_version_minor = define('ykneomgr_get_version_minor',
                                    [POINTER(ykneomgr_dev)], c_uint8)
ykneomgr_get_version_build = define('ykneomgr_get_version_build',
                                    [POINTER(ykneomgr_dev)], c_uint8)

__all__ = [x for x in globals().keys() if x.lower().startswith('ykneomgr')]
