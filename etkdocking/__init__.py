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


__all__ = ["DockLayout", "DockFrame", "DockPaned", "DockGroup", "DockItem", "settings"]
__version__ = "0.3"
__docformat__ = "restructuredtext"


############################################################################
# Initialization
############################################################################
import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

# Register some custom icons into the default icon theme
path = os.path.abspath(os.path.join(os.path.dirname(__file__), "icons", "16x16"))
Gtk.IconTheme.add_builtin_icon(
    "compact-close",
    16,
    GdkPixbuf.Pixbuf.new_from_file(os.path.join(path, "compact-close.png")),
)
Gtk.IconTheme.add_builtin_icon(
    "compact-close-prelight",
    16,
    GdkPixbuf.Pixbuf.new_from_file(os.path.join(path, "compact-close-prelight.png")),
)
Gtk.IconTheme.add_builtin_icon(
    "compact-list",
    16,
    GdkPixbuf.Pixbuf.new_from_file(os.path.join(path, "compact-list.png")),
)
Gtk.IconTheme.add_builtin_icon(
    "compact-minimize",
    16,
    GdkPixbuf.Pixbuf.new_from_file(os.path.join(path, "compact-minimize.png")),
)
Gtk.IconTheme.add_builtin_icon(
    "compact-maximize",
    16,
    GdkPixbuf.Pixbuf.new_from_file(os.path.join(path, "compact-maximize.png")),
)
Gtk.IconTheme.add_builtin_icon(
    "compact-restore",
    16,
    GdkPixbuf.Pixbuf.new_from_file(os.path.join(path, "compact-restore.png")),
)

# Check for elib, not required.
try:
    from elib.intl import install_module
except ImportError:

    def _(message):
        return message


# else:
#     localedir = os.path.abspath(
#         os.path.join(os.path.dirname(__file__), "..", "..", "share", "locale")
#     )
#     _ = install_module("etkdocking", localedir)
#     del localedir, install_module

# Keep our namespace nice and tidy
del os, gi, path

############################################################################
# GtkBuilder and Glade create GObject instances (and thus GTK+ widgets) using
# GObject.new(). For this to work, we have to be sure our subclasses have been
# registered with the GObject type system when etkdocking is imported.
# This also defines the widgets that can be considered public.
############################################################################
from .docklayout import DockLayout
from .docklayout import (
    add_new_group_left,
    add_new_group_right,
    add_new_group_above,
    add_new_group_below,
    add_new_group_floating,
)
from .dockframe import DockFrame
from .dockpaned import DockPaned
from .dockgroup import DockGroup
from .dockitem import DockItem
from .docksettings import settings
