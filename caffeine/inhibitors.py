# Copyright (c) 2015 Hugo Osvaldo Barrera <hugo@barrera.io>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Note: This code is part libcaffeine, though it's been moved in-tree (rather
# than handled as a proper dependency) because libcaffeine isn't really stable
# enough for public release.

import dbus
import logging
import os
import time

logger = logging.getLogger(__name__)

INHIBITION_REASON = "Inhibited via libcaffeine"


class BaseInhibitor:

    def __init__(self):
        self.__running = False

    # XXX: Do we need `running` to be a property, rather than an attribute?
    def get_running(self):
        return self.__running

    def set_running(self, running):
        self.__running = running

    running = property(get_running, set_running)

    def toggle(self):
        if not self.running:
            self.inhibit()
        else:
            self.uninhibit()


class GnomeInhibitor(BaseInhibitor):

    def __init__(self):
        BaseInhibitor.__init__(self)
        self.bus = dbus.SessionBus()

    def inhibit(self):
        if not self.__proxy:
            self.__proxy = self.bus.get_object('org.gnome.SessionManager',
                                               '/org/gnome/SessionManager')

        self.__cookie = self.__proxy.Inhibit("Caffeine", dbus.UInt32(0),
                                             INHIBITION_REASON,
                                             dbus.UInt32(8))
        self.running = True

    def uninhibit(self):
        if self.__cookie is not None:
            self.__proxy.Uninhibit(self.__cookie)
        self.running = False

    @property
    def applicable(self):
        return 'org.gnome.SessionManager' in self.bus.list_names()


class XdgScreenSaverInhibitor(BaseInhibitor):

    def __init__(self):
        BaseInhibitor.__init__(self)
        self.bus = dbus.SessionBus()

    def inhibit(self):
        self.__proxy_ss = \
            self.bus.get_object('org.freedesktop.ScreenSaver', '/ScreenSaver')
        self.__cookie_ss = \
            self.__proxy_ss.Inhibit("Caffeine", INHIBITION_REASON)

        self.running = True

    def uninhibit(self):
        if self.__cookie_ss is not None:
            self.__proxy_ss.UnInhibit(self.__cookie_ss)
        self.running = False

    @property
    def applicable(self):
        return 'org.freedesktop.ScreenSaver' in self.bus.list_names()


class XdgPowerManagmentInhibitor(BaseInhibitor):

    def __init__(self):
        BaseInhibitor.__init__(self)
        self.bus = dbus.SessionBus()

    def inhibit(self):
        self.__proxy_pm = \
            self.bus.get_object('org.freedesktop.PowerManagement.Inhibit',
                                '/org/freedesktop/PowerManagement/Inhibit')
        self.__cookie_pm = \
            self.__proxy_pm.Inhibit("Caffeine", INHIBITION_REASON)
        self.running = True

    def uninhibit(self):
        if self.__cookie_pm is not None:
            self.__proxy_pm.UnInhibit(self.__cookie_pm)
        self.running = False

    @property
    def applicable(self):
        return 'org.freedesktop.PowerManagement.Inhibit' in \
            self.bus.list_names()


class XssInhibitor(BaseInhibitor):

    def __init__(self):
        BaseInhibitor.__init__(self)

    def inhibit(self):
        self.running = True

        while self.running:
            os.system("xscreensaver-command -deactivate")
            time.sleep(50)

    def uninhibit(self):
        self.running = False

    @property
    def applicable(self):
        # TODO!
        return os.system("pgrep xscreensaver") is 0


class DpmsInhibitor(BaseInhibitor):

    def __init__(self):
        BaseInhibitor.__init__(self)

    def inhibit(self):
        self.running = True

        os.system("xset -dpms")

    def uninhibit(self):
        self.running = False

        # FIXME: Aren't we enabling it if it was never online?
        # Grep `xset q` for "DPMS is Enabled"
        os.system("xset +dpms")

    @property
    def applicable(self):
        # TODO!
        return True


class XorgInhibitor(BaseInhibitor):

    def __init__(self):
        BaseInhibitor.__init__(self)

    def inhibit(self):
        self.running = True

        os.system("xset s off")

    def uninhibit(self):
        self.running = False

        # FIXME: Aren't we enabling it if it was never online?
        # Scrensaver.*\n\s+timeout:  600
        os.system("xset s on")

    @property
    def applicable(self):
        # TODO!
        return True
