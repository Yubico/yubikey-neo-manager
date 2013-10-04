class Applet(object):

    def __init__(self, aid, name, description):
        self.aid = aid
        self.name = name
        self.description = description

    def __str__(self):
        return self.name


APPLETS = [
    Applet("a0000005272001", "YubiKey", "YubiKey OTP"),
    Applet("a0000005272101", "YubiOATH", "YubiOATH applet.")
]


def get_applets():
    return APPLETS


def get_applet(aid):
    for applet in APPLETS:
        if applet.aid == aid:
            return applet
    return Applet(aid, "Unknown", "Unknown applet")
