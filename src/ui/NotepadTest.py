import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

class Handler:
    def boldClicked(self, button):

        bounds = buffer.get_selection_bounds()
        tag_bold = buffer.create_tag("bold", weight=Pango.Weight.BOLD)
        if len(bounds) != 0:
            start, end = bounds
            buffer.apply_tag(tag_bold, start, end)


builder = Gtk.Builder()
builder.add_from_file("./TestNotepad1.glade")
textview = builder.get_object("textview")
buffer = textview.get_buffer()
builder.connect_signals(Handler())

window = builder.get_object("MainWindow")
window.show_all()

Gtk.main()
