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
from gi.repository import Gtk, GObject, Gdk


class DockFrame(Gtk.Bin):
    '''
    The etk.DockFrame widget is a Gtk.Bin that acts as the toplevel widget
    for a dock layout hierarchy.
    '''
    __gtype_name__ = 'EtkDockFrame'

    def __init__(self):
        Gtk.Bin.__init__(self)

        # Initialize logging
        self.log = getLogger('%s.%s' % (self.__gtype_name__, hex(id(self))))

        # Internal housekeeping
        self._placeholder = None
        self.border_width = 0

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
        """Returns whether the DockFrame prefers a height-for-width or a
        width-for-height layout. DockFrame doesn't trade width for height or
        height for width so we return CONSTANT_SIZE.
        """
        return Gtk.SizeRequestMode.CONSTANT_SIZE

    def do_get_preferred_height(self):
        """Calculates the DockFrame's initial minimum and natural height. While
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
        """Calculates the DockFrame's initial minimum and natural width. While
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
        """Returns this DockFrame's minimum and natural height if it would be
        given the specified width. While this call is specific to
        height-for-width requests (that we requested not to get) we cannot be
        certain that our wishes are granted, so we must implement this method
        as well. Since we really want to be the same size always, we simply
        return do_get_preferred_height.

        @param width The given width, as int. Ignored.
        """
        return self.do_get_preferred_height()

    def do_get_preferred_width_for_height(self, height):
        """Returns this DockFrame's minimum and natural width if it would be
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
    # EtkDockFrame
    ############################################################################
    def set_placeholder(self, placeholder):
        """
        Set a new placeholder widget on the frame. The placeholder is drawn on top
        of the dock items.

        If a new placeholder is set, an existing placeholder is destroyed.
        """
        if self._placeholder:
            self._placeholder.unparent()
            self._placeholder.destroy()
            self._placeholder = None

        if placeholder:
            self._placeholder = placeholder
            self._placeholder.set_parent(self)
