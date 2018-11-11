import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Dict, List, Union

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

DEFAULT_PAGE_NAME = 'Untitled Page'


class StructureComponent(ABC):
    """ Base class for notebook components containing methods that must be implemented
    """

    # global condition variable used to prevent concurrent component creation and _id overlap
    _component_create = threading.Condition(lock=threading.RLock())
    # global static identifier for new components
    _component_count = 0

    def __init__(self):
        """ Constructor
        """
        # GMT Unix time at which the page was created
        self.creation_time: int = time.time()
        StructureComponent._component_create.acquire()
        # unique ID to use as constant time reference to this page
        self.id: int = StructureComponent._component_count
        StructureComponent._component_count += 1
        StructureComponent._component_create.release()
        self.parent: StructureComponent = None

    def unroll_path(self) -> List[int]:
        """
        Unrolls the path from a page back to its root
        :return: The full path to the requested structure component in the order of root -> self
        """
        return [self.id]

    @abstractmethod
    def add_page(self, text_buffer: Gtk.TextBuffer, title: str = None) -> 'Page':
        pass

    @abstractmethod
    def remove(self, child_id: int):
        pass

    @abstractmethod
    def all_children(self) -> List[int]:
        pass


class Page(StructureComponent):
    """
    Represents a page in this notebook
    Recursive structure that maintains a list of all sub-pages beneath it
    Unfolding the hierarchy of pages should be done depth-first
    """

    def __init__(self, parent, text_buffer: Gtk.TextBuffer, title: str = 'Untitled Page'):
        """ Constructor
        :param title: The title of this new Page
        """
        super().__init__()
        # List of sub-pages owned by this page organized as {_id: Page}
        self.sub_pages: Dict[int, Page] = OrderedDict()
        # Pointer to the parent of this page
        self.parent: Union[Page, Tab] = parent
        # Title of this page
        self.title = title
        # The text buffer holding the text contents of the page
        self.text_buffer: Gtk.TextBuffer = text_buffer

    def is_leaf(self) -> bool:
        """ Tells if this page has any sub-pages
        :return: True if this page has no sub-pages, False otherwise
        """
        return len(self.sub_pages) == 0

    def is_root_page(self) -> bool:
        """ Tells if this page is a top-level page (no parent)
        :return: True if this page's parent is a Tab, False otherwise
        """
        return type(self.parent) is Tab

    def set_title(self, title: str) -> bool:
        """
        Sets a new title for this Page
        :param title: The new title
        :return: True if the title was changed, false otherwise
        """
        changed = title == self.title
        self.title = title
        return changed

    def unroll_path(self) -> List[int]:
        return [self.id] + self.parent.unroll_path()

    def add_page(self, text_buffer: Gtk.TextBuffer, title: str = DEFAULT_PAGE_NAME) -> 'Page':
        """ Creates a new sub-page, with this page as a parent
        :param text_buffer: The TextBuffer associated with this page
        :param title: The title of the new page
        :return: The new page created
        """
        page = Page(self, title)
        if title is not None:
            page.set_title(title)
        self.sub_pages[page.id] = page
        return page

    def remove(self, child_id: int):
        """ Removes a sub-page from the structure
        :except ValueError: If the given id is not a child of this Page
        """
        if child_id not in self.sub_pages:
            raise ValueError(f"Component with ID {child_id} is not a member of page with ID {self.id}")
        del self.sub_pages[child_id]

    def all_children(self) -> List[int]:
        """ Returns a depth-first accumulated list of all nested children for this Page
        :return: A list of of all child IDs of this Page
        """
        accumulator = []
        for child_id in self.sub_pages:
            accumulator.append(child_id)
            accumulator += self.sub_pages[child_id].all_children()
        return accumulator


