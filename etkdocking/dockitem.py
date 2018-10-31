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
from gi.repository import Gtk, Gdk, GObject


class DockItem(Gtk.Bin):
    __gtype_name__ = 'EtkDockItem'
    __gproperties__ = {'title':
                           (GObject.TYPE_STRING,
                            'Title',
                            'The title for the DockItem.',
                            '',
                            GObject.ParamFlags.READWRITE),
                       'title-tooltip-text':
                           (GObject.TYPE_STRING,
                            'Title tooltip text',
                            'The tooltip text for the title.',
                            '',
                            GObject.ParamFlags.READWRITE),
                       'icon-name':
                           (GObject.TYPE_STRING,
                            'Icon name',
                            'The name of the icon from the icon theme.',
                            '',
                            GObject.ParamFlags.READWRITE),
                       'stock':
                           (GObject.TYPE_STRING,
                            'Stock',
                            'Stock ID for a stock image to display.',
                            '',
                            GObject.ParamFlags.READWRITE),
                       'image':
                           (GObject.TYPE_PYOBJECT,
                            'Image',
                            'The image constructed from the specified stock ID or icon-name. Default value is Gtk.STOCK_MISSING_IMAGE.',
                            GObject.ParamFlags.READABLE)}
    __gsignals__ = {'close':
                        (GObject.SignalFlags.RUN_LAST,
                         None, ())}

    def __init__(self, title='', title_tooltip_text='', icon_name=None, stock_id=None):
        Gtk.Bin.__init__(self)

        self.set_has_window(False)

        self.set_redraw_on_allocate(False)

        # Initialize logging
        self.log = getLogger('%s.%s' % (self.__gtype_name__, hex(id(self))))

        # Internal housekeeping
        self._icon_name = icon_name
        self._stock_id = stock_id

        self.set_title(title)
        self.set_title_tooltip_text(title_tooltip_text)
        self.set_icon_name(icon_name)
        self.set_stock(stock_id)

    ############################################################################
    # GObject
    ############################################################################
    def do_get_property(self, pspec):
        if pspec.name == 'title':
            return self.get_title()
        elif pspec.name == 'title-tooltip-text':
            return self.get_title_tooltip_text()
        elif pspec.name == 'icon-name':
            return self.get_icon_name()
        elif pspec.name == 'stock':
            return self.get_stock()
        elif pspec.name == 'image':
            return self.get_image()

    def do_set_property(self, pspec, value):
        if pspec.name == 'title':
            self.set_title(value)
        elif pspec.name == 'title-tooltip-text':
            self.set_title_tooltip_text(value)
        elif pspec.name == 'icon-name':
            self.set_icon_name(value)
        elif pspec.name == 'stock':
            self.set_stock(value)

    def get_title(self):
        return self._title

    def set_title(self, text):
        self._title = text
        self.notify('title')

    def get_title_tooltip_text(self):
        return self._title_tooltip_text

    def set_title_tooltip_text(self, text):
        self._title_tooltip_text = text
        self.notify('title-tooltip-text')

    def get_icon_name(self):
        return self._icon_name

    def set_icon_name(self, icon_name):
        self._icon_name = icon_name
        self.notify('icon-name')

    def get_stock(self):
        return self._stock_id

    def set_stock(self, stock_id):
        self._stock_id = stock_id
        self.notify('stock')

    def get_image(self):
        if self._icon_name:
            return Gtk.Image.new_from_icon_name(self._icon_name, Gtk.IconSize.MENU)
        elif self._stock_id:
            return Gtk.Image.new_from_stock(self._stock_id, Gtk.IconSize.MENU)
        else:
            return Gtk.Image()

    title = property(get_title, set_title)
    title_tooltip_text = property(get_title_tooltip_text, set_title_tooltip_text)
    icon_name = property(get_icon_name, set_icon_name)
    stock = property(get_stock, set_stock)

    ############################################################################
    # GtkContainer
    ############################################################################
    def do_child_type(self):
        """Indicates that this container accepts any GTK+ widget."""
        return Gtk.Widget.get_type()

    def do_forall(self, include_internals, callback, *callback_data):
        """Invokes the given callback on the child widget, with the given data.

        @param include_internals Whether to run on internal children as well, as
                                 boolean. Ignored, as there are no internal
                                 children.
        @param callback The callback to call on the child, as Gtk.Callback
        @param callback_data The parameters to pass to the callback, as object
                             or None
        """
        child = self.get_child()
        if include_internals and child:
            callback(child, *callback_data)

    ############################################################################
    # GtkWidget
    ############################################################################
    def do_get_request_mode(self):
        """Returns whether the DockItem prefers a height-for-width or a
        width-for-height layout. DockItem doesn't trade width for height or
        height for width so we return CONSTANT_SIZE.
        """
        return Gtk.SizeRequestMode.CONSTANT_SIZE

    def do_get_preferred_height(self):
        """Calculates the DockItem's initial minimum and natural height. While
        this call is specific to width-for-height requests (that we requested
        not to get) we cannot be certain that our wishes are granted, so we
        must implement this method as well. Returns the preferred height of the
        child widget with padding added for the border width.
        """
        minimum_height = 0
        natural_height = 0
        child = self.get_child()
        if child and child.props.visible:
            minimum_height, natural_height = child.get_preferred_height()
            minimum_height += self.border_width * 2
            natural_height += self.border_width * 2
        return minimum_height, natural_height

    def do_get_preferred_width(self):
        """Calculates the DockItem's initial minimum and natural width. While
        this call is specific to width-for-height requests (that we requested
        not to get) we cannot be certain that our wishes are granted, so
        we must implement this method as well. Returns the preferred width of
        the child widget with padding added for the border width.
        """
        minimum_width = 0
        natural_width = 0
        child = self.get_child()
        if child and child.props.visible:
            minimum_width, natural_width = child.get_preferred_width()
            minimum_width += self.border_width * 2
            natural_width += self.border_width * 2
        return minimum_width, natural_width

    def do_get_preferred_height_for_width(self, width):
        """Returns this DockItem's minimum and natural height if it would be
        given the specified width. While this call is specific to
        height-for-width requests (that we requested not to get) we cannot be
        certain that our wishes are granted, so we must implement this method
        as well. Since we really want to be the same size always, we simply
        return do_get_preferred_height.

        @param width The given width, as int. Ignored.
        """
        return self.do_get_preferred_height()

    def do_get_preferred_width_for_height(self, height):
        """Returns this DockItem's minimum and natural width if it would be
        given the specified height. While this call is specific to
        width-for-height requests (that we requested not to get) we cannot be
        certain that our wishes are granted, so we must implement this method
        as well. Since we really want to be the same size always, we simply
        return do_get_preferred_width.

        @param height The given height, as int. Ignored.
        """
        return self.do_get_preferred_width()

    def do_size_allocate(self, allocation):
        self.border_width = self.get_border_width()
        child = self.get_child()

        if child and child.props.visible:
            child_allocation = Gdk.Rectangle()
            child_allocation.x = allocation.x + self.border_width
            child_allocation.y = allocation.y + self.border_width
            child_allocation.width = allocation.width - (2 * self.border_width)
            child_allocation.height = allocation.height - (2 * self.border_width)
            self.child.size_allocate(child_allocation)

    ############################################################################
    # DockItem
    ############################################################################
    def do_close(self):
        group = self.get_parent()
        if group:
            group.remove(self)

    def close(self):
        self.emit('close')
