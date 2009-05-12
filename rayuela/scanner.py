# Copyright 1995-2008 by Fredrik Lundh

# By obtaining, using, and/or copying this software and/or its associated 
# documentation, you agree that you have read, understood, and will comply
# with the following terms and conditions:

# Permission to use, copy, modify, and distribute this software and its 
# associated documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appears in all copies, and that both
# that copyright notice and this permission notice appear in supporting 
# documentation, and that the name of Secret Labs AB or the author not be used 
# in advertising or publicity pertaining to distribution of the software without 
# specific, written prior permission.

# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS 
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. 
# IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR BE LIABLE FOR ANY SPECIAL, 
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM 
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE 
# OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR 
# PERFORMANCE OF THIS SOFTWARE.

# FROM
# http://effbot.org/zone/xml-scanner.htm

import re, string

# xml tokenizer pattern
xml = re.compile("<([/?!]?\w+)|&(#?\w+);|([^<>&'\"=\s]+)|(\s+)|(.)")

def scan(str, target):
    # split string into xml elements

    # create a scanner function for this string
    def gettoken(space=0, scan=xml.scanner(str).match):
        # scanner function (bound to the string)
        try:
            while 1:
                m = scan()
                code = m.lastindex
                text = m.group(m.lastindex)
                if not space or code != 4:
                    return code, text
        except AttributeError:
            raise EOFError

    # token categories
    TAG = 1; ENTITY = 2; STRING = 3; WHITESPACE = 4; SEPARATOR = 5

    start = target.start; end = target.end; data = target.data

    try:
        while 1:
            code, text = gettoken()
            if code == TAG:
                # deal with tags
                type = text[:1]
                if type == "/":
                    # end tag
                    end(text[1:])
                    code, text = gettoken(1)
                    if text != ">":
                        raise SyntaxError, "malformed end tag"
                elif type == "!":
                    # document type declaration (incomplete)
                    value = []
                    while 1:
                        # parse start tag contents
                        code, text = gettoken(1)
                        if text == ">":
                            break
                        value.append(text)
                    value = string.join(value, "")
                else:
                    # start tag or procesing instruction
                    tag = text
                    attrib = {}
                    while 1:
                        # parse start tag contents
                        code, text = gettoken(1)
                        if text == ">":
                            start(tag, attrib)
                            break
                        if text == "/":
                            start(tag, attrib)
                            end(tag)
                            break
                        if text == "?":
                            if type != text:
                                raise SyntaxError, "unexpected quotation mark"
                            code, text = gettoken(1)
                            if text != ">":
                                raise SyntaxError, "expected end tag"
                            try:
                                target.xml(attrib)
                            except AttributeError:
                                pass
                            break
                        if code == STRING:
                            # attribute
                            key = text
                            code, text = gettoken(1)
                            if text != "=":
                                raise SyntaxError, "expected equal sign"
                            code, quote = gettoken(1)
                            if quote != "'" and quote != '"':
                                raise SyntaxError, "expected quote"
                            value = []
                            while 1:
                                code, text = gettoken()
                                if text == quote:
                                    break
                                if code == ENTITY:
                                    try:
                                        text = fixentity(text)
                                    except ValueError:
                                        text = target.resolve_entity(text)
                                value.append(text)
                            attrib[key] = string.join(value, "")
            elif code == ENTITY:
                # text entities
                try:
                    text = fixentity(text)
                except ValueError:
                    text = target.resolve_entity(text)
                data(text)
            else:
                # other text (whitespace, string, or separator)
                data(text)
    except EOFError:
        pass
    except SyntaxError, v:
        # generate nicer error message
        raise

xml_entities = {"amp": "&", "apos": "'", "gt": ">", "lt": "<", "quot": '"'}

def fixentity(entity):
    # map entity name to built-in entity
    try:
        return xml_entities[entity]
    except KeyError:
        pass
    # assume numeric entity (raises ValueError if malformed)
    if entity[:2] == "#x":
        value = int(entity[2:], 16)
    else:
        value = int(entity[1:])
    if value > 127:
        return unichr(value)
    return chr(value)

if __name__ == "__main__": pass
