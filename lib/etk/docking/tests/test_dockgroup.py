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


import unittest

import gtk
from etk.docking import DockItem, DockGroup


class TestDockGroup(unittest.TestCase):
    ############################################################################
    # Test properties
    ############################################################################
    def test_prop_group_id(self):
        global notify_called

        def _on_notify(gobject, pspec):
            global notify_called
            notify_called = True

        dockgroup = DockGroup()
        dockgroup.connect('notify::group-id', _on_notify)

        notify_called = False
        dockgroup.set_group_id(1)
        self.assertEquals(dockgroup.get_group_id(), 1,
                          msg='get_group_id method did not return expected value')
        self.assertTrue(notify_called,
                        msg='group-id property change notification failed when using set_group_id method')

        notify_called = False
        dockgroup.set_property('group-id', 2)
        self.assertEquals(dockgroup.get_property('group-id'), 2,
                          msg='get_property method did not return expected value')
        self.assertTrue(notify_called,
                        msg='group-id property change notification failed when using set_property method')

        notify_called = False
        dockgroup.props.group_id = 3
        self.assertEquals(dockgroup.props.group_id, 3,
                          msg='.props attribute did not return expected value')
        self.assertTrue(notify_called,
                        msg='group-id property change notification failed when using .props attribute')

        dockgroup.destroy()

    ############################################################################
    # Test public api
    ############################################################################
    def test_add(self):
        dockitem = DockItem()
        dockgroup = DockGroup()
        dockgroup.add(dockitem)

        self.assertTrue(dockitem in dockgroup)

        dockitem.destroy()
        dockgroup.destroy()

    def test_remove(self):
        dockitem = DockItem()
        dockgroup = DockGroup()
        dockgroup.add(dockitem)
        dockgroup.remove(dockitem)

        self.assertTrue(dockitem not in dockgroup)

        dockitem.destroy()
        dockgroup.destroy()

    def test_append_item(self):
        dockitem = DockItem()
        dockgroup = DockGroup()
        index = dockgroup.append_item(dockitem)

        self.assertTrue(index == 0)
        self.assertTrue(dockgroup.get_nth_item(0) is dockitem)

        dockitem.destroy()
        dockgroup.destroy()

    def test_prepend_item(self):
        dockitem1 = DockItem()
        dockitem2 = DockItem()
        dockgroup = DockGroup()
        index1 = dockgroup.append_item(dockitem1)
        index2 = dockgroup.prepend_item(dockitem2)

        self.assertTrue(index1 == 0)
        self.assertTrue(index2 == 0)
        self.assertTrue(dockgroup.get_nth_item(0) is dockitem2)
        self.assertTrue(dockgroup.get_nth_item(1) is dockitem1)

        dockitem1.destroy()
        dockitem2.destroy()
        dockgroup.destroy()

    def test_insert_item(self):
        dockitem1 = DockItem()
        dockitem2 = DockItem()
        dockitem3 = DockItem()
        dockgroup = DockGroup()
        dockgroup.insert_item(dockitem1, None)
        dockgroup.insert_item(dockitem2, 0)
        dockgroup.insert_item(dockitem3, 1)

        self.assertTrue(dockgroup.get_nth_item(0) is dockitem2)
        self.assertTrue(dockgroup.get_nth_item(1) is dockitem3)
        self.assertTrue(dockgroup.get_nth_item(2) is dockitem1)

        dockitem1.destroy()
        dockitem2.destroy()
        dockitem3.destroy()
        dockgroup.destroy()

    def test_remove_item(self):
        dockitem1 = DockItem()
        dockitem2 = DockItem()
        dockgroup = DockGroup()
        dockgroup.add(dockitem1)
        dockgroup.add(dockitem2)
        dockgroup.remove_item(0)
        dockgroup.remove_item(None)

        self.assertTrue(dockitem1 not in dockgroup)
        self.assertTrue(dockitem2 not in dockgroup)

        dockitem1.destroy()
        dockitem2.destroy()
        dockgroup.destroy()

    def test_item_num(self):
        dockitem1 = DockItem()
        dockitem2 = DockItem()
        dockgroup = DockGroup()
        dockgroup.add(dockitem1)

        self.assertTrue(dockgroup.item_num(dockitem1) == 0)
        self.assertTrue(dockgroup.item_num(dockitem2) is None)

        dockitem1.destroy()
        dockgroup.destroy()

    def test_get_n_items(self):
        dockgroup = DockGroup()
        self.assertTrue(dockgroup.get_n_items() == 0)

        dockitem = DockItem()
        dockgroup.add(dockitem)
        self.assertTrue(dockgroup.get_n_items() == 1)

        dockitem.destroy()
        dockgroup.destroy()

    def test_get_nth_item(self):
        dockitem1 = DockItem()
        dockitem2 = DockItem()
        dockgroup = DockGroup()
        dockgroup.add(dockitem1)
        dockgroup.add(dockitem2)

        self.assertTrue(dockgroup.get_nth_item(0) is dockitem1)
        self.assertTrue(dockgroup.get_nth_item(1) is dockitem2)
        self.assertTrue(dockgroup.get_nth_item(2) is None)
        self.assertTrue(dockgroup.get_nth_item(-1) is None)

        dockitem1.destroy()
        dockitem2.destroy()
        dockgroup.destroy()

    def test_get_current_item(self):
        dockitem = DockItem()
        dockgroup = DockGroup()
        self.assertTrue(dockgroup.get_current_item() is None)

        index = dockgroup.append_item(dockitem)
        self.assertTrue(dockgroup.get_current_item() == index)

        dockgroup.remove(dockitem)
        self.assertTrue(dockgroup.get_current_item() is None)

        dockitem.destroy()
        dockgroup.destroy()

    def test_set_current_item(self):
        dockitem1 = DockItem()
        dockitem2 = DockItem()
        dockgroup = DockGroup()
        self.assertTrue(dockgroup.get_current_item() is None)

        index = dockgroup.append_item(dockitem1)
        self.assertTrue(dockgroup.get_current_item() == index)

        index = dockgroup.append_item(dockitem2)
        self.assertTrue(dockgroup.get_current_item() == index)

        dockgroup.set_current_item(0)
        self.assertTrue(dockgroup.get_current_item() == 0)

        dockgroup.set_current_item(dockgroup.get_n_items() + 10)
        self.assertTrue(dockgroup.get_current_item() == dockgroup.get_n_items() - 1)

        dockgroup.set_current_item(-1)
        self.assertTrue(dockgroup.get_current_item() == 0)

        dockitem1.destroy()
        dockitem2.destroy()
        dockgroup.destroy()

    def test_next_item(self):
        dockitem1 = DockItem()
        dockitem2 = DockItem()
        dockgroup = DockGroup()
        dockgroup.add(dockitem1)
        dockgroup.add(dockitem2)
        dockgroup.set_current_item(0)
        self.assertTrue(dockgroup.get_current_item() == 0)

        dockgroup.next_item()
        self.assertTrue(dockgroup.get_current_item() == 1)

        dockgroup.next_item()
        self.assertTrue(dockgroup.get_current_item() == 1)

        dockitem1.destroy()
        dockitem2.destroy()
        dockgroup.destroy()

    def test_prev_item(self):
        dockitem1 = DockItem()
        dockitem2 = DockItem()
        dockgroup = DockGroup()
        dockgroup.add(dockitem1)
        dockgroup.add(dockitem2)
        self.assertTrue(dockgroup.get_current_item() == 1)

        dockgroup.prev_item()
        self.assertTrue(dockgroup.get_current_item() == 0)

        dockgroup.prev_item()
        self.assertTrue(dockgroup.get_current_item() == 0)

        dockitem1.destroy()
        dockitem2.destroy()
        dockgroup.destroy()

    def test_reorder_item(self):
        dockitem1 = DockItem()
        dockitem2 = DockItem()
        dockitem3 = DockItem()
        dockgroup = DockGroup()
        dockgroup.add(dockitem1)
        dockgroup.add(dockitem2)
        dockgroup.add(dockitem3)
        dockgroup.reorder_item(dockitem3, 0)
        dockgroup.reorder_item(dockitem1, 2)

        self.assertTrue(dockgroup.item_num(dockitem1) == 2)
        self.assertTrue(dockgroup.item_num(dockitem2) == 1)
        self.assertTrue(dockgroup.item_num(dockitem3) == 0)

        dockitem1.destroy()
        dockitem2.destroy()
        dockitem3.destroy()
        dockgroup.destroy()

    def test_drag_begin(self):
        dockitem1 = DockItem()
        dockitem2 = DockItem()
        dockitem3 = DockItem()
        dockgroup = DockGroup()
        dockgroup.add(dockitem1)
        dockgroup.add(dockitem2)
        dockgroup.add(dockitem3)

        window = gtk.Window()
        window.add(dockgroup)
        window.set_size_request(200, 200)

        self.assertEquals(dockitem3, dockgroup._current_tab.item)


