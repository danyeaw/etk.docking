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
from __future__ import division

from builtins import hex
from builtins import object
from builtins import range
from builtins import zip
from logging import getLogger

import gi
from past.utils import old_div

gi.require_version("Gtk", "3.0")
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk

from .dnd import DockDragContext
from .util import rect_overlaps
from .docksettings import settings

# The weight we allocate to a newly added item if we can't come up with anything else
FALLBACK_WEIGHT = 0.2


class _DockPanedHandle(object):
    """
    Private object storing information about a handle.
    """
    __slots__ = ['area']  # area, used for hit testing (Gdk.Rectangle)

    def __init__(self):
        self.area = Gdk.Rectangle()

    def __contains__(self, pos):
        return rect_overlaps(self.area, *pos)


class _DockPanedItem(object):
    """Private object storing information about a child widget.

    """
    __slots__ = ['child',  # child widget
                 'weight',  # relative weight [0..1]
                 'weight_request',  # requested weight, processed in size_allocate()
                 'min_size']  # minimum relative weight

    def __init__(self):
        self.weight = None
        self.weight_request = None
        self.min_size = None

    def __contains__(self, pos):
        return rect_overlaps(self.child.get_allocation(), *pos)


class DockPaned(Gtk.Container):
    """Container containing multiple horizontal or vertical panes.

    This widget is a container widget with multiple panes arranged either
    horizontally or vertically, depending on the value of the orientation
    property. Child widgets are added to the panes of the widget with the
    append_item, prepend_item, or insert_item methods.

    It draws a separator between its child widgets and a small handle that the
    user can drag to adjust the division. It does not draw any relief around
    the children or around the separator.

    """
    __gtype_name__ = 'EtkDockPaned'
    __gproperties__ = \
        {'handle-size':
             (GObject.TYPE_UINT,
              'handle size',
              'handle size',
              0,
              GLib.MAXINT,
              4,
              GObject.ParamFlags.READWRITE),
         'orientation':
             (GObject.TYPE_UINT,
              'orientation',
              'orientation',
              0,
              1,
              0,
              GObject.ParamFlags.READWRITE),
         'weight':
             (GObject.TYPE_FLOAT,
              'item weight',
              'item weight',
              0,  # min
              1,  # max
              .2,  # default
              GObject.ParamFlags.READWRITE)}
    __gsignals__ = {'item-added':
                        (GObject.SignalFlags.RUN_LAST,
                         None,
                         (GObject.TYPE_OBJECT,)),
                    'item-removed':
                        (GObject.SignalFlags.RUN_LAST,
                         None,
                         (GObject.TYPE_OBJECT,))}

    def __init__(self):
        Gtk.Container.__init__(self)

        # Initialize logging
        self.log = getLogger('%s.%s' % (self.__gtype_name__, hex(id(self))))

        # Initialize attributes
        self._items = []
        self._handles = []
        self._hcursor = None
        self._vcursor = None

        # Initialize handle dragging (not to be confused with DnD...)
        self._dragcontext = DockDragContext()

        # Initialize properties
        self.set_handle_size(4)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_weight(FALLBACK_WEIGHT)

    ############################################################################
    # Private
    ############################################################################
    def _children(self):
        """Yields an iterator of the items and handles in the DockPaned.

        Yields an iterator that returns the items and handles in the dockpaned
        in the order they are drawn. This corresponds to [_items[0],
        _handles[0], _items[1], _handles[1], _items[2], ...].

        Yields:
            object: The items and handles in the DockPaned

        """
        index = 0
        switch = True

        for x in range(len(self._items) + len(self._handles)):
            if switch:
                yield self._items[index]
                switch = False
            else:
                yield self._handles[index]
                switch = True
                index += 1

    def _insert_item(self, child, position=None, weight=None):
        """Inserts an item in the DockPaned.

        The private implementation behind the `add`, `insert_item`,
        `append_item`, and `prepend_item` methods.

        Args:
            child (Gtk.Widget): The child to use as the contents of the item.
            position (int): The index (starting at 0) at which to insert the
                item, negative or None to append the item after all the other
                items.
            weight (float): The relative amount of space the child should get,
                no guarantees.

        Returns:
            int: The index number of the item in the DockPaned.

        """
        assert isinstance(child, Gtk.Widget)
        assert self.item_num(child) is None
        assert not child.get_parent()

        if position is None or position < 0:
            position = len(self)

        # Create new _DockPanedItem
        item = _DockPanedItem()
        item.child = child
        item.child.set_parent(self)

        if self.get_realized():
            item.child.set_parent_window(self.window)

        self._items.insert(position, item)

        # Create a _DockPanedHandle if needed
        if len(self) > 1:
            self._insert_handle(position - 1)

        assert len(self._items) == len(self._handles) + 1

        if weight:
            assert 0.0 <= weight <= 1.0
            item.weight_request = weight
        elif len(self._items) == 1:
            # First item always gets 100% allocated
            item.weight = 1.0
        elif self.get_allocation() and child.get_allocation():
            size = self._effective_size(self.get_allocation()) - self._handle_size
            if self._orientation == Gtk.Orientation.HORIZONTAL:
                min_size, natural_size = child.get_preferred_width()
            else:
                min_size, natural_size = child.get_preferred_height()
            child_size = natural_size

            if size > 0 and child_size > 0:
                item.weight_request = old_div(float(child_size), size)
            else:
                item.weight_request = FALLBACK_WEIGHT
        else:
            item.weight_request = FALLBACK_WEIGHT

        self.queue_resize()
        self.emit('item-added', child)
        return self.item_num(child)

    def _remove_item(self, child):
        """Removes the child item from the DockPaned.

        The private implementation behind the `remove` and `remove_item`
        methods.

        Args:
            child (Gtk.Widget): The child to use as the contents of the item.

        """
        item_num = self.item_num(child)
        assert item_num is not None

        # Remove the DockPanedItem from the list
        child.unparent()
        del self._items[item_num]

        # If there are still items/handles in the list, we'd like to
        # remove a handle...
        if self._items:
            self._remove_handle(item_num)

        assert len(self._items) == len(self._handles) + 1 or \
               len(self._items) == len(self._handles) == 0

        self.queue_resize()
        self.emit('item-removed', child)

    def _insert_handle(self, position):
        """Insert a handle at the index specified by the position.

        Args:
            position (int): Index (starting at 0) of where to insert the
                handle.

        """
        handle = _DockPanedHandle()
        self._handles.insert(position, handle)

    def _remove_handle(self, position):
        """Remove a handle at the index specified by the position.

            position (int): Index (starting at 0) of where to remove the
                handle.

        """
        try:
            # Remove the DockPanedHandle that used to be located after
            # the DockPanedItem we just removed
            del self._handles[position]
        except IndexError:
            # Well, seems we removed the last DockPanedItem from the
            # list, so we'll remove the DockPanedHandle that used to
            # be located before the DockPanedItem we just removed
            del self._handles[position - 1]

    def _get_num_handles(self):
        """Returns the number of handles in the DockPaned.

        Returns:
            int: The number of handles.

        """
        return len(self._handles)

    def _get_handle_at_pos(self, x, y):
        """Returns the handle whose area contains the point.

        Args:
            x (int): The x position of the point.
            y (int): The y position of the point.

        Returns:
            object: The handle, or None if there is no handle at that position.

        """
        for handle in self._handles:
            if (x, y) in handle:
                return handle
        else:
            return None

    def _item_for_child(self, child):
        """Get the item associated with a child.

        Args:
            child: The child to look for as the child of an item.

        Returns:
            object: The item.

        """
        for item in self._items:
            if item.child is child:
                return item
        raise ValueError('child widget %s not in paned' % child)

    def _size(self, allocation):
        """Get the size (width or height), depending on the orientation.

        Args:
            allocation (Gdk.Rectangle): The rectangle to calculate the size
                from.

        Return:
            size (int): The width or height.

        """
        if self._orientation == Gtk.Orientation.HORIZONTAL:
            return allocation.width
        else:
            return allocation.height

    def _effective_size(self, allocation):
        """Find the size we can actually spend on items.

        The effective size is the size based on the orientation minus the
        size needed to be given to the handles.

        Args:
            allocation (Gdk.Rectangle): The rectangle to calculate the size
                from.

        """
        return self._size(allocation) - self._get_num_handles() * self._handle_size

    def _redistribute_size(self, delta_size, enlarge, shrink):
        """Shrink items and add the freed size to the enlarge item.

        Subtracts size from the items specified by `shrink` and adds the freed
        size to the item specified by `enlarge`. This is done until
        `delta_size` reaches 0, or there's no more items left in `shrink`.

        Args:
            delta_size (int): The size to add to the enlarge item.
            enlarge (_DockPanedItem): The item to add size to.
            shrink (list): The list of `_DockPanedItem`'s to take size from.

        """
        # Distribute delta_size amongst the items in shrink
        size = self._effective_size(self.allocation)
        enlarge_alloc = enlarge.child.allocation

        for item in shrink:

            available_size = self._size(item.child.allocation) - item.min_size

            # Check if we can shrink (respecting the child's size_request)
            if available_size > 0:
                a = item.child.allocation

                # Can we adjust the whole delta or not?
                if delta_size > available_size:
                    adjustment = available_size
                else:
                    adjustment = delta_size

                enlarge.weight_request = old_div(float(self._size(enlarge_alloc) + adjustment), size)
                item.weight_request = old_div(float(self._size(a) - adjustment), size)

                delta_size -= adjustment

            if delta_size == 0:
                break

        self.queue_resize()

    def _redistribute_weight(self, size):
        """Divide the space available over the items.

        Items that have explicitly been assigned a weight should get it
        assigned, as long as the max weight (1.0) is not exceeded.

        The general scheme is as follows:
        * figure out which items requested a new weight
        * ensure sum(min_sizes) fits in the allocated size
        * ensure the requested weights do not make items go smaller than min_size
        * divide remaining space over other items.

        Args:
            size (float): The size to distribute.

        """
        items = self._items
        size = float(size)

        # Scale non-expandable items, so their size does not change effectively
        allocation = self.get_allocation()
        if allocation:
            f = old_div(self._effective_size(allocation), size)
            for i in self._items:
                # if i.weight and not i.expand and not i.weight_request:
                if i.weight and not settings[i.child].expand and not i.weight_request:
                    i.weight_request = i.weight * f

        requested_items = [i for i in items if i.weight_request]
        other_items = [i for i in items if not i.weight_request]

        # Ensure the min_sizes do not exceed the overall size
        min_size = sum(i.min_size for i in items)

        if min_size > size:
            sf = old_div(size, min_size)
            self.log.warning('Size scaling required (factor=%f)' % sf)
        else:
            sf = 1.0

        # First ensure all remaining items can be placed
        for i, w in zip(other_items,
                        fair_scale(1.0 - sum(i.weight_request for i in requested_items), \
                                   [(i.weight, sf * i.min_size / size) for i in other_items])):
            i.weight = w

        # Divide what's left over the requesting items
        for i, w in zip(requested_items,
                        fair_scale(1.0 - sum(i.weight for i in other_items), \
                                   [(i.weight_request, sf * i.min_size / size) for i in requested_items])):
            i.weight = w
            i.weight_request = None

    ############################################################################

    def __getitem__(self, index):
        return self._items[index].child

    def __delitem__(self, index):
        child = self[index]
        self._remove_item(child)

    def __len__(self):
        return len(self._items)

    def __contains__(self, child):
        for i in self._items:
            if i.child is child:
                return True
        return False

    def __iter__(self):
        for i in self._items:
            yield i.child

    ############################################################################
    # GObject
    ############################################################################
    def do_get_property(self, pspec):
        """Gets the property value.

        Args:
            pspec (GObject.ParamSpec): A property of the DockPaned.

        Returns:
            The parameter value.

        """
        if pspec.name == 'handle-size':
            return self.get_handle_size()
        elif pspec.name == 'orientation':
            return self.get_orientation()
        elif pspec.name == 'weight':
            return self.get_weight()

    def do_set_property(self, pspec, value):
        """Sets the property value.

        Args:
            pspec (GObject.ParamSpec): A property of the DockPaned.
            value: The value to set.

        """
        if pspec.name == 'handle-size':
            self.set_handle_size(value)
        elif pspec.name == 'orientation':
            self.set_orientation(value)
        elif pspec.name == 'weight':
            self.set_weight(value)

    ############################################################################
    # GtkWidget
    ############################################################################
    def do_realize(self):
        """Creates the Gdk window resources for the DockPaned.

        """
        allocation = self.get_allocation()
        attr = Gdk.WindowAttr()
        attr.x = allocation.x
        attr.y = allocation.y
        attr.width = allocation.width
        attr.height = allocation.height
        attr.window_type = Gdk.WindowType.CHILD
        attr.wclass = Gdk.WindowWindowClass.INPUT_OUTPUT
        attr.event_mask = (Gdk.EventMask.EXPOSURE_MASK |
                           Gdk.EventMask.LEAVE_NOTIFY_MASK |
                           Gdk.EventMask.BUTTON_PRESS_MASK |
                           Gdk.EventMask.BUTTON_RELEASE_MASK |
                           Gdk.EventMask.POINTER_MOTION_MASK
                           )
        attr_mask = (Gdk.WindowAttributesType.X |
                     Gdk.WindowAttributesType.Y |
                     Gdk.WindowAttributesType.WMCLASS
                     )
        self.window = Gdk.Window(self.get_parent_window(), attr, attr_mask)
        self.window.set_user_data(self)
        # self.set_window(self.window)
        self.set_realized(True)

        # Set parent window on all child widgets
        for item in self._items:
            item.child.set_parent_window(self.window)

        # Initialize cursors
        self._hcursor = Gdk.Cursor.new_from_name(display=self.get_display(), name="ew-resize")
        self._vcursor = Gdk.Cursor.new_from_name(display=self.get_display(), name="ns-resize")

    def do_unrealize(self):
        """Clears the Gdk window resources for the DockPaned.

        """
        self._hcursor = None
        self._vcursor = None
        self.window.set_user_data(None)
        self.window.destroy()
        Gtk.Container.do_unrealize(self)

    def do_map(self):
        """Causes the DockPaned to be mapped if it isn’t already.

        """
        self.window.show()
        Gtk.Container.do_map(self)

    def do_unmap(self):
        """Causes the DockPaned to be unmapped if it is mapped.

        """
        self.window.hide()
        Gtk.Container.do_unmap(self)

    def do_get_request_mode(self):
        """Returns teh preferred container layout.

        Returns whether the container prefers a height-for-width or a
        width-for-height layout. DockPaned doesn't trade width for height or
        height for width so we return CONSTANT_SIZE.

        Returns:
            Gtk.SizeRequestMode: the constant size request mode.

        """
        return Gtk.SizeRequestMode.CONSTANT_SIZE

    def do_get_preferred_height(self):
        """Calculates the container's initial minimum and natural height.

        While this call is specific to width-for-height requests (that we requested
        not to get) we cannot be certain that our wishes are granted, so
        we must implement this method as well. Returns the the decoration area
        height.

        Returns:
             int: minimum height, natural height.

        """
        min_height = nat_height = 0

        # Add child widgets
        for item in self._items:
            item_min, item_nat = item.child.get_preferred_height()
            min_height += item_min
            nat_height += item_nat
            # Store the minimum weight for usage in do_size_allocate
            item.min_size = nat_height

        # Add handles
        min_height += self._get_num_handles() * self._handle_size
        nat_height += self._get_num_handles() * self._handle_size

        return min_height, nat_height

    def do_get_preferred_width(self):
        """Calculates the container's initial minimum and natural width.

        While this call is specific to width-for-height requests (that we
        requested not to get) we cannot be certain that our wishes are granted,
        so we must implement this method as well. Returns the decoration area
        width.

        Returns:
            int: minimum width, natural width

        """
        # Start with nothing
        min_width = nat_width = 0

        # Add child widgets
        for item in self._items:
            item_min, item_nat = item.child.get_preferred_width()
            min_width += item_min
            nat_width += item_nat
            # Store the minimum weight for usage in do_size_allocate
            item.min_size = item_nat

        # Add handles
        min_width += self._get_num_handles() * self._handle_size
        nat_width += self._get_num_handles() * self._handle_size

        return min_width, nat_width

    def do_get_preferred_height_for_width(self, width):
        """If given width, returns the minimum and natural height.

        Returns the container's minimum and natural height if given the
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

        Returns the container's minimum and natural width if given the
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
        """Assigns a size and position to the child widgets.

        Children may adjust the given allocation in the adjust_size_allocation
        virtual method. When a widget is resized (ie when the parent window is
        resized by the user), the do_get_preferred_size & do_size_allocate
        dance is typically executed multiple times with small changes (1 or 2
        pixels, sometimes more depending on the gdk backend used), instead of
        one pass with the complete delta. Distributing those small values
        evenly across multiple child widgets simply doesn't work very well. To
        overcome this problem, we assign a weight (can be translated to
        "factor") to each child.

        Args:
            allocation (Gdk.Rectangle): Position and size allocated.

        """
        if self._items:
            size = self._effective_size(allocation)

            self._redistribute_weight(size)

            cx = cy = 0  # current x and y counters
            handle_size = self._handle_size

            # Allocate child widgets: both items and handles, so we can simply increment
            for child in self._children():
                rect = Gdk.Rectangle()
                rect.x = cx
                rect.y = cy

                if isinstance(child, _DockPanedItem):
                    s = round(child.weight * size)

                    if self._orientation == Gtk.Orientation.HORIZONTAL:
                        rect.height = allocation.height
                        rect.width = s
                        cx += s

                        if child is self._items[-1]:
                            rect.width += allocation.width - cx
                    else:
                        rect.height = s
                        rect.width = allocation.width
                        cy += s

                        if child is self._items[-1]:
                            rect.height += allocation.height - cy

                    child.child.size_allocate(rect)

                elif isinstance(child, _DockPanedHandle):
                    if self._orientation == Gtk.Orientation.HORIZONTAL:
                        rect.height = allocation.height
                        rect.width = handle_size
                        cx += handle_size
                    else:
                        rect.height = handle_size
                        rect.width = allocation.width
                        cy += handle_size

                    child.area = rect

        # Accept new allocation
        self.allocation = allocation

        # Move/Resize our GdkWindow
        if self.get_realized():
            self.window.move_resize(x=allocation.x, y=allocation.y, width=allocation.width, height=allocation.height)

    def do_draw(self, cr):
        """Draws the container to the given Cairo context.

        The top left corner of the widget will be drawn to the currently set
        origin point of the context. The container needs to propagate the draw
        signal to its children.

        Args:
            cr (cairo.Context): The Cairo context to draw into

        """
        for item in self._items:
            self.propagate_draw(item.child, cr)

        for handle in self._handles:
            # TODO: render themed handle if not using compact layout
            pass

    def do_leave_notify_event(self, event):
        """Called when the pointer has entered the widget.

        Args:
            event (Gdk.EventCrossing): The event that is generated when the pointer leaves.

        Returns:
            True.

        """
        # Reset cursor
        self.window.set_cursor(None)

    def do_button_press_event(self, event):
        """Called when a pointer button is pressed.

        Sets the drag context source position and button equal to event if the
        event window is the DockPaned window and the button. We might start a
        DnD operation, or we could simply be starting a click on a tab. Store
        information from this event in self.dragcontext and decide in
        do_motion_notify_event if we're actually starting a DnD operation.

        Args:
            event (Gdk.EventButton): The event that triggered the signal

        Returns:
            bool: True to stop other handlers from being invoked for the event

        """
        if event.window is self.window and event.button == 1:
            handle = self._get_handle_at_pos(event.x, event.y)

            if handle:
                self._dragcontext.dragging = True
                self._dragcontext.dragged_object = handle
                self._dragcontext.source_button = event.button
                self._dragcontext.offset_x = event.x - handle.area.x
                self._dragcontext.offset_y = event.y - handle.area.y
                return True

        return False

    def do_button_release_event(self, event):
        """Called when a pointer button is released.

        On pointer button release, check if the user clicked on a tab, or right
        clicked to get a context menu. A special tab context menu is not
        currently implemented for right clicks on a tab, but this could be a
        potential enhancement in the future.

        Args:
            event (Gdk.EventButton): The event that triggered the signal

        Returns:
            bool: True to stop other handlers from being invoked for the event

        """
        # Reset drag context
        if event.button == self._dragcontext.source_button:
            self._dragcontext.reset()
            self.window.set_cursor(None)
            return True

        return False

    def do_motion_notify_event(self, event):
        """Called when the pointer moves over the DockPaned.

        When the motion notify event happens over a DockPaned, check if a DnD
        operation is in progress, and if so check if the user is dragging tabs
        in the DockPaned.

        Args:
            event (Gdk.EventMotion): The event that triggered the signal

        Returns:
            bool: True to stop other handlers from being invoked for the event

        """
        cursor = None

        # Set an appropriate cursor when the pointer is over a handle
        if self._get_handle_at_pos(event.x, event.y):
            if self._orientation == Gtk.Orientation.HORIZONTAL:
                cursor = self._hcursor
            else:
                cursor = self._vcursor

        # Drag a handle
        if self._dragcontext.dragging:
            if self._orientation == Gtk.Orientation.HORIZONTAL:
                cursor = self._hcursor
                delta_size = int(event.x -
                                 self._dragcontext.dragged_object.area.x -
                                 self._dragcontext.offset_x)
            else:
                cursor = self._vcursor
                delta_size = int(event.y -
                                 self._dragcontext.dragged_object.area.y -
                                 self._dragcontext.offset_y)

            handle_index = self._handles.index(self._dragcontext.dragged_object)
            item_after = self._items[handle_index + 1]

            if delta_size < 0:
                # Enlarge the item after and shrink the items before the handle
                delta_size = abs(delta_size)
                enlarge = item_after
                shrink = reversed(self._items[:self._items.index(item_after)])
                self._redistribute_size(delta_size, enlarge, shrink)
            elif delta_size > 0:
                # Enlarge the item before and shrink the items after the handle
                enlarge = self._items[handle_index]
                shrink = self._items[self._items.index(item_after):]
                self._redistribute_size(delta_size, enlarge, shrink)
            else:
                enlarge = None
                shrink = []

            self.queue_resize()

        # Set the cursor we decided upon above...
        if cursor:
            self.window.set_cursor(cursor)

    ############################################################################
    # GtkContainer
    ############################################################################
    def do_add(self, widget):
        """Called when the given widget is added to the DockPaned.

        Args:
            widget (Gtk.Widget): The widget to add

        """
        self._insert_item(widget)

    def do_remove(self, widget):
        """Called when the given widget is removed from the DockPaned.

        Args:
            widget (Gtk.Widget): The widget to remove

        """
        self._remove_item(widget)

    def do_forall(self, include_internals, callback, *callback_data):
        """Invokes the given callback on each item, with the given data.

        Args:
            include_internals (bool): Run on internal children
            callback (Gtk.Callback): The callback to call on each child
            callback_data (object or None): The parameters to pass to the
            callback

        """
        try:
            for item in self._items:
                callback(item.child, *callback_data)
        except AttributeError:
            pass

    ############################################################################
    # EtkDockPaned
    ############################################################################
    def get_handle_size(self):
        """Retrieves the size of the handles in the DockPaned.

        Returns:
            int: The size of the handles in the DockPaned.

        """
        return self._handle_size

    def set_handle_size(self, handle_size):
        """Sets the size for the handles in the DockPaned.

        Args:
            handle_size (int): The new size for the handles in the DockPaned.

        """
        self._handle_size = handle_size
        self.notify('handle-size')
        self.queue_resize()

    def get_orientation(self):
        """Retrieves the orientation of the DockPaned.

        Returns:
            Gtk.Orientation: The orientation of the DockPaned.

        """
        return self._orientation

    def set_orientation(self, orientation):
        """
        :param orientation: the DockPaned's new orientation.

        Sets the orientation of the DockPaned.

        Args:
            orientation:
        """
        self._orientation = orientation
        self.notify('orientation')
        self.queue_resize()

    def get_weight(self):
        """Get the weight of the DockPaned.

        Returns:
            float: The weight

        """
        return self.weight

    def set_weight(self, weight):
        """Set the weight of the DockPaned.

        Args:
            weight (float): The weight

        Returns:
            object:

        """
        self.weight = weight

    def append_item(self, child):
        """Appends an item to the DockPaned.

        Args:
            child (Gtk.Widget): The item to append.

        Returns:
            int: The index number of the item in the DockPaned.

        """
        return self._insert_item(child)

    def prepend_item(self, child):
        """Prepends an item to the DockPaned.

        Args:
            child (Gtk.Widget): The item to prepend.

        Returns:
            int: The index number of the item in the DockPaned.

        """
        return self._insert_item(child, 0)

    def insert_item(self, child, position=None, weight=None):
        """Insert an into the DockPaned.

        Inserts an item into the DockPaned at the location specified by
        position (0 is the first item). If position is None the item is
        appended to the DockGroup.

        Args:
            child (Gtk.Widget): The widget to use as the contents of the item.
            position (int): The index (0 start) at which to insert the item, or
                None to append the item after all other item tabs.
            weight (float): The relative amount of space the child should get.
                No guarentees.

        Returns:
            int: The index number of the item in the DockPaned.

        """
        return self._insert_item(child, position, weight)

    def remove_item(self, item_num):
        """Removes the item from the DockPaned.

        Removes the item at the location specified by item_num. The value of
        item_num starts from 0. If item_num is negative or None the last item
        of the DockPaned will be removed.

        Args:
            item_num(int): The index (starting from 0) of the item to remove.

        """
        if item_num is None or item_num < 0:
            child = self.get_nth_item(len(self) - 1)
        else:
            child = self.get_nth_item(item_num)

        self._remove_item(child)

    def item_num(self, child):
        """Returns the index of the item which contains the child widget.

        Returns the index of the item which contains the widget specified by
        child or None if no item contains the child.

        Args:
            child (Gtk.Widget): The child widget to get the index of.

        Returns:
            int: The index of the item containing the child.

        """
        try:
            return self.get_children().index(child)
        except ValueError:
            pass

    def get_nth_item(self, item_num):
        """Gets the child widget contained at the index.

        Returns the child widget contained at the index specified by item_num.
        If item_num is out of bounds for the item range of the DockPaned,
        returns None.

        Args:
            item_num (int): The index of an item in the DockPaned.

        Returns:
            Gtk.Widget: The child widget.

        """
        if item_num >= 0 and item_num <= len(self) - 1:
            return self._items[item_num].child
        else:
            return None

    def get_item_at_pos(self, x, y):
        """Gets the child widget at the position.

        Returns the child widget whose allocation contains the position
        specified by x and y or, None if no child widget is at that position.

        Args:
            x (int): the x coordinate of the position.
            y (int): the y coordinate of the position.

        Returns:
            Gtk.Widget the child widget at the position.

        """
        for item in self._items:
            if (x, y) in item:
                return item.child
        else:
            return None

    def reorder_item(self, child, position):
        """Reorders the DockPaned child widgets.

        Reorders the DockPaned child widgets so that the child appears in the
        location specified by location. If position is greater than equal to
        the number of children in the list or negative or None, child will be
        moved to the end of the list.

        Args:
            child (Gtk.Widget): The child widget to move.
            position (int): The index that the child is to move to.

        """
        item_num = self.item_num(child)
        assert item_num is not None

        if position is None or position < 0 or position > len(self) - 1:
            position = len(self)

        item = self._items[item_num]
        self._items.remove(item)
        self._items.insert(position, item)
        self.queue_resize()


def fair_scale(weight, wmpairs):
    """Fair scaling algorithm.

    A weight and a list of (weight, min_weight) pairs is provided. The result
    is a list of calculated weights that add up to weight, but are no smaller
    than their specified min_weight's.

    >>> fair_scale(.7, ((.3, .2), (.5, .1)))
    [0.26249999999999996, 0.43749999999999994]
    >>> fair_scale(.5, ((.3, .2), (.5, .1)))
    [0.2, 0.3]
    >>> fair_scale(.4, ((.3, .2), (.5, .1)))
    [0.2, 0.2]

    Args:
        weight (float): The relative amount of space the child should get.
        wmpairs (list): List of (weight, min_weight) pairs.

    Returns:
        list: List of calculated weights.

    """
    # List of new weights
    n = [0] * len(wmpairs)
    # Values that have been assigned their min_weight end up in this list:
    skip = [False] * len(wmpairs)
    while True:
        try:
            f = old_div(weight, sum(a[0] for a, s in zip(wmpairs, skip) if not s))
        except ZeroDivisionError:
            f = 0
        for i, (w, m) in enumerate(wmpairs):
            if skip[i]:
                continue
            n[i] = w * f
            if n[i] < m:
                n[i] = m
                weight -= m
                skip[i] = True
                break
        else:
            break  # quit while loop
    return n
