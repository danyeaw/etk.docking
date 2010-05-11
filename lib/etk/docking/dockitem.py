# -*- coding: utf-8 -*-
#
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


from __future__ import absolute_import,  division
from logging import getLogger

import gobject
import gtk
import gtk.gdk as gdk


class DockItem(gtk.Bin):
    __gtype_name__ = 'EtkDockItem'
    __gproperties__ = {'icon-name': (gobject.TYPE_STRING,
                                     'icon name',
                                     'icon name',
                                     '',
                                     gobject.PARAM_READWRITE),
                       'title': (gobject.TYPE_STRING,
                                 'icon name',
                                 'icon name',
                                 '',
                                 gobject.PARAM_READWRITE),
                       'title-tooltip-text': (gobject.TYPE_STRING,
                                              'title tooltip text',
                                              'title tooltip text',
                                              '',
                                              gobject.PARAM_READWRITE)}

    def __init__(self, icon_name='', title='', title_tooltip_text=''):
        gtk.Bin.__init__(self)
        self.set_flags(self.flags() | gtk.NO_WINDOW)

        # Initialize logging
        self.log = getLogger('<%s object at %s>' % (self.__gtype_name__, hex(id(self))))

        # Internal housekeeping
        self._icon_name = icon_name
        self._title = title
        self.set_name(title)
        self._title_tooltip_text = title_tooltip_text

    ############################################################################
    # GObject
    ############################################################################
    def do_get_property(self, pspec):
        if pspec.name == 'icon-name':
            return self.get_icon_name()
        elif pspec.name == 'title':
            return self.get_title()
        elif pspec.name == 'title-tooltip-text':
            return self.get_title_tooltip_text()

    def do_set_property(self, pspec, value):
        if pspec.name == 'icon-name':
            self.set_icon_name(value)
        elif pspec.name == 'title':
            self.set_title(value)
        elif pspec.name == 'title-tooltip-text':
            self.set_title_tooltip_text(value)

    def get_icon_name(self):
        return self._icon_name

    def set_icon_name(self, value):
        self._icon_name = value
        self.notify('icon-name')

    def get_title(self):
        return self._title

    def set_title(self, value):
        self._title = value
        self.set_name(value)
        self.notify('title')

    def get_title_tooltip_text(self):
        return self._title_tooltip_text

    def set_title_tooltip_text(self, value):
        self._title_tooltip_text = value
        self.notify('title-tooltip-text')

    ############################################################################
    # GtkWidget
    ############################################################################
    def do_realize(self):
        self.set_flags(self.flags() | gtk.REALIZED)

        self.window = gdk.Window(self.get_parent_window(),
                                 x = self.allocation.x,
                                 y = self.allocation.y,
                                 width = self.allocation.width,
                                 height = self.allocation.height,
                                 window_type = gdk.WINDOW_CHILD,
                                 wclass = gdk.INPUT_OUTPUT,
                                 event_mask = (gdk.EXPOSURE_MASK))
        self.window.set_user_data(self)
        self.style.attach(self.window)
        self.style.set_background(self.window, gtk.STATE_NORMAL)

        if self.child:
            self.child.set_parent_window(self.window)

    def do_unrealize(self):
        self.window.set_user_data(None)
        self.window.destroy()
        gtk.Bin.do_unrealize(self)

    def do_map(self):
        gtk.Bin.do_map(self)

        if self.window:
            self.window.show()

    def do_unmap(self):
        gtk.Bin.do_unmap(self)
        self.window.hide()

    def do_show(self):
        gtk.Bin.do_show(self)
        self.child.show()

    def do_hide(self):
        gtk.Bin.do_hide(self)
        self.child.hide()

    def do_size_request(self, requisition):
        requisition.width = self.border_width * 2
        requisition.height = self.border_width * 2

        if self.child:
            (w, h) = self.child.size_request()
            requisition.width += w
            requisition.height += h

    def do_size_allocate(self, allocation):
        self.allocation = allocation

        if self.child:
            child_allocation = gdk.Rectangle()
            child_allocation.x = self.border_width
            child_allocation.y = self.border_width
            child_allocation.width = max(self.allocation.width - self.border_width, 0)
            child_allocation.height = max(self.allocation.height - self.border_width, 0)
            self.child.size_allocate(child_allocation)

        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*self.allocation)
