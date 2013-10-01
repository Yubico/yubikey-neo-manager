from ctypes import Structure, POINTER, c_int, c_uint8, c_uint
from neoman.libloader import load_library

try:
    _lib = load_library('ykpers-1')
except ImportError:
    _lib = load_library('ykpers-1-1')


def define(name, args, res):
    fn = getattr(_lib, name)
    fn.argtypes = args
    fn.restype = res
    return fn


YK_KEY = type('YK_KEY', (Structure,), {})
YK_STATUS = type('YK_STATUS', (Structure,), {})
YK_TICKET = type('YK_TICKET', (Structure,), {})
YK_CONFIG = type('YK_CONFIG', (Structure,), {})
YK_NAV = type('YK_NAV', (Structure,), {})
YK_FRAME = type('YK_FRAME', (Structure,), {})
YK_NDEF = type('YK_NDEF', (Structure,), {})
YK_DEVICE_CONFIG = type('YK_DEVICE_CONFIG', (Structure,), {})

yk_init = define('yk_init', [], c_int)
yk_release = define('yk_release', [], c_int)

yk_open_first_key = define('yk_open_first_key', [], POINTER(YK_KEY))
yk_close_key = define('yk_close_key', [POINTER(YK_KEY)], c_int)

ykds_alloc = define('ykds_alloc', [], POINTER(YK_STATUS))
ykds_free = define('ykds_free', [POINTER(YK_STATUS)], None)
ykds_version_major = define('ykds_version_major', [POINTER(YK_STATUS)], c_int)
ykds_version_minor = define('ykds_version_minor', [POINTER(YK_STATUS)], c_int)
ykds_version_build = define('ykds_version_build', [POINTER(YK_STATUS)], c_int)

yk_get_status = define('yk_get_status', [
    POINTER(YK_KEY), POINTER(YK_STATUS)], c_int)
yk_get_serial = define('yk_get_serial', [
    POINTER(YK_KEY), c_uint8, c_uint, POINTER(c_uint)], c_int)


__all__ = [x for x in globals().keys() if x.lower().startswith('yk')]
