"""
Strings for YubiKey NEO Manager
Note: Strings must not start with underscore (_).
"""

organization = "Yubico"
domain = "yubico.com"
app_name = "YubiKey NEO Manager"
win_title_1 = "YubiKey NEO Manager (%s)"
overview = "Overview"
hid = "HID"
ccid = "CCID"
hid_ccid = "HID+CCID"
ccid_touch_eject = "CCID with touch eject"
hid_ccid_touch_eject = "HID+CCID with touch eject"
requires_ccid = "Requires CCID mode"
settings = "Settings"
installed_apps = "Installed apps"
change_name = "Change name"
change_name_desc = "Change the name of the device."
manage_keys = "Manage transport keys"
key_required = "Transport key required"
key_required_desc = "Managing apps on this YubiKey NEO requires a password"
change_mode = "Change connection mode"
change_mode_1 = "Change connection mode [%s]"
change_mode_desc = ("Set the connection mode used by your YubiKey NEO.\nFor "
                    "this setting to take effect, you will need to unplug, "
                    "and re-attach your YubiKey.")
remove_device = "\nRemove your YubiKey NEO now.\n"
name = "Name"
name_1 = "Name: %s"
serial_1 = "Serial: %s"
firmware_1 = "Firmware version: %s"
aid_1 = "AID: %s"
status_1 = "Status: %s"
install = "Install"
installed = "Installed"
installing_1 = "Installing applet: %s"
not_installed = "Not installed"
uninstall = "Uninstall"
delete_app_confirm = "Delete applet?"
delete_app_desc = ("WARNING! Deleting an applet removes ALL associated data, "
                   "including credentials, and this data will NOT be "
                   "recoverable.")
deleting_1 = "Deleting applet: %s"
devices = "Devices"
apps = "NEO apps"


def _translate(qt):
    values = globals()
    for key, value in values.items():
        if isinstance(value, basestring) and not key.startswith('_'):
            values[key] = qt.tr(value)
