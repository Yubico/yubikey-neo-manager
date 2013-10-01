from ctypes import Structure, POINTER, c_uint, c_char_p
from neoman.libloader import load_library

_lib = load_library('ykneomgr')


ykneomgr_rc = c_uint
ykneomgr_initflags = c_uint


def define(name, args, res):
    fn = getattr(_lib, name)
    fn.argtypes = args
    fn.restype = res
    return fn


ykneomgr_dev = type('ykneomgr_dev', (Structure,), {})

ykneomgr_global_init = define('ykneomgr_global_init', [ykneomgr_initflags],
                              ykneomgr_rc)
ykneomgr_dev_discover = define('ykneomgr_dev_discover',
                               [POINTER(POINTER(ykneomgr_dev))], ykneomgr_rc)
ykneomgr_dev_secure = define('ykneomgr_dev_secure', [POINTER(ykneomgr_dev)],
                             ykneomgr_rc)
ykneomgr_dev_listapps = define('ykneomgr_dev_listapps',
                               [POINTER(ykneomgr_dev), POINTER(c_char_p)],
                               ykneomgr_rc)
ykneomgr_dev_done = define('ykneomgr_dev_done',
                           [POINTER(ykneomgr_dev)], ykneomgr_rc)

__all__ = [x for x in globals().keys() if x.lower().startswith('ykneomgr')]
