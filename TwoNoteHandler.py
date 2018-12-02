import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

builder = Gtk.Builder()
builder.add_from_file("TestNotepad2.glade")
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


active_tags = []

buffer.create_mark("old_pos", buffer.get_iter_at_mark(buffer.get_insert()), True)

#implement emoji chooser
#strike through property?

class SearchDialog(Gtk.Dialog):

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Search", parent,
            Gtk.DialogFlags.MODAL, buttons=(
            Gtk.STOCK_FIND, Gtk.ResponseType.OK,
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))

        box = self.get_content_area()

        label = Gtk.Label("Insert text you want to search for:")
        box.add(label)

        self.entry = Gtk.Entry()
        box.add(self.entry)

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
        #for x in active_tags:
            #print(x)

        buffer.remove_tag_by_name("found", buffer.get_start_iter(), buffer.get_end_iter())
        buffer.apply_tag(tag_font, buffer.get_iter_at_mark(buffer.get_mark("old_pos")), buffer.get_iter_at_mark(buffer.get_insert()))
        buffer.apply_tag(tag_size, buffer.get_iter_at_mark(buffer.get_mark("old_pos")), buffer.get_iter_at_mark(buffer.get_insert()))

        for x in active_tags:
            buffer.apply_tag_by_name(x, buffer.get_iter_at_mark(buffer.get_mark("old_pos")), buffer.get_iter_at_mark(buffer.get_insert()))

    #should we change the way this works?
    def change_justification(self, button):
        global justification_blocked
        global main_justification_name

        if (justification_blocked == True):
            justification_blocked = False
            return

        #do not execute function when button is deactivated
        if(button.get_active() == False):
            return

        name = Gtk.Buildable.get_name(button)
        bounds = buffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds

        if len(bounds) != 0 and (not start.is_start() or not end.is_end()):
            #print(name)
            print(end.is_end())
            buffer.apply_tag_by_name(name, start, end)

            #restore main justification
            justification_blocked = True
            main_justification = builder.get_object(main_justification_name)
            main_justification.set_active(True)
        else:
            #print(name)
            main_justification_name = name
            textview.set_justification(justifications[name])

        insert = buffer.get_iter_at_mark(buffer.get_insert())
        buffer.place_cursor(insert)


    def change_justification_helper(self, button):
        bounds = buffer.get_selection_bounds()
        name = Gtk.Buildable.get_name(button)
        #print("outside")

        if (len(bounds) != 0 and button.get_active() == True):
            #print(name)
            start, end = bounds
            buffer.remove_tag_by_name("left", start, end)
            buffer.remove_tag_by_name("center", start, end)
            buffer.remove_tag_by_name("right", start, end)
            buffer.remove_tag_by_name("fill", start, end)
            buffer.apply_tag_by_name(name, start, end)
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

            Handler.search_and_mark(self, dialog.entry.get_text(), start) #TODO: missing argument: start

        dialog.destroy()

    #TODO: change this
    def search_and_mark(self, text, start):
        global buffer
        global tag_found
        end = buffer.get_end_iter()
        match = start.forward_search(text, 0, end)

        if match is not None:
            match_start, match_end = match
            buffer.apply_tag(tag_found, match_start, match_end)
            Handler.search_and_mark(self, text, match_end) #TODO: What is this 'self'. Deactivate tag when you start typing again

    #why the pointer?
    #or else python interpreter will continue running
    def close(self, *args):
        Gtk.main_quit()


builder.connect_signals(Handler())
buffer.connect("insert-text", Handler.get_old_pos)
buffer.connect("end-user-action", Handler.edit_input)
#buffer.connect("group-changed", Handler.set_spacing)

window = builder.get_object("MainWindow")
window.show_all()

Gtk.main()
