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

def create_id():
    """Return a unique ID using the current time."""
    now = datetime.datetime.now()
    timetuple = now.timetuple()
    id = time.mktime(timetuple)
    return str(id)
    
class Section :
    
    def __init__(self):
        self.title = ""
        self.synopsis = ""
        self.notes = ""
        self.id = None

    def set_id(self):
        self.id = create_id()
        return self.id

    def to_string(self):
        # Open tag
        section = '<header id="%s">\n' % self.id
        # Add sub tags
        if self.title:
            section += "<title>%s</title>\n" % self.title
        if self.synopsis:
            section += "<synopsis>\n%s\n</synopsis>\n" % self.synopsis
        if self.notes:
            section += "<notes>\n%s\n</notes>\n" % self.notes
        # Close tag
        section += "</header>\n" 

        return section

class Character:
    
    def __init__(self):
        # General
        self.name = ""
        self.age = ""
        self.job = ""
        self.origin = ""
        self.residency = ""
        self.religion = ""
        # physical: appereance, dress, weight, height, etc
        self.physical = ""
        # psychological: traumas, dreams, fobias
        self.psychological = ""
        # Social: relationship with other character, social status
        self.social = ""
        # Notes
        self.notes = ""
        self.id = None

    def set_id(self):
        self.id = create_id()
        return self.id

    def to_string(self):
        # Open tag
        profile = '<character id="%s">\n' % self.id

        # Internal elements
        profile += '<name>%s</name>\n' % self.name
        if self.age:
            profile += '<age>%s</age>\n' % self.age
        if self.job:
            profile += '<job>%s</job>\n' % self.job
        if self.origin:
            profile += '<origin>%s</origin>\n' % self.origin
        if self.residency:
            profile += '<residency>%s</residency>\n' % self.residency
        if self.religion:
            profile += '<religion>%s</religion>\n' % self.religion
        if self.physical:
            profile += '<physical>\n%s\n</physical>\n' % self.physical
        if self.psychological:
            profile += '<psychological>\n%s\n</psychological>\n' % self.psychological
        if self.social:
            profile += '<social>\n%s\n</social>\n' % self.social
        if self.notes:
            profile += '<notes>\n%s\n</notes>\n' % self.notes
        
        # Close tag
        profile += '</character>\n'

        return profile

class Location:
    
    def __init__(self):
        # General
        self.name = ""
        self.description = ""
        self.landscape = ""
        self.weather = ""
        self.tradition = ""
        self.id = None

    def set_id(self):
        self.id = create_id()
        return self.id

    def to_string(self):
        # Open tag
        profile = '<location id="%s">\n' % self.id

        # Add internal elements
        profile += '<name>%s</name>\n' % self.name
        if self.description:
            profile += '<description>\n%s\n</description>\n' % self.description
        if self.landscape:
            profile += '<landscape>\n%s\n</landscape>\n' % self.landscape
        if self.weather:
            profile += '<weather>\n%s\n</weather>\n' % self.weather
        if self.tradition:
            profile += '<tradition>\n%s\n</tradition>\n' % self.tradition

        # Close tag
        profile += '</location>\n'

        return profile

#################################################
# 
# Buffer to XML
#
#################################################
import re

(INIT,
 TITLE,
 SECTION,
 ENDSECTION,
 HEADER,
 PARA,
 BREAK
) = range(7)

(STARTTAG, 
 ENDTAG, 
 TEXT) = range(1,4)

seudo_xml = re.compile(r"""<(\w+).+?>       # 1. starttag
                           |</(\w+)>        # 2. endtag
                           |([^<>\n]+)      # 3. text strings
                        """, re.VERBOSE)



def scanner(txt):
    result_list = []
    scan = seudo_xml.scanner(txt)
    while True:
        m = scan.match()
        if not m:
            break
        result_list.append([m.lastindex, m.group(m.lastindex)])
    return result_list[0]

