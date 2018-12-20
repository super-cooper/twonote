import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango
from storage.StructureManager import StructureManager, STRUCTURE_MANAGER_FILE
import os

TEST_NOTEBOOK_PATH = '/tmp/TestNotebook/'

'''Get essential widgets from Glade File'''
builder = Gtk.Builder()
builder.add_from_file("Weizheng.glade")
window = builder.get_object("MainWindow")
treeview = builder.get_object("treeview")
textview_box=builder.get_object("textview_box")
scrolled_window = builder.get_object("scrolled_window")
color_chooser = builder.get_object("color_chooser")
highlight_chooser = builder.get_object("highlight_chooser")

'''create data store for treeview'''
store = Gtk.TreeStore(str, int)

'''list of tags to apply to inputted text'''
active_tags = []

'''justifications for indentation'''
justifications = {"left" : Gtk.Justification.LEFT, "center" : Gtk.Justification.CENTER, "right" : Gtk.Justification.RIGHT, "fill": Gtk.Justification.FILL}
main_justification_name = "left"
justification_blocked = False

'''setup font and spacing'''
font_chooser = builder.get_object("font_chooser")
spacing = "single" #keep track of current space
spacing_blocked = True
wrapping_blocked = False

'''create tag table for buffer'''
def setup_buffer(buffer):
    global tag_table, tag_font, tag_size, tag_bold, tag_underline, tag_italic, tag_left, tag_center, tag_right, tag_fill, tag_double, one_half, tag_found, tag_strike, tag_color, tag_highlight

    global tag_table
    tag_table = buffer.get_tag_table()

    font_family = font_chooser.get_font_family().get_name()
    font_size = font_chooser.get_font_size()
    tag_font = buffer.create_tag(font_family, family=font_family)
    tag_size = buffer.create_tag(str(font_size), size=12288)

    tag_bold = buffer.create_tag("bold", weight=Pango.Weight.BOLD)
    tag_underline = buffer.create_tag("underline", underline=Pango.Underline.SINGLE)
    tag_italic = buffer.create_tag("italics", style=Pango.Style.ITALIC)

    tag_left = buffer.create_tag("left", justification=Gtk.Justification.LEFT)
    tag_center = buffer.create_tag("center", justification=Gtk.Justification.CENTER)
    tag_right = buffer.create_tag("right", justification=Gtk.Justification.RIGHT)
    tag_fill = buffer.create_tag("fill", justification=Gtk.Justification.FILL)

    # TODO: spacing, word wrapping
    tag_double = buffer.create_tag("double", pixels_above_lines=10)
    one_half = buffer.create_tag("one_half", pixels_above_lines=7.5)

    tag_found = buffer.create_tag("found", background="yellow")

    tag_strike = buffer.create_tag("strike", strikethrough=True)

    tag_color = buffer.create_tag("Gdk.RGBA(red=0.000000, green=0.000000, blue=0.000000, alpha=1.000000)", foreground_rgba=Gdk.RGBA(red=0.000000, green=0.000000, blue=0.000000, alpha=1.000000))

    tag_highlight = buffer.create_tag("highlight: Gdk.RGBA(red=0.000000, green=0.000000, blue=0.000000, alpha=0.000000)", background_rgba=Gdk.RGBA(red=0.000000, green=0.000000, blue=0.000000, alpha=0.000000))

    '''create mark to keep track of position of cursor before user input'''
    buffer.create_mark("old_pos", buffer.get_iter_at_mark(buffer.get_insert()), True)

'''setup treeview'''
def show_treeview():
    #create the model
    #returns TreeIter poiting to this row
    #new_text = store.append(None, ["newfile.txt"])

    #the treeview shows the model
    treeview.set_model(store)
    single_click = True
    treeview.set_activate_on_single_click(single_click)

    # the cellrenderer for the first column
    renderer = Gtk.CellRendererText()
    #renderer2 = Gtk.CellRendererText()
    column_new_text = Gtk.TreeViewColumn("Notes", renderer, text=0)
    column_new_text.set_sort_column_id(0)
    column_id = Gtk.TreeViewColumn("ID", renderer, text=1)
    column_id.set_sort_column_id(1)

    #setting header clickable does not work
    treeview.set_headers_clickable(True)
    column_new_text.set_clickable(True)
    #print(treeview.get_headers_clickable())

    resizable = True
    column_new_text.set_resizable(resizable)
    treeview.append_column(column_new_text)

    resizable = True
    column_id.set_resizable(resizable)
    column_id.set_visible(True)
    treeview.append_column(column_id)


