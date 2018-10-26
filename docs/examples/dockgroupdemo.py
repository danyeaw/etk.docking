#!/usr/bin/env python
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

from builtins import range
import logging
import random

from gi.repository import GObject
from gi.repository import Gtk
import Gtk.gdk as gdk
from gi.repository import Pango

try:
    from etkdocking import DockLayout, DockPaned, DockGroup, DockItem
except ImportError:
    # The lib directory is most likely not on PYTHONPATH, so add it here.
    import os, sys

    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    from etkdocking import DockLayout, DockPaned, DockGroup, DockItem

    del os, sys


class MainWindow(Gtk.Window):
    def __init__(self):
        GObject.GObject.__init__(self)

        self.set_default_size(500, 150)
        self.set_title('DockGroup Demo')
        self.set_border_width(4)
        self.file_counter = 1

        vbox = Gtk.VBox()
        vbox.set_spacing(4)
        self.add(vbox)

        ########################################################################
        # Docking
        ########################################################################
        self.dg = DockGroup()
        vbox.pack_start(child=self.dg, expand=True, fill=True, padding=0)

        ########################################################################
        # Testing Tools
        ########################################################################
        adddibutton = Gtk.Button.new_with_label('Create docked items')
        adddibutton.get_child().set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        adddibutton.connect('clicked', self._on_add_di_button_clicked)
        vbox.pack_start(child=adddibutton, expand=False, fill=False, padding=0)

        self.show_all()

    def _on_add_di_button_clicked(self, button):
        examples = [('calc', 'calculator', '#!/usr/bin/env python\n\nprint \'Hello!\''),
                    ('file-manager', 'Hi!', 'Hello!'),
                    ('fonts', 'ABC', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
                    ('style', 'abc', 'abcdefghijklmnopqrstuvwxyz'),
                    ('web-browser', 'browser', '0123456789'),
                    ('date', 'today', '9876543210')]

        for i in range(random.randrange(1, 10, 1)):
            icon_name, tooltip_text, text = random.choice(examples)

            # Create a TextView and set some example text
            scrolledwindow = Gtk.ScrolledWindow()
            scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            textview = Gtk.TextView()
            textview.get_buffer().set_text(text)
            scrolledwindow.add(textview)

            # Create a DockItem and add our TextView
            di = DockItem(icon_name=icon_name, title='New %s' % self.file_counter, title_tooltip_text=tooltip_text)
            di.add(scrolledwindow)
            di.show_all()

            # Add out DockItem to the DockGroup
            self.dg.add(di)

            # Increment file counter
            self.file_counter += 1


def quit(widget, event, mainloop):
    mainloop.quit()


def main():
    # Initialize logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s\t%(levelname)s\t%(name)s\t%(funcName)s\t%(message)s')

    # Uncomment to enable log filtering
    # for handler in logging.getLogger('').handlers:
    #    handler.addFilter(logging.Filter('EtkDockGroup'))

    # Initialize mainloop
    GObject.threads_init()
    mainloop = GObject.MainLoop()

    # Initialize mainwindow
    mainwindow = MainWindow()
    mainwindow.connect('delete-event', quit, mainloop)
    mainwindow.show()

    # Run mainloop
    mainloop.run()


if __name__ == '__main__':
    main()
