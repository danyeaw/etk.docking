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
from builtins import object
from logging import getLogger

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import cairo


DRAG_TARGET_ITEM_LIST = Gtk.TargetEntry.new("x-etk-docking/item-list", Gtk.TargetFlags.SAME_APP, 0)


class DockDragContext(object):
    '''
    As we can't reliably use drag_source_set to initiate a drag operation
    (there's just to much information locked away in C structs - GtkDragSourceSite,
    GtkDragSourceInfo, GtkDragDestSite, GtkDragDestInfo, ... - that are not
    exposed to Python), we are sadly forced to mimic some of that default behavior.

    This class is also used to store extra information about a drag operation
    in progress not available in the C structs mentioned above.
    '''
    __slots__ = ['dragging',  # are we dragging or not (bool)
                 'dragged_object',  # object being dragged
                 'source_x',  # x coordinate starting a potential drag
                 'source_y',  # y coordinate starting a potential drag
                 'source_button',  # the button the user pressed to start the drag
                 'offset_x',  # cursor x offset relative to dragged object source_x
                 'offset_y']  # cursor y offset relative to dragged object source_y

    def __init__(self):
        self.reset()

    def reset(self):
        self.dragging = False
        self.dragged_object = None
        self.source_x = None
        self.source_y = None
        self.source_button = None
        self.offset_x = None
        self.offset_y = None


class Placeholder(Gtk.DrawingArea):
    __gtype_name__ = 'EtkDockPlaceholder'

    def __init__(self):
        Gtk.DrawingArea.__init__(self)

    def do_draw(self, cr):
        alloc = self.allocation
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1.0)
        cr.rectangle(0.5, 0.5, alloc.width - 1, alloc.height - 1)
        cr.stroke()


class PlaceHolderWindow(Gtk.Window):
    '''
    The etk.dnd.PlaceHolderWindow is a Gtk.Window that can highlight an area
    on screen. When a PlaceHolderWindow has no child widget an undecorated
    utility popup is shown drawing a transparent highlighting rectangle around
    the desired area. The location and size of the highlight rectangle can
    easily be updated with the move_resize method. The show and hide methods
    do as they suggest.

    When you add a child widget to the PlaceHolderWindow the utility popup is
    automatically decorated (get's a title bar) and removes it's transparency.

    This is used by the drag and drop implementation to mark a valid destination
    for the drag and drop operation while dragging and as the container window
    for teared off floating items.
    '''
    __gtype_name__ = 'EtkDockPlaceHolderWindow'

    def __init__(self):
        Gtk.Window.__init__(self, Gtk.WindowType.POPUP)
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        # TODO: self.set_transient_for(???.get_toplevel())

        # Initialize logging
        self.log = getLogger('%s.%s' % (self.__gtype_name__, hex(id(self))))

    def _create_shape(self, da, ctx):
        width, height = self.get_size()
        mask = cairo.SolidPattern(255, 255, 255, 0)
        ctx.set_source_rgba(0, 0, 0, 1)
        ctx.rectangle(0, 0, width, height)
        ctx.mask(mask)

    ############################################################################
    # GtkWidget
    ############################################################################
    def do_realize(self):
        Gtk.Window.do_realize(self)

    def do_unrealize(self):
        Gtk.Window.do_unrealize(self)

    def do_size_allocate(self, allocation):
        self.log.debug('%s' % allocation)
        Gtk.Window.do_size_allocate(self, allocation)
        drawingarea = Gtk.DrawingArea
        drawingarea.connect("draw", self._create_shape)

    ############################################################################
    # GtkContainer
    ############################################################################
    def do_add(self, widget):
        self.set_decorated(True)
        self.reset_shapes()
        Gtk.Window.add(self, widget)

    ############################################################################
    # EtkPlaceHolderWindow
    ############################################################################
    def move_resize(self, x, y, width, height):
        self.log.debug('%s, %s, %s, %s' % (x, y, width, height))

        self.move(x, y)
        self.resize(width, height)
