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

"""
Strings for YubiKey NEO Manager.

Note: String names must not start with underscore (_).

"""

organization = "Yubico"
domain = "yubico.com"
app_name = "YubiKey NEO Manager"
win_title_1 = "YubiKey NEO Manager (%s)"
ok = "OK"
cancel = "Cancel"
wait = "Please wait..."
welcome = "Welcome"
note_1 = "NOTE: %s"
overview = "Overview"
otp = "OTP"
ccid = "CCID"
otp_ccid = "OTP+CCID"
u2f = "U2F"
otp_u2f = "OTP+U2F"
u2f_ccid = "U2F+CCID"
otp_u2f_ccid = "OTP+U2F+CCID"
ccid_touch_eject = "CCID with touch eject"
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
mode_note = ("To be able to list/manage apps, your YubiKey NEO must have CCID "
             "enabled.")
name = "Name"
name_1 = "Name: %s"
serial_1 = "Serial: %s"
firmware_1 = "Firmware version: %s"
u2f_1 = "U2F/FIDO: %s"
u2f_supported = "supported"
u2f_not_supported_1 = "<a href=\"%s\">not supported</a>"
aid_1 = "AID: %s"
status_1 = "Status: %s"
version_1 = "Version: %s"
latest_version_1 = "Latest version: %s"
download = "Download"
downloading_file = "Downloading file..."
install = "Install"
installed = "Installed"
installed_1 = "%s installed"
installing = "Installing applet"
installing_1 = "Installing applet: %s"
error_installing = "Error installing applet"
error_installing_1 = "There was an error installing the applet: %s"
error_uninstalling = "Error uninstalling applet"
error_uninstalling_1 = "There was an error uninstalling the applet: %s"
error_downloading = "Error downloading applet"
error_downloading_1 = "There was an error downloading the applet: %s"
not_installed = "Not installed"
uninstall = "Uninstall"
delete_app_confirm = "Delete applet?"
delete_app_desc = ("WARNING! Deleting an applet removes ALL associated data, "
                   "including credentials, and this data will NOT be "
                   "recoverable.")
deleting_1 = "Deleting applet: %s"
install_cap = "Install applet from CAP file"
select_cap = "Select a CAP file"
devices = "Devices"
apps = "Available apps"
installed_apps = "Installed apps"
unknown = "Unknown"
unknown_applet = "Unknown applet"
about_1 = "About: %s"
libraries = "Library versions"
about_link_1 = "For help and discussion, see our <a href=\"%s\">forum</a>."
copyright = "Copyright &copy; 2014 Yubico"


def _translate(qt):
    values = globals()
    for key, value in values.items():
        if isinstance(value, basestring) and not key.startswith('_'):
            values[key] = qt.tr(value)
