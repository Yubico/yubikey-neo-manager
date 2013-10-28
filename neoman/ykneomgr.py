from ctypes import (Structure, POINTER,
                    c_int, c_uint, c_uint8, c_char_p, c_size_t)
from neoman.libloader import load_library

_lib = load_library('ykneomgr')


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
