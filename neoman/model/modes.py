from neoman import messages as m


class Modes(object):
    # OTP, CCID, U2F
    MODE_CODES = {
        (True, False, False): 0x00,
        (False, True, False): 0x01,
        (True, True, False): 0x02,
        (False, False, True): 0x03,
        (True, False, True): 0x04,
        (False, True, True): 0x05,
        (True, True, True): 0x06
    }

    TOUCH_EJECT_FLAG = 0x80

    MODE_NAMES = [
        m.otp,
        m.ccid,
        m.otp_ccid,
        m.u2f,
        m.otp_u2f,
        m.u2f_ccid,
        m.otp_u2f_ccid
    ]

    def name_for_mode(self, mode):
        return self.MODE_NAMES[mode & ~self.TOUCH_EJECT_FLAG]

    def mode_for_flags(self, otp, ccid, u2f, touch_eject=False):
        mode = self.MODE_CODES[(otp, ccid, u2f)]
        if touch_eject:
            mode |= self.TOUCH_EJECT_FLAG
        return mode

    def flags_for_mode(self, mode):
        touch_eject = mode & self.TOUCH_EJECT_FLAG != 0
        mode &= ~self.TOUCH_EJECT_FLAG
        for (otp, ccid, u2f), code in self.MODE_CODES.items():
            if code == mode:
                return otp, ccid, u2f, touch_eject


MODE = Modes()
