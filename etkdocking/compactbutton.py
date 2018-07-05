# Copyright © 2010 etkdocking Contributors
#
# This file is part of etkdocking.
#
# etkdocking is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# etkdocking is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with etkdocking. If not, see <http://www.gnu.org/licenses/>.


from __future__ import absolute_import

from builtins import hex
from logging import getLogger

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

from .util import load_icon


class CompactButton(Gtk.Widget):
    __gtype_name__ = "EtkCompactButton"
    __gsignals__ = {
        "clicked": (
            GObject.SignalFlags.RUN_FIRST | GObject.SignalFlags.ACTION,
            None,
            tuple(),
        )
    }
    __gproperties__ = {
        "icon-name-normal": (
            GObject.TYPE_STRING,
            "icon name normal",
            "icon name normal",
            "",
            GObject.PARAM_READWRITE,
        ),
        "icon-name-prelight": (
            GObject.TYPE_STRING,
            "icon name prelight",
            "icon name prelight",
            "",
            GObject.PARAM_READWRITE,
        ),
        "icon-name-active": (
            GObject.TYPE_STRING,
            "icon name active",
            "icon name active",
            "",
            GObject.PARAM_READWRITE,
        ),
        "size": (
            GObject.TYPE_UINT,
            "size",
            "size",
            0,
            GObject.G_MAXUINT,
            16,
            GObject.PARAM_READWRITE,
        ),
        "has-frame": (
            GObject.TYPE_BOOLEAN,
            "has frame",
            "has frame",
            True,
            GObject.PARAM_READWRITE,
        ),
    }

    def __init__(self, icon_name_normal="", size=16, has_frame=True):
        GObject.GObject.__init__(self)
        # TODO this is pyGTK specific, and no equivalent in PyGi. Does it need to be GInitiallyUnowned?
        # self.set_flags(self.flags() | Gtk.NO_WINDOW)

        # Initialize logging
        self.log = getLogger("%s.%s" % (self.__gtype_name__, hex(id(self))))

        # Internal housekeeping
        self._entered = False
        self._icon_normal = None
        self._icon_prelight = None
        self._icon_active = None
        self.set_size(size)
        self.set_has_frame(has_frame)
        self.set_icon_name_normal(icon_name_normal)

    ############################################################################
    # Convenience
    ############################################################################
    def _refresh_icons(self):
        self._icon_normal = load_icon(self._icon_name_normal, self._size)

        if self._icon_name_prelight == self._icon_name_normal:
            self._icon_prelight = self._icon_normal
        else:
            self._icon_prelight = load_icon(self._icon_name_prelight, self._size)

        if self._icon_name_active == self._icon_name_prelight:
            self._icon_active = self._icon_prelight
        else:
            self._icon_active = load_icon(self._icon_name_active, self._size)

    ############################################################################
    # GObject
    ############################################################################
    def do_get_property(self, pspec):
        if pspec.name == "icon-name-normal":
            return self.get_icon_name_normal()
        elif pspec.name == "icon-name-prelight":
            return self.get_icon_name_prelight()
        elif pspec.name == "icon-name-active":
            return self.get_icon_name_active()
        elif pspec.name == "size":
            return self.get_size()
        elif pspec.name == "has-frame":
            return self.get_has_frame()

    def do_set_property(self, pspec, value):
        if pspec.name == "icon-name-normal":
            self.set_icon_name_normal(value)
        elif pspec.name == "icon-name-prelight":
            self.set_icon_name_prelight(value)
        elif pspec.name == "icon-name-active":
            self.set_icon_name_active(value)
        elif pspec.name == "size":
            self.set_size(value)
        elif pspec.name == "has-frame":
            self.set_has_frame(value)

    def get_icon_name_normal(self):
        return self._icon_name_normal

    def set_icon_name_normal(self, value):
        self._icon_name_normal = value
        self._icon_name_prelight = value
        self._icon_name_active = value

        if self.get_realized():
            self._refresh_icons()
            self.queue_resize()

    def get_icon_name_prelight(self):
        return self._icon_name_prelight

    def set_icon_name_prelight(self, value):
        self._icon_name_prelight = value
        self._icon_name_active = value

        if self.get_realized():
            self._refresh_icons()
            self.queue_resize()

    def get_icon_name_active(self):
        return self._icon_name_active

    def set_icon_name_active(self, value):
        self._icon_name_active = value

        if self.get_realized():
            self._refresh_icons()
            self.queue_resize()

    def get_size(self):
        return self._size

    def set_size(self, value):
        self._size = value

    def get_has_frame(self):
        return self._has_frame

    def set_has_frame(self, value):
        self._has_frame = value

    ############################################################################
    # GtkWidget
    ############################################################################
    def do_realize(self):
        Gtk.Widget.do_realize(self)
        self._input_window = Gdk.Window(
            self.get_parent_window(),
            x=self.allocation.x,
            y=self.allocation.y,
            width=self.allocation.width,
            height=self.allocation.height,
            window_type=Gdk.WINDOW_CHILD,
            wclass=Gdk.INPUT_ONLY,
            visual=self.get_visual(),
            colormap=self.get_colormap(),
            event_mask=(
                Gdk.EventMask.ENTER_NOTIFY_MASK
                | Gdk.EventMask.LEAVE_NOTIFY_MASK
                | Gdk.EventMask.BUTTON_PRESS_MASK
                | Gdk.EventMask.BUTTON_RELEASE_MASK
            ),
        )
        self._input_window.set_user_data(self)
        self._refresh_icons()

    def do_unrealize(self):
        self._input_window.set_user_data(None)
        self._input_window.destroy()
        Gtk.Widget.do_unrealize(self)

    def do_map(self):
        self._input_window.show()
        Gtk.Widget.do_map(self)

    def do_unmap(self):
        self._input_window.hide()
        Gtk.Widget.do_unmap(self)

    def do_size_request(self, requisition):
        requisition.width = self._size
        requisition.height = self._size

    def do_size_allocate(self, allocation):
        self.allocation = allocation

        if self.get_realized():
            self._input_window.move_resize(*self.allocation)

    def do_expose_event(self, event):
        # Draw icon
        if self.state == Gtk.StateType.NORMAL:
            pixbuf = self._icon_normal
            x = self.allocation.x
            y = self.allocation.y
        elif self.state == Gtk.StateType.PRELIGHT:
            pixbuf = self._icon_prelight
            x = self.allocation.x
            y = self.allocation.y
        elif self.state == Gtk.StateType.ACTIVE:
            pixbuf = self._icon_active
            x = self.allocation.x + 1
            y = self.allocation.y + 1

        event.window.draw_pixbuf(self.style.base_gc[self.state], pixbuf, 0, 0, x, y)

        # Draw frame
        if self._has_frame and self.state != Gtk.StateType.NORMAL:
            event.window.draw_rectangle(
                self.style.dark_gc[self.state],
                False,
                self.allocation.x,
                self.allocation.y,
                self.allocation.width - 1,
                self.allocation.height - 1,
            )

        return False

    def do_enter_notify_event(self, event):
        self._entered = True
        self.set_state(Gtk.StateType.PRELIGHT)
        self.queue_draw()
        return True

    def do_leave_notify_event(self, event):
        self._entered = False
        self.set_state(Gtk.StateType.NORMAL)
        self.queue_draw()
        return True

    def do_button_press_event(self, event):
        if event.button == 1:
            self.set_state(Gtk.StateType.ACTIVE)
            self.queue_draw()

        return True

    def do_button_release_event(self, event):
        if event.button == 1 and self._entered == True:
            self.set_state(Gtk.StateType.PRELIGHT)
            self.emit("clicked")
            self.queue_draw()

        return True
