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


from __future__ import division

from builtins import range
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GObject


class HslColor(GObject.GObject):
    """

    """
    __gtype_name__ = 'EtkHslColor'
    __gproperties__ = {'h': (float, 'h', 'h', 0.0, 1.0, 0.0, GObject.ParamFlags.READWRITE),
                       's': (float, 's', 's', 0.0, 1.0, 0.0, GObject.ParamFlags.READWRITE),
                       'l': (float, 'l', 'l', 0.0, 1.0, 0.0, GObject.ParamFlags.READWRITE),
                       'red-float': (
                           float, 'red-float', 'red-float', 0.0, 1.0, 0.0, GObject.ParamFlags.READABLE
                       ),
                       'green-float': (
                           float, 'green-float', 'green-float', 0.0, 1.0, 0.0, GObject.ParamFlags.READABLE
                       ),
                       'blue-float': (
                           float, 'blue-float', 'blue-float', 0.0, 1.0, 0.0, GObject.ParamFlags.READABLE
                       )
                       }

    def __init__(self, color):
        GObject.GObject.__init__(self)

        self._update_hsl(color)
        self._update_rgb()

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
        if pspec.name == 'h':
            return self.get_h()
        elif pspec.name == 's':
            return self.get_s()
        elif pspec.name == 'l':
            return self.get_l()
        elif pspec.name == 'red-float':
            return self.get_red_float()
        elif pspec.name == 'green-float':
            return self.get_green_float()
        elif pspec.name == 'blue-float':
            return self.get_blue_float()

    def do_set_property(self, pspec, value):
        """Sets the property value.

        Args:
            pspec (GObject.ParamSpec): The property of the CompactButton to set.
            value: the value to set.

        """
        if pspec.name == 'h':
            self.set_h(value)
        elif pspec.name == 's':
            self.set_s(value)
        elif pspec.name == 'l':
            self.set_l(value)

    def get_h(self):
        """Gets the color's hue.

        Returns:
            float: The hue, between 0 and 1.

        """
        return self._h

    def set_h(self, value):
        """Sets the color's hue.

        Args:
            value (float): The hue value to set, between 0 and 1.

        """
        if value < 0:
            self._h = 0.0
        elif value > 1:
            self._h = 1.0
        else:
            self._h = value
            self._update_rgb()

    def get_s(self):
        """Gets the color's saturation.

        Returns:
            float: The saturation, between 0 and 1.

        """
        return self._s

    def set_s(self, value):
        """Sets the color's saturation.

        Args:
            value (float): The saturation value to set, between 0 and 1.

        """
        if value < 0:
            self._s = 0.0
        elif value > 1:
            self._s = 1.0
        else:
            self._s = value
            self._update_rgb()

    def get_l(self):
        """Gets the color's lightness.

        Returns:
            float: The lightness, between 0 and 1.

        """
        return self._l

    def set_l(self, value):
        """Sets the color's lightness.

        Args:
            value (float): The lightness, between 0 and 1.

        """
        if value < 0:
            self._l = 0.0
        elif value > 1:
            self._l = 1.0
        else:
            self._l = value
            self._update_rgb()

    def get_red_float(self):
        """Gets the color's red component.

        Returns:
            float: The red value, between 0 and 1.

        """
        return self._red_float

    def get_green_float(self):
        """Gets the color's green component.

        Returns:
            float: The green value, between 0 and 1.

        """
        return self._green_float

    def get_blue_float(self):
        """Gets the color's blue component.

        Returns:
            float: The blue value, between 0 and 1.

        """
        return self._blue_float

    def get_rgb_float(self):
        """Gets the RGB color value as float.

        Returns:
            tuple of float: red, green, blue (between 0 and 1).

        """
        return (self._red_float, self._green_float, self._blue_float)

    def get_rgb(self):
        """Gets the RGB color value as 16-bit color (0 - 65535).

        Returns:
            tuple of int: red, green, blue.

        """
        return (int(self._red_float * 65535), int(self._green_float * 65535), int(self._blue_float * 65535))

    ############################################################################
    # HslColor
    ############################################################################
    def to_gdk_color(self):
        """Converts the color to a Gdk.Color.

        TODO: Deprecated, need to use Gdk.RGBA

        Returns:
            Gdk.Color: The Gdk color object.

        """
        return Gdk.Color(*self.get_rgb_float())

    def _update_hsl(self, color):
        """Update the HSL representation of the color.

        Args:
            color: The RGB color.

        """
        r = color.red / float(65535)
        g = color.green / float(65535)
        b = color.blue / float(65535)

        v = max((r, g, b))
        m = min((r, g, b))

        self._l = (m + v) / 2.0

        if self._l <= 0.0:
            return

        vm = v - m
        self._s = vm

        if self._s > 0.0:
            if self._l <= 0.5:
                self._s = self._s / (v + m)
            else:
                self._s = self._s / (2.0 - v - m)
        else:
            return

        r2 = (v - r) / vm
        g2 = (v - g) / vm
        b2 = (v - b) / vm

        if r == v:
            if g == m:
                self._h = 5.0 + b2
            else:
                self._h = 1.0 - g2
        elif g == v:
            if b == m:
                self._h = 1.0 + r2
            else:
                self._h = 3.0 - b2
        else:
            if r == m:
                self._h = 3.0 + g2
            else:
                self._h = 5.0 - r2

        self._h = self._h / 6.0

    def _update_rgb(self):
        """Update RGB representation of the color.

        """
        if self._h > 1: self._h = 1
        if self._h < 0: self._h = 0
        if self._s > 1: self._s = 1
        if self._s < 0: self._s = 0
        if self._l > 1: self._l = 1
        if self._l < 0: self._l = 0

        if self._l == 0:
            self._red_float = self._green_float = self._blue_float = 0.0
        elif self._s == 0:
            self._red_float = self._green_float = self._blue_float = self._l
        else:
            if self._l <= 0.5:
                t2 = self._l * (1.0 + self._s)
            else:
                t2 = self._l + self._s - (self._l * self._s)

            t1 = 2.0 * self._l - t2

            t3 = [self._h + 1.0 / 3.0, self._h, self._h - 1.0 / 3.0]
            clr = [0.0, 0.0, 0.0]

            for i in range(3):
                if t3[i] < 0:
                    t3[i] += 1.0

                if t3[i] > 1:
                    t3[i] -= 1.0

                if 6.0 * t3[i] < 1.0:
                    clr[i] = t1 + (t2 - t1) * t3[i] * 6.0
                elif 2.0 * t3[i] < 1.0:
                    clr[i] = t2
                elif 3.0 * t3[i] < 2.0:
                    clr[i] = t1 + (t2 - t1) * ((2.0 / 3.0) - t3[i]) * 6.0
                else:
                    clr[i] = t1

            self._red_float = clr[0]
            self._green_float = clr[1]
            self._blue_float = clr[2]
