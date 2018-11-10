import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango


class Handler:

    def set_bold(self, button):
        bounds = buffer.get_selection_bounds()
        tag_bold = buffer.create_tag('bold', weight=Pango.Weight.BOLD)
        if len(bounds) != 0:
            (start, end) = bounds
            buffer.apply_tag(tag_bold, start, end)

    def set_italic(self, button):
        bounds = buffer.get_selection_bounds()
        tag_italic = buffer.create_tag('italic',
                style=Pango.Style.ITALIC)
        if len(bounds) != 0:
            (start, end) = bounds
            buffer.apply_tag(tag_italic, start, end)

    def set_underline(self, button):
        bounds = buffer.get_selection_bounds()
        tag_underline = buffer.create_tag('underline',
                underline=Pango.Underline.SINGLE)
        if len(bounds) != 0:
            (start, end) = bounds
            buffer.apply_tag(tag_underline, start, end)

    def set_found(self, button):
        bounds = buffer.get_selection_bounds()
        tag_found = buffer.create_tag('found', background='yellow')
        if len(bounds) != 0:
            (start, end) = bounds
            buffer.apply_tag(tag_found, start, end)


builder = Gtk.Builder()
builder.add_from_file('../views/application_view.glade')
textview = builder.get_object('textview')
buffer = textview.get_buffer()
builder.connect_signals(Handler())

window = builder.get_object('MainWindow')
window.show_all()

Gtk.main()

			
