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


import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def rect_contains(rect, x, y):
    """Checks if a point, defined by x and y, falls within the rectangle.

    Note: Unlike rect_overlaps defined below, this function ignores a 1 pixel
    border. This function is used by the DockGroup to determine if an event
    occurs within a DockGroupTab.

    Args:
        rect: An area defined by x, y, width, and height.
        x (int): The x position of the point.
        y (int): The y position of the point.

    Returns:
        bool: True if the point is in the rectangle.

    """
    if x > rect.x and x < rect.x + rect.width and y > rect.y and y < rect.y + rect.height:
        return True
    else:
        return False


def rect_overlaps(rect, x, y):
    """Checks if a point, defined by x and y, overlaps the rectangle.

    Note: Unlike rect_contains defined above, this function does not ignore a 1
    pixel border. This function is used by DockPaned to determine if an event
    occurs overlapping a DockPanedHandle.

    Args:
        rect: An area defined by x, y, width, and height.
        x (int): The x position of the point.
        y (int): The y position of the point.

    Returns:
        bool: True if the point is in the rectangle.

    """
    if x >= rect.x and x <= rect.x + rect.width and y >= rect.y and y <= rect.y + rect.height:
        return True
    else:
        return False


def load_icon(icon_name, size):
    """Looks up an icon, scales it and renders it to a pixbuf.

    # TODO: Should change/add on to this. It does not work well with
    # IconFactories for example.

    Args:
        icon_name (string): The name of the icon to lookup.
        size (int): The desired icon size.

    Returns:
        Gdk.Pixbuf.Pixbuf: The rendered icon as a pixbuf.

    """

    icontheme = Gtk.IconTheme.get_default()

    if not icontheme.has_icon(icon_name):
        icon_name = 'gtk-missing-image'

    return icontheme.load_icon(icon_name, size, Gtk.IconLookupFlags.USE_BUILTIN)


def load_icon_image(icon_name, size):
    """Creates a Gtk.Image displaying an icon from the current icon theme.

    Args:
        icon_name (string): An icon name for the new icon.
        size (int): A stock icon size (Gtk.IconSize)

    Returns:
        Gtk.Widget: The created Gtk.Image icon.

    """
    icontheme = Gtk.IconTheme.get_default()

    if not icontheme.has_icon(icon_name):
        icon_name = 'gtk-missing-image'

    return Gtk.Image.new_from_icon_name(icon_name, size)


def flatten(w, child_getter=Gtk.Container.get_children):
    """Generator function that returns all items in a hierarchy.

    Default `child_getter` returns children in a GTK+ widget hierarchy.

    Args:
        w: The root node of the hierarchy, for Gtk+ often a Window.
        child_getter: Function call that returns a list of children.

    Yields:
        object: Item in a hierarchy.

    """
    yield w
    try:
        for c in child_getter(w):
            for d in flatten(c, child_getter):
                yield d
    except TypeError:
        pass  # Not a child of the right type