''' use destroy to remove widget from boc
textview_box.remove(textview)
textview.destroy()'''
#print(treeview.get_activate_on_single_click())
'''move textview methods here'''

'''setup initial page in treeview when no structure manager is found on startup'''
def initial_setup(parent_tab_name, initial_page_id):
    global treeview
    global store
    global manager
    global first_page_iter

    tree_selection = treeview.get_selection()
    iter = tree_selection.get_selected()[1]
    new_row = store.insert(iter, 100)
    #store.set(new_row, 0, name, 1, '0')
    store.set(new_row, 0, parent_tab_name)
    store.set(new_row, 1, 0)

    tree_selection.select_iter(new_row)

    tree_selection = treeview.get_selection()
    iter = tree_selection.get_selected()[1]
    new_row = store.insert(iter, 100)
    #store.set(new_row, 0, 'Untitled Page', 1, '1')
    store.set(new_row, 0, 'Untitled Page')
    store.set(new_row, 1, initial_page_id)
    #store.set(new_row, 0, 'Untitled Page')
    #store.set(new_row, (0, name), (1, '0'))
    #path = treeview.get_path_at_pos(0, store.iter_depth(new_row))[0]
    #take parent tab into account

    path_parent =  store.get_path(iter)
    path_row = store.get_path(new_row)
    treeview.expand_row(path_parent, False)
    tree_selection.select_iter(new_row)
    first_page_iter = new_row

'''NOTE: first try statement does not work. Delete structure manager after running the applicastion'''
#try:
    #manager = StructureManager.load_from_disk(os.path.join(TEST_NOTEBOOK_PATH, STRUCTURE_MANAGER_FILE))
    #buffer = manager.extract_text_from_page(manager.active_page)
    #textview = Gtk.TextView()
    #textview.set_buffer(buffer)
    #get the active page

#except FileNotFoundError:
manager = StructureManager(TEST_NOTEBOOK_PATH)
parent_tab_ID = manager.new_tab("Notebook")
parent_tab = "Notebook"
show_treeview()
initial_setup(parent_tab, manager.new_page(parent_tab_ID))

textview = Gtk.TextView()
buffer = textview.get_buffer()

textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
setup_buffer(buffer)
scrolled_window.add(textview)

class SearchDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Search", parent,
            Gtk.DialogFlags.MODAL, buttons=(
            Gtk.STOCK_FIND, Gtk.ResponseType.OK,
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        box = self.get_content_area()

        label_find = Gtk.Label("Insert text you want to search for:")
        box.add(label_find)

        self.entry_find = Gtk.Entry()
        box.add(self.entry_find)

        label_replace = Gtk.Label("Insert replacement text (optional):")
        box.add(label_replace)

        self.entry_replace = Gtk.Entry()
        box.add(self.entry_replace)

        self.show_all()


class Handler:

    def button_clicked(self, button):
        name = Gtk.Buildable.get_name(button)
        bounds = buffer.get_selection_bounds()

        #Will this fail with a non-toggle button
        if (button.get_active() == False):
            active_tags.remove(name)
            if len(bounds) != 0:
                start, end = bounds
                buffer.remove_tag_by_name(name, start, end)
        else:
            active_tags.append(name)

            if len(bounds) != 0:
                start, end = bounds
                buffer.apply_tag_by_name(name, start, end)

        #text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        #print(text)

    def font(self, button):
        global font_family
        global font_size
        global tag_font
        global tag_size
        #buffer.get_tag_table().remove(buffer.get_tag_table().lookup("font"))
        #active_tags.remove(font_type)

        font_family = font_chooser.get_font_family().get_name()
        font_size = font_chooser.get_font_size()

        if (tag_table.lookup(str(font_size)) == None):
            tag_size = buffer.create_tag(str(font_size), size=font_size)
        else :
            tag_size = tag_table.lookup(str(font_size))

        if (tag_table.lookup(font_chooser.get_font_family().get_name()) == None):
            tag_font = buffer.create_tag(font_family, family=font_family)
        else:
            tag_font = tag_table.lookup(font_chooser.get_font_family().get_name())

        #TEST THIS: remove tag?
        bounds = buffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            buffer.apply_tag(tag_font, start, end)
            buffer.apply_tag(tag_size, start, end)

    #begin user action or insert text?
    def get_old_pos(buffer, iter, text, len):
        buffer.move_mark_by_name("old_pos", iter)

    def edit_input(buffer):
        global tag_font
        global tag_size
        global tag_color
        global tag_highlight
        #for x in active_tags:
            #print(x)

        print(manager.active_page)
        buffer.remove_tag_by_name("found", buffer.get_start_iter(), buffer.get_end_iter())
        buffer.apply_tag(tag_font, buffer.get_iter_at_mark(buffer.get_mark("old_pos")), buffer.get_iter_at_mark(buffer.get_insert()))
        buffer.apply_tag(tag_size, buffer.get_iter_at_mark(buffer.get_mark("old_pos")), buffer.get_iter_at_mark(buffer.get_insert()))
        buffer.apply_tag(tag_color, buffer.get_iter_at_mark(buffer.get_mark("old_pos")), buffer.get_iter_at_mark(buffer.get_insert()))
        buffer.apply_tag(tag_highlight, buffer.get_iter_at_mark(buffer.get_mark("old_pos")), buffer.get_iter_at_mark(buffer.get_insert()))

        for x in active_tags:
            buffer.apply_tag_by_name(x, buffer.get_iter_at_mark(buffer.get_mark("old_pos")), buffer.get_iter_at_mark(buffer.get_insert()))

    #should we change the way this works?
    #fixed after user testing
    def change_justification(self, button):
        global justification_blocked
        global main_justification_name

        #do not execute function when button is deactivated
        if(button.get_active() == False):
            return


        name = Gtk.Buildable.get_name(button)
        bounds = buffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds

        if len(bounds) != 0 and (not start.is_start() or not end.is_end()) and justification_blocked == False:
            #print("if: " + name)
            #print(end.is_end())
            buffer.apply_tag_by_name(name, start, end)

            #restore main justification
            justification_blocked = True
            main_justification = builder.get_object(main_justification_name)
            main_justification.set_active(True)
        else:
            #print("else: "+ name)
            main_justification_name = name
            textview.set_justification(justifications[name])

        if (justification_blocked == True):
                justification_blocked = False

        insert = buffer.get_iter_at_mark(buffer.get_insert())
        buffer.place_cursor(insert)

    #TODO: if you highlight backwards, you get wierd behaviour
    #For when we align highlighted text with the main justification
    def change_justification_helper(self, button):
        bounds = buffer.get_selection_bounds()
        name = Gtk.Buildable.get_name(button)
        #print("outside")

        if (len(bounds) != 0 and button.get_active() == True):
            print(name)
            print("inside")
            start, end = bounds
            buffer.remove_tag_by_name("left", start, end)
            buffer.remove_tag_by_name("center", start, end)
            buffer.remove_tag_by_name("right", start, end)
            buffer.remove_tag_by_name("fill", start, end)
            #commenting this line out aligns highlighted text once again with the group
            #buffer.apply_tag_by_name(name, start, end)
            insert = buffer.get_iter_at_mark(buffer.get_insert())
            buffer.place_cursor(insert)

    def set_spacing(self, button):
        global spacing
        global spacing_blocked

        if (spacing_blocked == False):
            name = Gtk.Buildable.get_name(button)
            #print(name)
            bounds = buffer.get_selection_bounds()

            if (spacing != "single"):
                active_tags.remove(spacing)
                if len(bounds) != 0:
                    start, end = bounds
                    buffer.remove_tag_by_name(spacing, start, end)

            if (name != "single"):
                active_tags.append(name)
                if len(bounds) != 0:
                    start, end = bounds
                    buffer.apply_tag_by_name(name, start, end)

            spacing = name
            spacing_blocked = True
        else:
            spacing_blocked = False

    def on_search_clicked(self, widget):
        global buffer
        global window
        dialog = SearchDialog(window)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            cursor_mark = buffer.get_insert()
            start = buffer.get_iter_at_mark(cursor_mark)
            if start.get_offset() == buffer.get_char_count():
                start = buffer.get_start_iter()

            Handler.search_and_mark(self, dialog.entry_find.get_text(), dialog.entry_replace.get_text(), start) #TODO: missing argument: start

        dialog.destroy()

    #TODO: Make user apply tags to highlighted text
    def search_and_mark(self, text_entry, text_replace, start):
        global buffer
        global tag_found
        end = buffer.get_end_iter()
        match = start.forward_search(text_entry, 0, end)

        if match is not None:
            match_start, match_end = match
            #mark = buffer.create_mark("mark", match_start, False)
            #mark2 = buffer.create_mark("mark2", match_end, True)
            if (len(text_replace) > 0):
                #user_interaction = True
                #buffer_editable = True
                #buffer.select_range(match_start, match_end)
                #buffer.delete_selection(user_interaction, buffer_editable)
                buffer.delete(match_start, match_end)
                buffer.insert_with_tags(match_end, text_replace, tag_found)
            else:
                buffer.apply_tag(tag_found, match_start, match_end)
            Handler.search_and_mark(self, text_entry, text_replace, match_end) #TODO: What is this 'self'. Deactivate tag when you start typing again. fixed after user testing

    def set_wrapping(self, button):
        global textview
        global wrapping_blocked

        if (wrapping_blocked == False):
            name = Gtk.Buildable.get_name(button)
            if (name == "word_wrapping"):
                textview.set_wrap_mode(Gtk.WrapMode.WORD)
            elif (name == "char-wrapping"):
                textview.set_wrap_mode(Gtk.WrapMode.CHAR)
            elif (name == "both"):
                textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            else:
                textview.set_wrap_mode(Gtk.WrapMode.NONE)
        else:
            wrapping_blocked = True

    def change_color(self, widget, number):
        global buffer
        global tag_table
        global tag_color
        RGBA = widget.get_rgba()

        if (tag_table.lookup(str(RGBA)) == None):
            tag_color = buffer.create_tag(str(RGBA), foreground_rgba=RGBA)
        else :
            tag_color = tag_table.lookup(str(RGBA))

        #TEST THIS: remove tag?
        bounds = buffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            buffer.apply_tag(tag_color, start, end)

    def change_highlight(self, widget, number):
        global buffer
        global tag_table
        global tag_highlight

        RGBA = widget.get_rgba()

        if (tag_table.lookup("highlight: " + str(RGBA)) == None):
            tag_highlight = buffer.create_tag("highlight: " + str(RGBA), background_rgba=RGBA)
        else :
            tag_highlight = tag_table.lookup("highlight: " + str(RGBA))

        #TEST THIS: remove tag?
        bounds = buffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            buffer.apply_tag(tag_highlight, start, end)



    def open_color_dialog(self, button):
        Gtk.Widget.show_all(builder.get_object("color_chooser"))

    def open_highlight_dialog(self, button):
        Gtk.Widget.show_all(builder.get_object("highlight_chooser"))

    def close_dialog(self, widget, number):
        print(widget.get_rgba())
        Gtk.Widget.hide(widget)

    def new_page(self, button):
        global treeview
        global store
        global manager
        global textview
        global buffer
        '''new page and then set active page'''

        manager.save_page(buffer)

        manager.new_page(manager.active_page)

        tree_selection = treeview.get_selection()
        iter = tree_selection.get_selected()[1]
        new_row = store.insert(iter, 100)
        store.set(new_row, 0, "Untitled Page")
        store.set(new_row, 1, manager.active_page)

        #path = treeview.get_path_at_pos(0, store.iter_depth(new_row))[0]
        #take parent tab into account

        '''expand parent row'''
        if (iter != None):
            path_parent =  store.get_path(iter)
            path_row = store.get_path(new_row)
            treeview.expand_row(path_parent, False)
            tree_selection.select_iter(new_row)

        buffer = Gtk.TextBuffer()
        setup_buffer(buffer)
        textview.set_buffer(buffer)
        '''will this work?'''

    #def switch_active_page(self, ):

    def delete_row(self, button):
        global treeview
        global store
        tree_selection = treeview.get_selection()
        iter = tree_selection.get_selected()[1]

        store.remove(iter)

    def change_page(tree_model, path, column):
        global manager
        global store
        global buffer
        global textview
        global scrolled_window
        global first_page_iter

        '''If no page is open and you want to switch to a page'''
        if (store.get(store.get_iter(path), 0)[0] == "Notebook"):
            tree_selection = treeview.get_selection()
            tree_selection.select_iter(first_page_iter)
        else:
            '''switch from one page to another'''
            #print("If statement 3")
            manager.save_page(buffer)
            active_page_ID = store.get(store.get_iter(path), 1)[0]
            '''Is this necessary?'''
            manager.set_active_page(active_page_ID)
            #print(active_page_ID)
            buffer = manager.extract_text_from_page(manager.active_page)
            textview.set_buffer(buffer)

    #why the pointer?
    #or else python interpreter will continue running
    def close(self, *args):
        global manager
        #manager.save(buffer)
        manager.close()
        Gtk.main_quit()


####################################### Shortcuts Implementation ##################################

def bind_accelerator(accelerators, widget, accelerator, signal='clicked'):
    key, mod = Gtk.accelerator_parse(accelerator)
    widget.add_accelerator(signal, accelerators, key, mod, Gtk.AccelFlags.VISIBLE)

def run_command_bold(widget):
#	if (button.get_active() == False):
#		print("button false")
#	else:
#		print("button true")
    #Handler.button_clicked(widget)
    name = Gtk.Buildable.get_name(widget)
    bounds = buffer.get_selection_bounds()

    if "bold" not in active_tags:
        active_tags.append("bold")
        if len(bounds) != 0:
            start, end = bounds
            buffer.apply_tag_by_name(name, start, end)
    else:
        active_tags.remove("bold")
        if len(bounds) != 0:
            start, end = bounds
            buffer.remove_tag_by_name(name, start, end)

def run_command_underline(widget):
    name = Gtk.Buildable.get_name(widget)
    bounds = buffer.get_selection_bounds()
    #Handler.button_clicked(widget)
    if "underline" not in active_tags:
        active_tags.append("underline")
        if len(bounds) != 0:
            start, end = bounds
            buffer.apply_tag_by_name(name, start, end)
        #widget.set_active(True)
    else:
        active_tags.remove("underline")
        #widget.set_active(False)
        if len(bounds) != 0:
            start, end = bounds
            buffer.remove_tag_by_name(name, start, end)


def run_command_italics(widget):
    #handler = Handler()

    #Handler.button_clicked(handler,widget)
    #if "bold" not in active_tags:
    #    
    #else:
    #    
    name = Gtk.Buildable.get_name(widget)
    bounds = buffer.get_selection_bounds()
    #Handler.button_clicked(widget)
    if "italics" not in active_tags:
        active_tags.append("italics")
        if len(bounds) != 0:
            start, end = bounds
            buffer.apply_tag_by_name(name, start, end)
        #widget.set_active(True)
    else:
        active_tags.remove("italics")
        #widget.set_active(False)
        if len(bounds) != 0:
            start, end = bounds
            buffer.remove_tag_by_name(name, start, end)

#Adding accelerators to the window
accelerators = Gtk.AccelGroup()
window.add_accel_group(accelerators)

#Widget
target_bold = builder.get_object("bold")
target_bold.connect('clicked', run_command_bold)
target_underline = builder.get_object("underline")
target_underline.connect('clicked', run_command_underline)
target_italics = builder.get_object("italics")
target_italics.connect('clicked', run_command_italics)

#Bind
bind_accelerator(accelerators, target_bold, '<Control>b')
bind_accelerator(accelerators, target_underline, '<Control>u')
bind_accelerator(accelerators, target_italics, '<Control>i')



###################################################################################################


builder.connect_signals(Handler())
buffer.connect("insert-text", Handler.get_old_pos)
buffer.connect("end-user-action", Handler.edit_input)
treeview.connect("row-activated", Handler.change_page)
#color_chooser.connect("response", Handler.close_dialog)
#buffer.connect("group-changed", Handler.set_spacing)

window = builder.get_object("MainWindow")
textview_box = builder.get_object("textview_box")
window.show_all()

Gtk.main()