def state_machine(document):
    txt = ''
    STATE = INIT
    sections = False
    lines = document.split('\n')
    for line in lines:
        if not line:
            if STATE == PARA:
                txt += '</p>\n'
                STATE = BREAK
            continue
        token = scanner(line)
        if STATE == INIT:
            if token[0] == STARTTAG and token[1] == 'title':
                txt += line
                txt += '\n'
                STATE = TITLE
                continue
            else:
                assert False
        if STATE == TITLE:
            if token[0] == STARTTAG and token[1] == 'section':
                txt += line
                txt += '\n'
                STATE = SECTION
                sections = True
                continue
            elif token[0] == TEXT:
                txt += '<p>\n'
                txt += line
                txt += '\n'
                STATE = PARA
                continue
            else:
                assert False
        if STATE == SECTION:
            if token[0] == STARTTAG and token[1] == 'title':
                txt += line
                txt += '\n'
                STATE = HEADER
                continue
            else:
                assert False
        if STATE == HEADER:
            if token[0] == ENDTAG and token[1] == 'section':
                txt += line
                txt += '\n'
                STATE = ENDSECTION
                continue
            elif token[0] == TEXT:
                txt += '<p>\n'
                txt += line
                txt += '\n'
                STATE = PARA
                continue
            else:
                assert False
        if STATE == ENDSECTION:
            if token[0] == STARTTAG and token[1] == 'section':
                txt += line
                txt += '\n'
                STATE = SECTION
                continue
            elif token[0] == TEXT:
                txt += '<p>\n'
                txt += line
                txt += '\n'
                STATE = PARA
                continue
            else:
                assert False
        if STATE == PARA:
            if token[0] == ENDTAG and token[1] == 'section':
                txt += line
                txt += '\n'
                STATE = ENDSECTION
                continue
            elif token[0] == TEXT:
                txt += '<br />\n'
                txt += line
                txt += '\n'
                STATE = PARA
                continue
            else:
                assert False
    
        if STATE == BREAK:
            if token[0] == ENDTAG and token[1] == 'section':
                txt += line
                txt += '\n'
                STATE = ENDSECTION
                continue
            elif token[0] == TEXT:
                txt += '<p>\n'
                txt += line
                txt += '\n'
                STATE = PARA
                continue
            else:
                assert False

    if sections and STATE != ENDSECTION:
        txt += '</section>\n'

    return txt
#################################################

class Loader:
    
    def __init__(self, document):
        self.stack = []
        self.content = ""
        self.document = document
        self.first_section = True

    def xml(self, attrib):
        print "XML", attrib

    def start(self, tag, attrib):
        # Map main sections:
        if tag == 'rayuela':
            self.stack.append(tag)
        if tag == 'sections':
            self.stack.append(tag)
        if tag == 'characters':
            self.stack.append(tag)
        if tag == 'locations':
            self.stack.append(tag)
        if tag == 'content':
            self.stack.append(tag)

        # Handle tags
        if tag == 'character':
            assert self.stack[-1] == 'characters'
            character = Character()
            character.id = attrib['id']
            character.name = attrib['name']
            character.age = attrib["age"]
            character.job = attrib["job"]
            character.origin = attrib["origin"]
            character.residency = attrib["residency"]
            character.religion = attrib["religion"]
            character.physical = attrib["physical"]
            character.psychological = attrib["psychological"]
            character.social = attrib["social"]
            character.notes = attrib["notes"]
            self.document.character.append(character)

        if tag == 'location':
            assert self.stack[-1] == 'locations'
            location = Location()
            location.id = attrib["id"] 
            location.name = attrib["name"] 
            location.description = attrib["description"] 
            location.landscape = attrib["landscape"] 
            location.weather = attrib["weather"] 
            location.tradition = attrib["tradition"] 
            self.document.location.append(location)

        if tag == 'section':
            if self.stack[-1] == 'sections':
                if attrib['id'] == 'synopsis':
                    #self.document.synopsis.id = attrib['id']
                    self.document.head.title = attrib['title']
                    self.document.head.summary = attrib['synopsis']
                    self.document.head.notes = attrib['notes']
                else:
                    section = Section()
                    section.id = attrib['id']
                    section.title = attrib['title']
                    section.synopsis = attrib['synopsis']
                    section.notes = attrib['notes']
                    self.document.append(section)
            else:
                if self.first_section:
                    self.first_section = False
                else:
                    xml_tag = '</section>\n'
                    self.document.buffer.insert_at_cursor(xml_tag)
                cursor_mark = self.document.buffer.get_insert()
                cursor = self.document.buffer.get_iter_at_mark(cursor_mark)
                self.document.buffer.create_mark(attrib['id'], cursor, True)

                xml_tag = '<section id="%s">\n' % attrib['id']
                self.document.buffer.insert(cursor, xml_tag)

        if tag == 'title':
            if self.stack[-1] == 'content':
                cursor_mark = self.document.buffer.get_insert()
                cursor = self.document.buffer.get_iter_at_mark(cursor_mark)

                xml_tag = '<title>'
                self.document.buffer.insert(cursor, xml_tag)

    def end(self, tag):
        if tag == 'sections':
            opentag = self.stack.pop()
            assert opentag == tag
        if tag == 'characters':
            opentag = self.stack.pop()
            assert opentag == tag
        if tag == 'locations':
            opentag = self.stack.pop()
            assert opentag == tag
        if tag == 'content':
            opentag = self.stack.pop()
            assert opentag == tag
        if tag == 'title':
            if self.stack[-1] == 'content':
                cursor_mark = self.document.buffer.get_insert()
                cursor = self.document.buffer.get_iter_at_mark(cursor_mark)

                xml_tag = '</title>'
                self.document.buffer.insert(cursor, xml_tag)
                
        if tag == 'rayuela':
            #self.content
            pass

    def data(self, text):
        if self.stack[-1] == 'content':
            self.document.buffer.insert_at_cursor(text)

