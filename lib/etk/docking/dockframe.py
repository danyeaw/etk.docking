# -*- coding: utf-8 -*-
# vim:sw=4:et:ai
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


from __future__ import absolute_import
from logging import getLogger

import gtk


class DockFrame(gtk.EventBox):
    """
    Top level widget for a dock layout hierarchy.
    """
    __gtype_name__ = 'EtkDockLayout'

    def __init__(self):
        gtk.EventBox.__init__(self)

        # Initialize logging
        self.log = getLogger('<%s object at %s>' % (self.__gtype_name__, hex(id(self))))

        # Child containers:
        self._floating_windows = []
        #self.set_above_child(True)


    ############################################################################
    # GtkWidget drag source
    ############################################################################

    def do_drag_begin(self, context):
        self.log.debug('Layout do_drag_begin: %s' % context)

    ############################################################################
    # GtkWidget drag destination
    ############################################################################

    def do_drag_motion(self, context, x, y, timestamp):
        print 'Layout drag motion', x, y

