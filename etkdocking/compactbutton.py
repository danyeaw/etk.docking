# -*- coding: utf-8 -*-
# vim:sw=4:et:ai

# Copyright © 2010 etk.docking Contributors
#
# This file is part of etk.docking.
#
# etk.docking is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# etk.docking is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with etk.docking. If not, see <http://www.gnu.org/licenses/>.


from __future__ import absolute_import
from builtins import hex
from logging import getLogger

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib

from .util import load_icon


class CompactButton(Gtk.Widget):
    """Compact minimize, maximize, list, close, and restore button Widget.

    A button widget to add compact buttons to the tabs of a DockGroup.

    To use:
    >>> min_button = CompactButton('compact-minimize')
    >>> def on_min_button_clicked():
    >>>     pass
    >>> min_button.connect('clicked', on_min_button_clicked)

    """
    __gtype_name__ = 'EtkCompactButton'
    __gsignals__ = {'clicked':
                        (GObject.SignalFlags.RUN_FIRST | GObject.SignalFlags.ACTION,
                         None,
                         tuple())}
    __gproperties__ = {'icon-name-normal':
                           (GObject.TYPE_STRING,
                            'icon name normal',
                            'icon name normal',
                            '',
                            GObject.ParamFlags.READWRITE),
                       'icon-name-prelight':
                           (GObject.TYPE_STRING,
                            'icon name prelight',
                            'icon name prelight',
                            '',
                            GObject.ParamFlags.READWRITE),
                       'icon-name-active':
                           (GObject.TYPE_STRING,
                            'icon name active',
                            'icon name active',
                            '',
                            GObject.ParamFlags.READWRITE),
                       'size':
                           (GObject.TYPE_UINT,
                            'size',
                            'size',
                            0,
                            GLib.MAXUINT,
                            16,
                            GObject.ParamFlags.READWRITE),
                       'has-frame':
                           (GObject.TYPE_BOOLEAN,
                            'has frame',
                            'has frame',
                            True,
                            GObject.ParamFlags.READWRITE)}

    def __init__(self, icon_name_normal='', size=16, has_frame=True):
        Gtk.Widget.__init__(self)
        self.set_has_window(False)

        # Initialize logging
        self.log = getLogger('%s.%s' % (self.__gtype_name__, hex(id(self))))

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
        """Used to reload the button icon after the widget is realized.

        """
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
        """Gets the property value.

        Args:
            pspec (GObject.ParamSpec): A property of the CompactButton.

        Returns:
            The parameter value.

        """
        if pspec.name == 'icon-name-normal':
            return self.get_icon_name_normal()
        elif pspec.name == 'icon-name-prelight':
            return self.get_icon_name_prelight()
        elif pspec.name == 'icon-name-active':
            return self.get_icon_name_active()
        elif pspec.name == 'size':
            return self.get_size()
        elif pspec.name == 'has-frame':
            return self.get_has_frame()

    def do_set_property(self, pspec, value):
        """Sets the property value.

        Args:
            pspec (GObject.ParamSpec): The property of the CompactButton to set.
            value: the value to set.

        """
        if pspec.name == 'icon-name-normal':
            self.set_icon_name_normal(value)
        elif pspec.name == 'icon-name-prelight':
            self.set_icon_name_prelight(value)
        elif pspec.name == 'icon-name-active':
            self.set_icon_name_active(value)
        elif pspec.name == 'size':
            self.set_size(value)
        elif pspec.name == 'has-frame':
            self.set_has_frame(value)

    def get_icon_name_normal(self):
        """Gets the name of the normal icon.

        Returns:
            string: The name of the normal icon.

        """
        return self._icon_name_normal

    def set_icon_name_normal(self, value):
        """Sets the name of the normal icon.

        Args:
            value (string): The name to set.

        """
        self._icon_name_normal = value
        self._icon_name_prelight = value
        self._icon_name_active = value

        if self.get_realized():
            self._refresh_icons()
            self.queue_resize()

    def get_icon_name_prelight(self):
        """Gets the name of the prelight icon.

        The prelight icon is the icon displayed when the pointer is over it.

        Returns:
            string: The name of the prelight icon.

        """
        return self._icon_name_prelight

    def set_icon_name_prelight(self, value):
        """Sets the name of the prelight icon.

        The prelight icon is the icon displayed when the pointer is over it.

        Args:
            value: The name to set.

        """
        self._icon_name_prelight = value
        self._icon_name_active = value

        if self.get_realized():
            self._refresh_icons()
            self.queue_resize()

    def get_icon_name_active(self):
        """Get the icon name when active.

        The active icon is the icon displayed when the button is pressed or active.

        Returns:
            string: The name of the active icon.

        """
        return self._icon_name_active

    def set_icon_name_active(self, value):
        """Set the name of the active icon.

        The active icon is the icon displayed when the button is pressed or active.

        Args:
            value: The name to set.

        """
        self._icon_name_active = value

        if self.get_realized():
            self._refresh_icons()
            self.queue_resize()

    def get_size(self):
        """Gets the size of the icon.

        Returns:
            int: The icon size.

        """
        return self._size

    def set_size(self, value):
        """Sets the size of the icon.

        Args:
            value (int): The size of the icon.

        """
        self._size = value

    def get_has_frame(self):
        """Gets whether the CompactButton has a frame.

        Returns:
            bool: Whether it has a frame.

        """
        return self._has_frame

    def set_has_frame(self, value):
        """Sets whether the CompactButton has a frame.

        Args:
            value (bool): Whether it has a frame.

        """
        self._has_frame = value

    ############################################################################
    # GtkWidget
    ############################################################################
    def do_realize(self):
        """Associate a Gdk.Window with the CompactButton widget.

        """
        allocation = self.get_allocation()
        attr = Gdk.WindowAttr()
        attr.x = allocation.x
        attr.y = allocation.y
        attr.width = allocation.width
        attr.height = allocation.height
        attr.window_type = Gdk.WindowType.CHILD
        attr.wclass = Gdk.WindowWindowClass.INPUT_ONLY
        attr.visual = self.get_visual()
        attr.event_mask = (Gdk.EventMask.EXPOSURE_MASK |
                           Gdk.EventMask.POINTER_MOTION_MASK |
                           Gdk.EventMask.BUTTON_PRESS_MASK |
                           Gdk.EventMask.BUTTON_RELEASE_MASK
                           )
        attr_mask = (Gdk.WindowAttributesType.X |
                           Gdk.WindowAttributesType.Y |
                           Gdk.WindowAttributesType.WMCLASS |
                           Gdk.WindowAttributesType.VISUAL
                           )
        self._input_window = Gdk.Window(self.get_parent_window(), attr, attr_mask)
        self._input_window.set_/ser_data(self)
        self._refresh_icons()
        self.set_realized(True)

    def do_unrealize(self):
        """Break the association with the Gdk.Window.

        This custom widget override is optional.

        """
        self._input_window.set_user_data(None)
        self._input_window.destroy()
        Gtk.Widget.do_unrealize(self)

    def do_map(self):
        """Causes the widget to be mapped if it isn't already.

        This custom widget override is optional.

        """
        self.set_mapped(True)
        self._input_window.show()

    def do_unmap(self):
        """Causes the widget to be unmapped if it is currently mapped.

        This custom widget override is optional.

        """
        self.set_mapped(False)
        self._input_window.hide()

    def do_get_request_mode(self):
        """Returns the preferred widget layout.

        Returns whether the container prefers a height-for-width or a
        width-for-height layout. CompactButton doesn't trade width for height
        or height for width so we return CONSTANT_SIZE.

        Returns:
            Gtk.SizeRequestMode: the constant size request mode

        """
        return Gtk.SizeRequestMode.CONSTANT_SIZE

    def do_get_preferred_height(self):
        """Calculates the widget's initial minimum and natural height.

        While this call is specific to width-for-height requests (that we
        requested not to get) we cannot be certain that our wishes are granted,
        so we must implement this method as well. Returns the icon size as the
        minimum and natural height.

        Returns:
             int: minimum height, natural height

        """
        icon_size = self.get_size()
        return icon_size, icon_size

    def do_get_preferred_width(self):
        """Calculates the widget's initial minimum and natural width.

        While this call is specific to width-for-height requests (that we requested
        not to get) we cannot be certain that our wishes are granted, so
        we must implement this method as well. Returns the icon size as the
        minimum and natural width.

        Returns:
            int: minimum width, natural width

        """
        icon_size = self.get_size()
        return icon_size, icon_size

    def do_get_preferred_height_for_width(self, width):
        """If given width, returns the minimum and natural height.

        Returns the container's minimum and natural height if given the
        specified width. While this call is specific to height-for-width
        requests (that we requested not to get) we cannot be certain that our
        wishes are granted, so we must implement this method as well. Since we
        really want to be the same size always, we simply return
        do_get_preferred_height.

        Args:
            width (int): The given width. Ignored.

        Returns:
            int: minimum height, natural height

        """
        return self.do_get_preferred_height()

    def do_get_preferred_width_for_height(self, height):
        """If given height, returns the minimum and natural width.

        Returns the container's minimum and natural width if given the
        specified height. While this call is specific to width-for-height
        requests (that we requested not to get) we cannot be certain that our
        wishes are granted, so we must implement this method as well. Since we
        really want to be the same size always, we simply return
        do_get_preferred_width.

        Args:
            height (int): The given height. Ignored.

        Returns:
            int: minimum width, natural width

        """
        return self.do_get_preferred_width()

    def do_size_allocate(self, allocation):
        """Position the CompactButton, given the allocation.

        Args:
            allocation (Gdk.Rectangle): The position and size to be allocated

        """
        self.allocation = allocation

        if self.get_realized():
            self._input_window.move_resize(allocation.x, allocation.y, allocation.width, allocation.height)

    def do_draw(self, cr):
        """Draw on supplied Cairo Context.

        Draws the icon and frame of the CompactButton.

        Args:
            cr (cairo.Context): The context to draw on

        """
        # Draw icon
        if self.state == Gtk.StateFlags.PRELIGHT:
            pixbuf = self._icon_prelight
            x = self.allocation.x
            y = self.allocation.y
        elif self.state == Gtk.StateFlags.ACTIVE:
            pixbuf = self._icon_active
            x = self.allocation.x + 1
            y = self.allocation.y + 1
        else:  # Gtk.StateFlags.NORMAL and all others
            pixbuf = self._icon_normal
            x = self.allocation.x
            y = self.allocation.y

        Gdk.cairo_set_source_pixbuf(cr, pixbuf, x, y)
        cr.paint()

        # Draw frame
        if self._has_frame and self.state != Gtk.StateFlags.NORMAL:
            style_provider = Gtk.CssProvider()
            style_context = self.get_style_context()
            style_context.add_provider(style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            style_context.set_state(self.state)
            Gtk.render_frame(
                context=style_context,
                cr=cr,
                x=self.allocation.x,
                y=self.allocation.y,
                width=self.allocation.width - 1,
                height=self.allocation.height - 1
            )

    def do_enter_notify_event(self, event):
        """Called when the pointer has entered the widget.

        Args:
            event (Gdk.EnterCrossing): The event that is generated when the pointer enters.

        Returns:
            True.

        """
        self._entered = True
        self.set_state(Gtk.StateFlags.PRELIGHT)
        self.queue_draw()
        return True

    def do_leave_notify_event(self, event):
        """Called when the pointer has entered the widget.

        Args:
            event (Gdk.EventCrossing): The event that is generated when the pointer leaves.

        Returns:
            True.

        """
        self._entered = False
        self.set_state(Gtk.StateFlags.NORMAL)
        self.queue_draw()
        return True

    def do_button_press_event(self, event):
        """Called wen the pointer button is clicked.

        Args:
            event (Gdk.EventButton): Button press event.

        Returns:
            True.

        """
        if event.button == 1:
            self.set_state(Gtk.StateFlags.ACTIVE)
            self.queue_draw()

        return True

    def do_button_release_event(self, event):
        """Called when the pointer button is released.

        Args:
            event (Gdk.EventButton): Button release event.

        Returns:
            True.

        """
        if event.button == 1 and self._entered:
            self.set_state(Gtk.StateFlags.PRELIGHT)
            self.emit('clicked')
            self.queue_draw()

        return True