class Tab(StructureComponent):
    """
    Represents one tab of this notebook.
    Maintains a list of top-level pages, each of which may manage infinite sub-pages
    """

    def __init__(self, name: str):
        """ Constructor
        :param name: The name of this new Tab
        """
        super().__init__()
        # name of this tab
        self.name: str = name
        # dict of all top-level pages as {_id: Page}
        self.pages: Dict[int, Page] = OrderedDict()

    def add_page(self, text_buffer: Gtk.TextBuffer, title: str = DEFAULT_PAGE_NAME) -> Page:
        """ Adds a new page under this Tab
        :param text_buffer: The TextBuffer associated with this page
        :param title: The title of the new page
        :return: The new page created
        """
        new_page = Page(self, text_buffer, title)
        self.pages[new_page.id] = new_page
        return new_page

    def set_name(self, name: str) -> bool:
        """ Sets the name of this Tab to a new name
        :param name:
        :return:
        """
        changed = self.name == name
        self.name = name
        return changed

    def remove(self, child_id: int):
        """ Removes a child page from the structure
        :param child_id: The ID of the child to remove
        """
        if child_id not in self.pages:
            raise ValueError(f"Page with ID {child_id} not a member of Tab with ID {self.id}")
        del self.pages[child_id]

    def all_children(self) -> List[int]:
        """ Returns a depth-first accumulated list of all nested children for this Tab
        :return: A list of of all child IDs of this Tab
        """
        accumulator = []
        for child_id in self.pages:
            accumulator.append(child_id)
            accumulator += self.pages[child_id].all_children()
        return accumulator


class StructureManager:
    """
    Manages document structure for a notebook
    Notebooks are organized with top-level categories known as "tabs," and each tab contains a series of
    pages, each of which may contain infinite sub-pages
    TODO support remove parent pages without deleting children (giving them a new parent?)
    """

    def __init__(self, path: str):
        """ Constructor
        """
        # number of total tabs created (used for naming untitled tabs)
        self._total_tabs = 0
        # dict that associates IDs with components
        self.components: Dict[int, StructureComponent] = {}
        # path is a string that stores the root of the notebook in the filesystem
        self.path = path

    def new_tab(self, name: str = None) -> Tab:
        """ Creates a new Tab in this notebook
        :param name: The name of the new Tab
        :return: The new Tab created
        """
        self._total_tabs += 1
        tab = Tab(name if name is not None else "Tab " + str(self._total_tabs))
        self.components[tab.id] = tab
        return tab

    def new_page(self, parent: StructureComponent, text_buffer: Gtk.TextBuffer, title: str = DEFAULT_PAGE_NAME) -> Page:
        """
        Creates a new page at the specified path
        :param text_buffer: The TextBuffer associated with the new page
        :param parent: The component under which to add the new page
        :param title: The title of the new page
        :except ValueError: if the structure has no tabs, or the given parent is not in the structure
        :return: The new page that was created
        """
        if len(self.components) == 0:
            raise ValueError("Cannot insert pages if no tabs exist")
        if parent.id not in self:
            raise ValueError(f"Cannot insert pages as child of component not in structure. Parent ID: {parent.id}")
        page = parent.add_page(text_buffer, title)
        self.components[page.id] = page
        return page

    def remove_component(self, _id):
        """ Removes a component from the structure
        :param _id: The ID of the component to be removed
        :except KeyError: If there is no component associated with _id
        """
        component = self.get_component(_id)
        if component.parent is not None:
            component.parent.remove(_id)
        for child_id in self.components[_id].all_children():
            del self.components[child_id]
        del self.components[_id]

    def get_component(self, _id: int) -> StructureComponent:
        """
        Searches for a component by _id number
        :param _id: The _id to search for
        :except KeyError: If _id is not associated with some component in the structure
        :return: The component associated with the given _id
        """
        if _id not in self.components:
            raise KeyError(f"No component found with ID {_id}")
        return self.components[_id]

    def __contains__(self, _id: int) -> bool:
        """ Tells if a component is in this structure (by ID)
        :param _id: The _id of the component to look up
        :return: True if the component is in this structure, False otherwise
        """
        return _id in self.components
