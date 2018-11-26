import copy
import pickle
import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Dict, List

DEFAULT_PAGE_NAME = 'Untitled Page'
ID_FILE_NAME = 'id'


class StructureComponent(ABC):
    """ Base class for notebook components containing methods that must be implemented
    """

    # global condition variable used to prevent concurrent component creation and _id overlap
    _component_create = threading.Condition(lock=threading.RLock())

    def __init__(self, _id: int):
        """ Constructor
        """
        # GMT Unix time at which the page was created
        self.creation_time: int = time.time()
        # unique ID to use as constant time reference to this page
        self.id: int = _id
        self.parent: int = None

    @abstractmethod
    def add_page(self, text_buffer: str, _id: int, title: str = None) -> 'Page':
        pass

    @abstractmethod
    def remove(self, child_id: int):
        pass

    @abstractmethod
    def all_children(self) -> List[int]:
        pass

    @abstractmethod
    def __eq__(self, other: 'StructureComponent') -> bool:
        pass


class Page(StructureComponent):
    """
    Represents a page in this notebook
    Recursive structure that maintains a list of all sub-pages beneath it
    Unfolding the hierarchy of pages should be done depth-first
    """

    def __init__(self, parent: int, text_buffer: str, _id: int, title: str = 'Untitled Page'):
        """ Constructor
        :param title: The title of this new Page
        """
        super().__init__(_id)
        # List of sub-pages owned by this page organized as {_id: Page}
        self.sub_pages: Dict[int, Page] = OrderedDict()
        # Pointer to the parent of this page
        self.parent: int = parent
        # Title of this page
        self.title = title
        # The text buffer holding the text contents of the page
        self.text_buffer: str = text_buffer

    def is_leaf(self) -> bool:
        """ Tells if this page has any sub-pages
        :return: True if this page has no sub-pages, False otherwise
        """
        return len(self.sub_pages) == 0

    def set_title(self, title: str) -> bool:
        """
        Sets a new title for this Page
        :param title: The new title
        :return: True if the title was changed, false otherwise
        """
        changed = title == self.title
        self.title = title
        return changed

    def add_page(self, text_buffer: str, _id: int, title: str = DEFAULT_PAGE_NAME) -> 'Page':
        """ Creates a new sub-page, with this page as a parent
        :param _id: The ID of the new page
        :param text_buffer: The TextBuffer associated with this page
        :param title: The title of the new page
        :return: The new page created
        """
        page = Page(self.id, text_buffer, _id, title)
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

    def __eq__(self, other: 'Page') -> bool:
        """ Tells if this Page is equal to another in attributes and structure
        :param other: The other Page to compare
        :return: True if the Pages are equal, False otherwise
        """
        if type(self) is not type(other) or len(self.sub_pages) != len(other.sub_pages):
            return False
        for attr1, attr2 in zip([self.id, self.title, self.text_buffer] + self.all_children(),
                                [other.id, other.title, self.text_buffer] + other.all_children()):
            if attr1 != attr2:
                return False
        return True

    def __deepcopy__(self, memodict=None) -> 'Page':
        new_page = Page(self.parent, self.text_buffer, self.id, self.title)
        old_time = self.creation_time
        items = vars(self).items()
        for attr, val in items:
            if attr != 'parent':
                new_page.__setattr__(attr, copy.deepcopy(val))
        new_page.creation_time = old_time
        return new_page

    def set_text(self, text: str) -> bool:
        """ Sets the text of this Page's text_buffer
        :param text: The text to set
        :return: True if buffer was changed, false otherwise
        """
        no_change = self.text_buffer == text
        self.text_buffer = text
        return no_change


