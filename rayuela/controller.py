### Copyright (C) 2009 Manuel Ospina <ospina.manuel@gmail.com>

# This file is part of rayuela.
#
# rayuela is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# rayuela is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rayuela; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

try:
    import pygtk
    pygtk.require('2.0')
except:
    pass
try:
    import gtk
    import gtk.glade
    import pango
except:
    print "GTK is not installed"
    sys.exit(1)

import model
import view

class Controller:
    
    def __init__(self, glade_file):

        self.model = model.Model()
        self.view = view.View(self, self.model, glade_file)
        # [TODO]
        # We need a session framework. 
        # priority = low
        #self.new(None)
        #.

    def quit(self, obj):
        window = obj.get_toplevel()
        window.destroy()
        gtk.main_quit()

    def delete_event(self, obj, event): 
        return False

    def _get_page_(self): 
        notebook = self.view.widget_tree.get_widget("main_notebook")
        if not self.model.documents:
            textview = self.view.widget_tree.get_widget("textview")
        else:
            textview = self.view.add_textview()
            if not textview:
                view.error_dialog("Impossible to create a new page")
        current_page = notebook.get_current_page()
        #textbuffer = textview.get_buffer()
        textbuffer = gtk.TextBuffer(self.view.tag_table)
        textview.set_buffer(textbuffer)
        return (current_page, textbuffer)
    
    def _get_document_(self):
        notebook = self.view.widget_tree.get_widget("main_notebook")
        current_page = notebook.get_current_page()
        document = self.model.get_document_by_page(current_page)
        return document
    
    # [NOTE]
    # This features are not included in v0.1
    def _get_selection_iters_(self):
        """This function gets the start and end selection
        iters from the text view.
        Returns - start,end - gtk.TextIter objects

        (Based on:
        http://www.learningpython.com/2006/08/19/wordpress-python-library/
        )
        """

        #First check to see that the text buffer is valid
        document = self._get_document_()
        if not document.buffer:
            view.error_dialog("Text buffer not available")
            return

        #Get the selection bounds
        bounds = document.buffer.get_selection_bounds()
        if bounds:
            start, end = bounds
        else:
            # [NOTE]
            # Using the cursor mark as start and end doesn't change anything! 
            # All changes are done in selected text.
            cursor = document.buffer.get_insert()
            start = document.buffer.get_iter_at_mark(cursor)
            end = document.buffer.get_iter_at_mark(cursor)
            #.
        return start, end

    def _apply_tag_(self, tag):
        """This function is used to apply the tag to the selection.

        (Based on:
        http://www.learningpython.com/2006/08/19/wordpress-python-library/
        )
        """

        start_xml = "<" + tag + ">"
        end_xml = "</" + tag + ">"

        document = self._get_document_()

        bounds = self._get_selection_iters_()
        if not bounds:
            view.error_dialog("Error inserting tags")
            return
        else:
            start, end = bounds
        
        # Create a mark at the start and end
        start_mark = document.buffer.create_mark(None,start, True)
        end_mark = document.buffer.create_mark(None, end, False)
        
        # Create open XML tag
        # The start iter is still valid, we don't need to get it from the mark.
        document.buffer.insert_with_tags_by_name(start, start_xml, "invisible")

        # Create close XML tag
        end = document.buffer.get_iter_at_mark(end_mark)
        document.buffer.insert_with_tags_by_name(end, end_xml, "invisible")

        #Set pango tag
        start = document.buffer.get_iter_at_mark(start_mark)
        end = document.buffer.get_iter_at_mark(end_mark)
        document.buffer.apply_tag_by_name(tag, start, end)
        
        # Place cursor at the end of selection
        document.buffer.place_cursor(end)
    #.

    def new(self, obj):
        current_page, textbuffer = self._get_page_()
        self.model.open(current_page, textbuffer)
        self._add_synopsis_()

    def open(self, obj):
        filename = view.file_chooser('Open...', gtk.FILE_CHOOSER_ACTION_OPEN)
        current_page, textbuffer = self._get_page_()
        self.model.open(current_page, textbuffer, filename)

    def save(self, obj):
        document = self._get_document_()
        if document.filepath:
            self.model.save(document)
        else:
            self.save_as(obj)

    def save_as(self, obj):
        document = self._get_document_()
        filename = view.file_chooser('Save As...', gtk.FILE_CHOOSER_ACTION_SAVE)
        self.model.save(document, filename)

    def undo(self, obj): view.error_dialog("Not implemented")

    def redo(self, obj): view.error_dialog("Not implemented")

    def cut(self, obj): 
        document = self._get_document_()
        document.buffer.cut_clipboard(self.view.clipboard, True)

    def copy(self, obj):
        document = self._get_document_()
        document.buffer.copy_clipboard(self.view.clipboard)

    def paste(self, obj):
        document = self._get_document_()
        document.buffer.paste_clipboard(self.view.clipboard, None, True)

    def delete(self, obj): 
        self.cut(obj)
    
    def _add_synopsis_(self):
        document = self._get_document_()
        document.synopsis.id = 'synopsis'
        result = self.view.section_dialog(document.synopsis)
        if result == gtk.RESPONSE_OK:
            # tags:
            xml_start = "<title>"
            xml_end = "</title>"

            # Start tag
            cursor_mark = document.buffer.get_insert()
            cursor = document.buffer.get_iter_at_mark(cursor_mark)
            document.buffer.insert_with_tags_by_name(cursor, 
                                                     xml_start, 
                                                     "invisible", "center")
            # Add title:
            document.buffer.insert_with_tags_by_name(cursor, 
                                                     document.synopsis.title,
                                                     "bold", "uneditable")
            # End tag    
            document.buffer.insert_with_tags_by_name(cursor, 
                                                     xml_end, 
                                                     "invisible")
            # Break Line
            document.buffer.insert(cursor, "\n")

    def _add_dedication_(self):
        view.error_dialog("Not implemented")

    def _add_section_(self):
        section = model.Section()
        result = self.view.section_dialog(section)
        if result == gtk.RESPONSE_OK:
            document = self._get_document_()
            document.append(section)
            # tags:
            xml_start = "<title>"
            xml_end = "</title>"

            # Add tag:
            cursor_mark = document.buffer.get_insert()
            cursor = document.buffer.get_iter_at_mark(cursor_mark)
            mark = document.buffer.create_mark(section.id, cursor, True)

            xml_tag = '<section id="%s">' % section.id
            document.buffer.insert_with_tags_by_name(cursor, 
                                                     xml_tag, 
                                                     "invisible")
            # Title start tag
            document.buffer.insert_with_tags_by_name(cursor, 
                                                     xml_start, 
                                                     "invisible")

            # Add title:
            document.buffer.insert_with_tags_by_name(cursor, 
                                                     section.title,
                                                     "bold", "uneditable")
            # Title end tag
            document.buffer.insert_with_tags_by_name(cursor, 
                                                     xml_end, 
                                                     "invisible")
                
            # line break
            document.buffer.insert(cursor, "\n")

            # Ask the model to notify the observers:
            self.model.notify()

    def add_section(self, obj): 
        self._add_section_()

        # [NOTES]
        # This is not supported in v0.1 and it will change in the future:
        #section = self.view.get_section_to_add()
        #
        #if section == "synopsis":
        #    self._add_synopsis_()
        #elif section == "dedication":
        #    self._add_dedication_()
        #elif section == "section":
        #    self._add_section_()
        #else:
        #    view.error_dialog("Not implemented")
        #.

    # [NOTE]
    # This features are not supported in v0.1
    def bold(self, obj): 
        self._apply_tag_("bold")

    def italic(self, obj):
        self._apply_tag_("italic")

    def underline(self, obj):
        self._apply_tag_("underline")

    def justify_left(self, obj):
        self._apply_tag_("left")

    def justify_center(self, obj):
        self._apply_tag_("center")

    def justify_right(self, obj):
        self._apply_tag_("right")

    def justify_fill(self, obj): view.error_dialog("Not implemented")
    #.

    def preferences(self, obj): view.error_dialog("Not implemented")

    def spell_check(self, obj): view.error_dialog("Not implemented")

    def about(self, obj):
        txt = "Rayuela is a creative writing framework."
        view.info_dialog(txt) 

if __name__ == "__main__":
    from rayuela.glade import RAYUELA_GLADE_FILE 
    Controller(RAYUELA_GLADE_FILE)
    gtk.main()
