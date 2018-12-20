import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango

builder = Gtk.Builder()
builder.add_from_file("Notepad.glade")
textview = builder.get_object("textview")
buffer = textview.get_buffer()
window = builder.get_object("MainWindow")

tag_table = buffer.get_tag_table()

font_chooser = builder.get_object("font_chooser")
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
justifications = {"left" : Gtk.Justification.LEFT, "center" : Gtk.Justification.CENTER, "right" : Gtk.Justification.RIGHT, "fill": Gtk.Justification.FILL}
main_justification_name = "left"
justification_blocked = False

# TODO: spacing, word wrapping
tag_double = buffer.create_tag("double", pixels_above_lines=10)
one_half = buffer.create_tag("one_half", pixels_above_lines=7.5)
spacing = "single" #keep track of current space
spacing_blocked = True

tag_found = buffer.create_tag("found", background="yellow")

tag_strike = buffer.create_tag("strike", strikethrough=True)

textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
wrapping_blocked = False

color_chooser = builder.get_object("color_chooser")
tag_color = buffer.create_tag("Gdk.RGBA(red=0.000000, green=0.000000, blue=0.000000, alpha=1.000000)", foreground_rgba=Gdk.RGBA(red=0.000000, green=0.000000, blue=0.000000, alpha=1.000000))

highlight_chooser = builder.get_object("highlight_chooser")
tag_highlight = buffer.create_tag("highlight: Gdk.RGBA(red=0.000000, green=0.000000, blue=0.000000, alpha=0.000000)", background_rgba=Gdk.RGBA(red=0.000000, green=0.000000, blue=0.000000, alpha=0.000000))

active_tags = []

buffer.create_mark("old_pos", buffer.get_iter_at_mark(buffer.get_insert()), True)


#implement emoji chooser
#strike through property?

#TODO: treeview
#create the model
store = Gtk.TreeStore(str)
#returns TreeIter poiting to this row
new_text = store.append(None, ["newfile.txt"])

#the treeview shows the model
treeview = builder.get_object("treeview")
treeview.set_model(store)
single_click = True
treeview.set_activate_on_single_click(single_click)

# the cellrenderer for the first column
renderer = Gtk.CellRendererText()
# text attribute gets value from column 2
column_new_text = Gtk.TreeViewColumn("Notes", renderer, text=0)
resizable = True
column_new_text.set_resizable(resizable)
treeview.append_column(column_new_text)
''' use destroy to remove widget from boc
textview_box.remove(textview)
textview.destroy()'''
#print(treeview.get_activate_on_single_click())

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

    #TODO: change this
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

    #TODO: change this
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

    def test(text, a ,b ,c, d):
        print("ahh!")

    def test2(self, button, etc):
        global window
        print("hi")

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

    #why the pointer?
    #or else python interpreter will continue running
    def close(self, *args):
        Gtk.main_quit()


builder.connect_signals(Handler())
buffer.connect("insert-text", Handler.get_old_pos)
buffer.connect("end-user-action", Handler.edit_input)
#TODO: not working
textview.connect("move-cursor", Handler.test)
#color_chooser.connect("response", Handler.close_dialog)
#buffer.connect("group-changed", Handler.set_spacing)

window = builder.get_object("MainWindow")
textview_box = builder.get_object("textview_box")
window.show_all()

Gtk.main()
