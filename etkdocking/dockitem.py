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
    """DockItems are added as tabs to a DockGroup.

    DockItems have an icon image, a title, tooltip, and use the CompactButtons
    for user input for things like requesting that the tab is closed or
    maximized. Each DockItem is a Gtk.Bin and can have a single child widget.

    """
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
        """Gets the property value.

        Args:
            pspec (GObject.ParamSpec): A property of the CompactButton.

        Returns:
            The parameter value.

        """
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
        """Sets the property value.

        Args:
            pspec (GObject.ParamSpec): The property of the CompactButton to set.
            value: the value to set.

        """
        if pspec.name == 'title':
            self.set_title(value)
        elif pspec.name == 'title-tooltip-text':
            self.set_title_tooltip_text(value)
        elif pspec.name == 'icon-name':
            self.set_icon_name(value)
        elif pspec.name == 'stock':
            self.set_stock(value)

    def get_title(self):
        """Get title of DockItem.

        Returns:
            string: Title of DockItem.

        """
        return self._title

    def set_title(self, text):
        """Set title of DockItem.

        Args:
            text (string): Text to set title of DockItem to.

        """
        self._title = text
        self.notify('title')

    def get_title_tooltip_text(self):
        """Get tooltip text of DockItem title that is displayed on hover.

        Returns:
            string: Tooltip text of title.

        """
        return self._title_tooltip_text

    def set_title_tooltip_text(self, text):
        """Set tootip text of DockItem title that is displayed on hover.

        Args:
            text (string): Text to set tooltip to.

        """
        self._title_tooltip_text = text
        self.notify('title-tooltip-text')

    def get_icon_name(self):
        """Get icon name of DockItem.

        Returns:
            string: Icon name.

        """
        return self._icon_name

    def set_icon_name(self, icon_name):
        """Set icon name of DockItem.

        Args:
            icon_name (string): Icon name to set.

        """
        self._icon_name = icon_name
        self.notify('icon-name')

    def get_stock(self):
        """Gets the icon stock id.

        TODO: stock has been deprecated in Gtk+

        Returns:

        """
        return self._stock_id

    def set_stock(self, stock_id):
        """Sets the icon stock id.

        TODO: stock has been deprecated in Gtk+

        Args:
            stock_id (string): A stock icon name.

        """
        self._stock_id = stock_id
        self.notify('stock')

    def get_image(self):
        """Gets the Gtk.Image for the DockItem.

        Returns:
            Gtk.Image: The image displayed in the DockItem tab.

        """
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
    # Gtk.Container
    ############################################################################
    def do_child_type(self):
        """Indicates that this container accepts any GTK+ widget.

            Returns:
                GObject.GType: The type of children supported by the Container.
        """
        return Gtk.Widget.get_type()

    def do_forall(self, include_internals, callback, *callback_data):
        """Invokes the given callback on each tab, with the given data.

        Args:
            include_internals (bool): Run on internal children
            callback (Gtk.Callback): The callback to call on each child
            callback_data (object or None): The parameters to pass to the
                callback

        """
        child = self.get_child()
        if include_internals and child:
            callback(child, *callback_data)

    ############################################################################
    # Gtk.Widget
    ############################################################################
    def do_get_request_mode(self):
        """Returns the preferred container layout.

        Returns whether the container prefers a height-for-width or a
        width-for-height layout. DockGroup doesn't trade width for height or
        height for width so we return CONSTANT_SIZE.

        Returns:
            Gtk.SizeRequestMode: the constant size request mode.

        """
        return Gtk.SizeRequestMode.CONSTANT_SIZE

    def do_get_preferred_height(self):
        """Calculates the DockItem's initial minimum and natural height.

        While this call is specific to width-for-height requests (that we requested
        not to get) we cannot be certain that our wishes are granted, so
        we must implement this method as well. Returns the the decoration area
        height.

        Returns:
             int: minimum height, natural height.

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
        """Calculates the container's initial minimum and natural width.

        While this call is specific to width-for-height requests (that we
        requested not to get) we cannot be certain that our wishes are granted,
        so we must implement this method as well. Returns the decoration area
        width.

        Returns:
            int: minimum width, natural width

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
        """If given width, returns the minimum and natural height.

        Returns the DockItem's minimum and natural height if given the
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

        Returns the DockItem's minimum and natural width if given the
        specified height. While this call is specific to width-for-height
        requests (that we requested not to get) we cannot be certain that our
        wishes are granted, so we must implement this method as well. Since we
        really want to be the same size always, we simply return
        do_get_preferred_width.

        Args:
            height (int): The given height. Ignored.

        Returns:
            int: minimum width, natural width.

        """
        return self.do_get_preferred_width()

    def do_size_allocate(self, allocation):
        """Assigns a size and position to DockItem's child widget.

        The child may adjust the given allocation in the adjust_size_allocation
        virtual method.

        Args:
            allocation (Gdk.Rectangle): Position and size allocated.

        """
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
        """Removes the DockItem from the parent DockGroup.

        """
        group = self.get_parent()
        if group:
            group.remove(self)

    def close(self):
        """Emits the close signal on the DockItem.

        """
        self.emit('close')