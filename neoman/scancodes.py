mapping = {
    '!': '\x9e',
    '@': '\x9f',
    '#': '\xa0',
    '$': '\xa1',
    '%': '\xa2',
    '^': '\xa3',
    '&': '\xa4',
    '*': '\xa5',
    '(': '\xa6',
    ')': '\xa7',
    '_': '\xad',
    ':': '\xb3',
    '"': '\xb4',
    '~': '\xb5',
    '|': '\xb2',
    '<': '\xb6',
    '>': '\xb7',
    '?': '\xb8',
    '1': '\x1e',
    '2': '\x1f',
    '3': '\x20',
    '4': '\x21',
    '5': '\x22',
    '6': '\x23',
    '7': '\x24',
    '8': '\x25',
    '9': '\x26',
    '0': '\x27',
    '-': '\x2d',
    '=': '\x2e',
    ';': '\x33',
    "'": '\x34',
    '\\': '\x32',
    ',': '\x36',
    '.': '\x37',
    '/': '\x38',
}


def _to_scancode(c):
    if c.islower():
        return chr(ord(c) - 93)
    if c.isupper():
        return chr(ord(c) + 67)
    return mapping[c]


def to_scancodes(str):
    return ''.join([_to_scancode(c) for c in str])