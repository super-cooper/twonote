import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

builder = Gtk.Builder()
builder.add_from_file("/home/thomas/Documents/TestNotepad2.glade")
textview = builder.get_object("textview")
buffer = textview.get_buffer()

tag_table = buffer.get_tag_table()

font_chooser = builder.get_object("font_chooser")
font_family = font_chooser.get_font_family().get_name()
font_size = font_chooser.get_font_size()
tag_font = buffer.create_tag(font_family, family=font_family)
tag_size = buffer.create_tag(str(font_size), size=12288)

tag_bold = buffer.create_tag("bold", weight=Pango.Weight.BOLD)
tag_underline = buffer.create_tag("underline", underline=Pango.Underline.SINGLE)
tag_italic = buffer.create_tag("italics", style=Pango.Style.ITALIC)

active_tags = []

buffer.create_mark("old_pos", buffer.get_iter_at_mark(buffer.get_insert()), True)
#buffer.create_mark("new_pos", buffer.get_iter_at_mark(buffer.get_insert()), True)

class Handler:

    def button_clicked(self, button):
        name = Gtk.Buildable.get_name(button)

        if (name in active_tags):
            active_tags.remove(name)
        else:
            active_tags.append(name)
            bounds = buffer.get_selection_bounds()
            if len(bounds) != 0:
                start, end = bounds
                buffer.apply_tag_by_name(name, start, end)

        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)
        print(text)

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



    def get_old_pos(buffer, iter, text, len):
        buffer.move_mark_by_name("old_pos", iter)

    def edit_input(buffer):
        global tag_font
        global tag_size
        for x in active_tags:
            print(x)

        buffer.apply_tag(tag_font, buffer.get_iter_at_mark(buffer.get_mark("old_pos")), buffer.get_iter_at_mark(buffer.get_insert()))
        buffer.apply_tag(tag_size, buffer.get_iter_at_mark(buffer.get_mark("old_pos")), buffer.get_iter_at_mark(buffer.get_insert()))

        for x in active_tags:
            buffer.apply_tag_by_name(x, buffer.get_iter_at_mark(buffer.get_mark("old_pos")), buffer.get_iter_at_mark(buffer.get_insert()))


builder.connect_signals(Handler())
#buffer.connect("insert-text", Handler.edit_input)
buffer.connect("end-user-action", Handler.edit_input)
buffer.connect("insert-text", Handler.get_old_pos)

window = builder.get_object("MainWindow")
window.show_all()

Gtk.main()