class Tab(StructureComponent):
    """
    Represents one tab of this notebook.
    Maintains a list of top-level pages, each of which may manage infinite sub-pages
    """

    def __init__(self, name: str, _id: int):
        """ Constructor
        :param name: The name of this new Tab
        """
        super().__init__(_id)
        # name of this tab
        self.name: str = name
        # dict of all top-level pages as {_id: Page}
        self.pages: Dict[int, Page] = OrderedDict()

    def add_page(self, text_buffer: str, _id: int, title: str = DEFAULT_PAGE_NAME) -> Page:
        """ Adds a new page under this Tab
        :param _id: The ID of the new page
        :param text_buffer: The TextBuffer associated with this page
        :param title: The title of the new page
        :return: The new page created
        """
        new_page = Page(self.id, text_buffer, _id, title)
        self.pages[new_page.id] = new_page
        return new_page

    def set_name(self, name: str) -> bool:
        """ Sets the name of this Tab to a new name
        :param name:
        :return: True if the name was changed, False otherwise
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

    def __eq__(self, other: 'Tab') -> bool:
        """ Tells if a Tab is equal to another by attributes and structure
        :param other: The other Tab to compare
        :return: True if these Tabs are equal, False otherwise
        """
        if type(self) is not type(other) or len(self.pages) != len(other.pages):
            return False
        for attr1, attr2 in zip([self.name, self.id] + self.all_children(),
                                [other.name, other.id] + other.all_children()):
            if attr1 != attr2:
                return False
        return True


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
        self.components: Dict[int, StructureComponent] = OrderedDict()
        # path is a string that stores the root of the notebook in the filesystem
        self.path = path
        # identifier for new components
        self._component_count = 0

    def new_tab(self, name: str = None) -> Tab:
        """ Creates a new Tab in this notebook
        :param name: The name of the new Tab
        :return: The new Tab created
        """
        self._total_tabs += 1
        StructureComponent._component_create.acquire()
        tab = Tab(name if name is not None else "Tab " + str(self._total_tabs), self._component_count)
        self._component_count += 1
        StructureComponent._component_create.release()
        self.components[tab.id] = tab
        return tab

    def new_page(self, parent: StructureComponent, text_buffer: str, title: str = DEFAULT_PAGE_NAME) -> Page:
        """ Creates a new page at the specified path
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
        StructureComponent._component_create.acquire()
        page = parent.add_page(text_buffer, self._component_count, title)
        self._component_count += 1
        StructureComponent._component_create.release()
        self.components[page.id] = page
        return page

    def remove_component(self, _id):
        """ Removes a component from the structure
        :param _id: The ID of the component to be removed
        :except KeyError: If there is no component associated with _id
        """
        component = self.get_component(_id)
        if component.parent is not None:
            self.get_component(component.parent).remove(_id)
        for child_id in self.components[_id].all_children():
            del self.components[child_id]
        del self.components[_id]

    def get_component(self, _id: int) -> StructureComponent:
        """ Searches for a component by _id number
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

    def __eq__(self, other: 'StructureManager') -> bool:
        """ Tells if this StructureManager is equal internally to another
        Compares all contained components for equality, very inefficient
        TODO Find more decidable way to implement this
        :param other: The other StructureManager to compare to
        :return: True if all fields of this and other are equal
        """
        return len(self.components) == len(other.components) and all(
            self.get_component(id1) == other.get_component(id2) for id1, id2 in
            zip(self.components.keys(), other.components.keys())) and self.path == other.path

    def unroll_path(self, _id: int) -> List[int]:
        """ Unrolls the path of a component
        :param _id: The id of the component
        :return: The path from component to root
        """
        comp = self.get_component(_id)
        path = [comp.id]
        while type(comp) is not Tab:
            comp = self.get_component(comp.parent)
            path.append(comp.id)
        return path

    def save(self) -> bool:
        """ Saves this StructureManager to disk
        :return: Result of call to StructureManager.persist(self, self.path)
        """
        return StructureManager.persist(self, self.path)

    @staticmethod
    def persist(structure_manager: 'StructureManager', f_name: str) -> bool:
        """ Persists this StructureManager to disk using a Pickler
        :param structure_manager: The StructureManager to persist
        :param f_name: The name of the file to be saved
        :return: True if successfully persisted, False otherwise
        """
        if f_name == ID_FILE_NAME:
            f_name += '-notebook'
        if not f_name.endswith('.tnb'):
            f_name += '.tnb'
        _copy = copy.deepcopy(structure_manager)
        with open(f_name, 'wb') as file:
            pickle.dump(_copy, file)
        with open('id', 'wb') as file:
            pickle.dump(structure_manager._component_count, file)
        return True

    @staticmethod
    def load_from_disk(path: str) -> 'StructureManager':
        """ Loads a StructureManager from a pickle file
        :param path: The path of the pickle file to load from
        :raise TypeError: If the given pickle file does not represent a StructureManager
        :return: A StructureManager restored from the pickle file
        """
        with open(path, 'rb') as file:
            sm = pickle.load(file)
        with open(ID_FILE_NAME, 'rb') as file:
            sm._component_count = int(pickle.load(file))
        if type(sm) is not StructureManager:
            raise TypeError(f"Loaded file {path} is not a StructureManager!")
        return sm
