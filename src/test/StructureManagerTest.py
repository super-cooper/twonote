import os
import shutil
import unittest

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from storage.StructureManager import *

TEST_PATH = '/tmp/TestNotebook/'


class StructureManagerTest(unittest.TestCase):
    """ Unit tests for StructureManager
    """

    def setUp(self):
        self.structure_manager = StructureManager(TEST_PATH)

    def tearDown(self):
        if os.path.exists(TEST_PATH):
            shutil.rmtree(TEST_PATH)

    def test_new_tab(self):
        tab = self.structure_manager.new_tab('Test Tab')
        self.assertEqual(1, len(self.structure_manager.components), "Incorrect number of tabs inserted")
        self.assertEqual(tab.name, 'Test Tab', "Created tab does not have correct name")
        tab = self.structure_manager.new_tab()
        self.assertEqual(2, len(self.structure_manager.components), "Incorrect number of tabs or pages inserted")
        self.assertEqual("Tab " + str(self.structure_manager._total_tabs), tab.name, "Default tab name incorrect")

    def test_new_page_error(self):
        with self.assertRaises(ValueError, msg="ValueError not raised with invalid page creation"):
            tab1 = self.structure_manager.new_tab()
            tab2 = self.structure_manager.new_tab()
            self.structure_manager.remove_component(tab1.id)
            self.structure_manager.new_page(tab1, Gtk.TextBuffer())
            self.structure_manager.remove_component(tab2.id)
            self.structure_manager.new_page(tab1, Gtk.TextBuffer())

    def test_new_page(self):
        tab = self.structure_manager.new_tab('Test')
        page = self.structure_manager.new_page(tab, Gtk.TextBuffer())
        self.assertEqual([page.id, tab.id], self.structure_manager.unroll_path(page.id), "Initial new page incorrect")
        self.assertEqual(DEFAULT_PAGE_NAME, page.title, "Default page title incorrect")
        self.assertTrue(page.is_leaf(), "First page is not leaf")
        sub_page = self.structure_manager.new_page(page, Gtk.TextBuffer())
        self.assertEqual([sub_page.id, page.id, tab.id], self.structure_manager.unroll_path(sub_page.id),
                         "Document structure of sub-page not formed correctly")

    def test_remove_component(self):
        tab1 = self.structure_manager.new_tab()
        tab2 = self.structure_manager.new_tab()
        page1 = self.structure_manager.new_page(tab1, Gtk.TextBuffer())
        page2 = self.structure_manager.new_page(tab2, Gtk.TextBuffer())
        self.structure_manager.remove_component(page1.id)
        self.assertTrue(page1.id not in self.structure_manager, "Remove of single page unsuccessful")
        self.assertTrue(page1.id not in tab1.pages, "Remove of page from tab unsuccessful")
        self.structure_manager.remove_component(tab2.id)
        self.assertTrue(page2.id not in self.structure_manager,
                        "Nested remove of page does not affect StructureManager")
        self.assertTrue(tab2.id not in self.structure_manager, "Remove of tab does not affect StructureManager")

    def test_eq(self):
        _copy = copy.deepcopy(self.structure_manager)
        self.assertTrue(_copy == self.structure_manager, "Copied empty StructureManager is not equal")
        tab = self.structure_manager.new_tab()
        page = self.structure_manager.new_page(tab, Gtk.TextBuffer())
        _copy = copy.deepcopy(self.structure_manager)
        self.assertTrue(_copy == self.structure_manager, "Copied StructureManager is not equal")
        sm1 = StructureManager(TEST_PATH)
        self.assertTrue(sm1 != self.structure_manager, "Empty StructureManager is equal to non-empty StructureManager")
        self.assertTrue(StructureManager(TEST_PATH) != StructureManager(TEST_PATH + 'a'),
                        "StructureManagers with different paths considered equal")
        _copy.new_page(page, Gtk.TextBuffer())
        self.assertTrue(self.structure_manager != _copy, "Different populated StructureManagers considered equal")
