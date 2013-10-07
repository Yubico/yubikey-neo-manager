class Applet(object):

    def __init__(self, aid, name, description):
        self.aid = aid
        self.name = name
        self.description = description

    def __str__(self):
        return self.name


APPLETS = [
    Applet("a0000005272001", "YubiKey", "YubiKey OTP applet."),
    Applet("a0000005272101", "YubiOATH", "YubiOATH applet."),
    Applet("a0000005272102", "Yubico Bitcoin", "Yubico bitcoin applet."),
    Applet("d27600012401", "OpenPGP", "Open PGP applet.")
]

HIDDEN = [
    "a0000000035350"
]


def get_applets():
    return APPLETS


def get_applet(aid):
    if aid in HIDDEN:
        return None
    for applet in APPLETS:
        if applet.aid == aid:
            return applet
    return Applet(aid, "Unknown", "Unknown applet")
