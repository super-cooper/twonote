import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Dict, List, Union


class StructureComponent(ABC):
    """ Base class for notebook components containing methods that must be implemented
    """

    # global condition variable used to prevent concurrent component creation and _id overlap
    component_create = threading.Condition(lock=threading.RLock())

    def __init__(self):
        """ Constructor
        """
        StructureComponent.component_create.acquire()
        # GMT Unix time at which the page was created
        self.creation_time: int = time.time()
        # Current REALLY shitty solution to prevent page ID collision TODO replace this
        time.sleep(1)
        StructureComponent.component_create.release()
        # unique ID to use as constant time reference to this page
        self._id: int = self.creation_time

    def unroll_path(self) -> List[int]:
        """
        Unrolls the path from a page back to its root
        :return: The full path to the requested structure component in the order of root -> self
        """
        return [self._id]

    @abstractmethod
    def add_page(self, title: str=None) -> 'Page':
        pass


class Page(StructureComponent):
    """
    Represents a page in this notebook
    Recursive structure that maintains a list of all sub-pages beneath it
    Unfolding the hierarchy of pages should be done depth-first
    """

    def __init__(self, parent, title: str = 'Untitled Page'):
        """ Constructor
        :param title: The title of this new Page
        """
        super().__init__()
        # List of sub-pages owned by this page organized as {_id: Page}
        self.sub_pages: Dict[int, Page] = OrderedDict()
        # Pointer to the parent of this page
        self.parent: Union[Page, Tab] = parent
        self.title = title

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
        return [self._id] + self.parent.unroll_path()

    def add_page(self, title: str=None) -> 'Page':
        """ Creates a new sub-page, with this page as a parent
        :param title: The title of the new page
        :return: The new page created
        """
        page = Page(self)
        if title is not None:
            page.set_title(title)
        return page


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

    def add_page(self, title: str=None) -> Page:
        """ Adds a new page under this Tab
        :param title: The title of the new page
        :return: The new page created
        """
        new_page = Page(parent=self)
        self.pages[new_page._id] = new_page
        return new_page

    def set_name(self, name: str) -> bool:
        """ Sets the name of this Tab to a new name
        :param name:
        :return:
        """
        changed = self.name == name
        self.name = name
        return changed


class StructureManager:
    """
    Manages document structure for a notebook
    Notebooks are organized with top-level categories known as "tabs," and each tab contains a series of
    pages, each of which may contain infinite sub-pages
    """

    def __init__(self, path: str):
        """ Constructor
        """
        # number of total tabs created
        self._total_tabs = 1
        # dict that associates IDs with components
        self.components: Dict[int, StructureComponent] = {}
        # path is a string that stores the root of the notebook in the filesystem
        self.path = path

    def new_tab(self, name: str = None, has_default_page: bool = False) -> Tab:
        """ Creates a new Tab in this notebook
        :param name: The name of the new Tab
        :param has_default_page: Whether or not the new Tab will be initialized with a default empty page
        :return: The new Tab created
        """
        tab = Tab(name if name is not None else "Tab " + str(self._total_tabs))
        self._total_tabs += 1
        if has_default_page:
            page = tab.add_page()
            self.components[page._id] = page
        self.components[tab._id] = tab
        return tab

    def new_page(self, parent: StructureComponent, title: str = None) -> Page:
        """
        Creates a new page at the specified path
        :param parent: The component under which to add the new page
        :param title: The title of the new page
        :return: The new page that was created
        """
        page = parent.add_page(title)
        self.components[page._id] = page
        return page

    def get_component(self, _id: int) -> Union[StructureComponent, None]:
        """
        Searches for a component by _id number
        :param _id: The _id to search for
        :return: The component associated with the given _id
        """
        return self.components[_id] if _id in self.components else None
