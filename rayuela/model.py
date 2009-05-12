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

import os
import datetime, time

class Section :
    
    def __init__(self):
        self.title = ""
        self.synopsis = ""
        self.notes = ""
        self.id = None

    def set_id(self):
        d = datetime.datetime.now()
        id = time.mktime(d.timetuple())
        self.id = str(id)
        return self.id

    def to_string(self):
        section = '''<section id="%s" 
        title="%s"
        synopsis="%s" 
        notes="%s">''' % (self.id, self.title, self.synopsis, self.notes)
        return section

class Loader:
    
    def __init__(self, document):
        self.stack = []
        self.content = ""
        self.document = document

    def xml(self, attrib):
        print "XML", attrib

    def start(self, tag, attrib):
        # Map main sections:
        if tag == 'rayuela':
            self.stack.append(tag)
        if tag == 'sections':
            self.stack.append(tag)
        if tag == 'content':
            self.stack.append(tag)

        # Handle tags
        if tag == 'section':
            if self.stack[-1] == 'sections':
                if attrib['id'] == 'synopsis':
                    self.document.synopsis.id = attrib['id']
                    self.document.synopsis.title = attrib['title']
                    self.document.synopsis.synopsis = attrib['synopsis']
                    self.document.synopsis.notes = attrib['notes']
                else:
                    section = Section()
                    section.id = attrib['id']
                    section.title = attrib['title']
                    section.synopsis = attrib['synopsis']
                    section.notes = attrib['notes']
                    self.document.append(section)
            else:
                cursor_mark = self.document.buffer.get_insert()
                cursor = self.document.buffer.get_iter_at_mark(cursor_mark)
                self.document.buffer.create_mark(attrib['id'], cursor, True)

                xml_tag = '<section id="%s">' % attrib['id']
                self.document.buffer.insert_with_tags_by_name(cursor, 
                                                              xml_tag, 
                                                              "invisible")

        if tag == 'title':
            if self.stack[-1] == 'content':
                cursor_mark = self.document.buffer.get_insert()
                cursor = self.document.buffer.get_iter_at_mark(cursor_mark)
                self.document.buffer.create_mark('startbold', cursor, True)

                xml_tag = '<title>'
                self.document.buffer.insert_with_tags_by_name(cursor, 
                                                              xml_tag, 
                                                              "invisible")

    def end(self, tag):
        if tag == 'sections':
            opentag = self.stack.pop()
            assert opentag == tag
        if tag == 'content':
            opentag = self.stack.pop()
            assert opentag == tag
        if tag == 'title':
            if self.stack[-1] == 'content':
                cursor_mark = self.document.buffer.get_insert()
                cursor = self.document.buffer.get_iter_at_mark(cursor_mark)
                self.document.buffer.create_mark('endbold', cursor, False)

                xml_tag = '</title>'
                self.document.buffer.insert_with_tags_by_name(cursor, 
                                                         xml_tag, 
                                                         "invisible")
                
                start_mark = self.document.buffer.get_mark('startbold')
                start = self.document.buffer.get_iter_at_mark(start_mark)
                end_mark = self.document.buffer.get_mark('endbold')
                end = self.document.buffer.get_iter_at_mark(end_mark)
                self.document.buffer.apply_tag_by_name('bold', start, end)
                self.document.buffer.delete_mark(start_mark)
                self.document.buffer.delete_mark(end_mark)
                
        if tag == 'rayuela':
            #self.content
            pass

    def data(self, text):
        if self.stack[-1] == 'content':
            self.document.buffer.insert_at_cursor(text)

class Document(list):
    
    def __init__(self, page, buffer):
        list.__init__(self)

        self.page = page
        self.buffer = buffer
        self.synopsis = Section()
        self.synopsis
        self.filename = ''
        self.filepath = ''

    def load_file(self, filename):
        assert os.path.isfile(filename)
        self.filepath, self.filename = os.path.split(filename)
        # [TODO] priority: high
        # Scan the file, put buffer tags and create section objects
        import scanner
        fh = open(filename)
        scanner.scan(fh.read(), Loader(self))
        #self.buffer.set_text(fh.read())
        fh.close()
        #.

    def dump_file(self, filename=''):
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        txt = self.buffer.get_text(start, end)

        if not filename:
            filename = os.path.join(self.filepath, self.filename)
        else:
            self.filepath, self.filename = os.path.split(filename)
        
        # [TODO] priority: high
        # This should save the XML file.

        # sections:
        sections = "<sections>\n"
        sections += self.synopsis.to_string()
        for section in self:
            sections += section.to_string()
        sections += "</sections>\n" 
        
        # document:
        document = '''<rayuela>
        %s
        <content>
        %s
        </content>
        </rayuela>
        ''' % (sections, txt)

        fh = open(filename, 'w')
        fh.write(document)
        fh.close()
        # and reload the buffer.
        #.

        self.buffer.set_modified(False)
        
    def get_section_by_id(self, id):
        for section in self:
            if section.id == id:
                return section
        return None

class Model:
    
    observers = []
    
    def __init__(self):
        self.documents = []
 
    def open(self, page, buffer, filename=''):
        new_document = Document(page, buffer)
        if filename:
            new_document.load_file(filename)
        self.documents.append(new_document)
        self.notify()
    
    def save(self, document, filename=''):
        document.dump_file(filename)
        self.notify()

    def get_document_by_page(self, page):
        for i in self.documents:
            if i.page == page:
                return i
        return None

    # Observer Pattern:    
    def register(self, observer):
        self.observers.append(observer)

    def remove(self, observer):
        self.observers.delete(observer)

    def notify(self):
        for observer in self.observers:
            if hasattr(observer, "update"):
                observer.update()

if __name__ == "__main__": pass