class Header:

    def __init__(self):
        self.title = ''
        self.author = ''
        self.language = ''
        self.summary = ''
        self.notes = ''

    def to_string(self):
        # Open tag
        result = '<head>\n'
        result += '<title>%s</title>\n' % self.title
        # Adding optional elements
        if self.author:
            result += '<author>%s</author>\n' % self.author
        if self.language:
            result += '<language>%s</language>\n' % self.language
        if self.summary:
            result += '<summary>\n%s\n</summary>\n' % self.summary
        if self.notes:
            result += '<notes>\n%s\n</notes>\n' % self.notes
        # Close tag
        result += '</head>\n'
        return result

class Document(list):
    
    def __init__(self, page, buffer):
        list.__init__(self)

        self.page = page
        self.buffer = buffer
        self.head = Header()
        self.character = []
        self.location = []
        self.filename = ''
        self.filepath = ''

    def load_file(self, filename):
        assert os.path.isfile(filename)
        self.filepath, self.filename = os.path.split(filename)
        # [TODO] 
        # priority: medium
        # Use the python default xml library.
        import scanner
        fh = open(filename)
        scanner.scan(fh.read(), Loader(self))
        #.
        fh.close()
        #.
    
    def buffer_to_xml(self):
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        txt = self.buffer.get_text(start, end)
        # [TODO]
        # priority: high
        # Parse the txt, add <body>, <br /> and <p> tags.
        txt = txt.strip()
        return state_machine(txt)
        #lines = txt.split('\n')
        #n = 0
        #for i in lines:
        #    n += 1
        #    print i
        #.

    def dump_file(self, filename=''):
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        txt = self.buffer.get_text(start, end)

        if not filename:
            filename = os.path.join(self.filepath, self.filename)
        else:
            self.filepath, self.filename = os.path.split(filename)
        
        # Open tag:
        document = '<rayuela>\n' # lang="%s"> % self.lang

        # sections:
        sections = "<toc>\n"
        for section in self:
            sections += section.to_string()
        sections += "</toc>\n" 

        document += sections
        
        # characters:
        characters = "<characters>\n"
        for n in self.character:
            characters += n.to_string()
        characters += "</characters>\n" 

        document += characters

        # locations:
        locations = "<locations>\n"
        for n in self.location:
            locations += n.to_string()
        locations += "</locations>\n" 

        document += locations

        # Add manuscript:
        manuscript = '<manuscript>\n'

        # Add head:
        manuscript += self.head.to_string()

        # Add body:
        body = '<body>\n%s\n</body>\n' % self.buffer_to_xml() #txt.strip()
        
        manuscript += body
        manuscript += '</manuscript>'

        document += manuscript

        # Close tag:
        document += '</rayuela>'

        fh = open(filename, 'w')
        fh.write(document)
        fh.close()

        self.buffer.set_modified(False)
        
    def get_section_by_id(self, id):
        for section in self:
            if section.id == id:
                return section
        return None

    def get_character_by_id(self, id):
        for i in self.character:
            if i.id == id:
                return i
        return None

    def get_location_by_id(self, id):  
        for i in self.location:
            if i.id == id:
                return i
        return None

if __name__ == "__main__":
    import sys
    import gtk
    d = Document(0, gtk.TextBuffer())
    d.load_file(sys.argv[1])
    d.dump_file(sys.argv[2])
    # d.buffer_to_xml()
