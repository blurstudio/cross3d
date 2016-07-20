"""Dynamically patch :mod:`xml.dom.minidom`'s attribute value escaping.

:meth:`xml.dom.minidom.Element.setAttribute` doesn't preform some
character escaping (see the `Python bug`_ and `XML specs`_).
Importing this module applies the suggested patch dynamically.

.. _Python bug: http://bugs.python.org/issue5752
.. _XML specs:
  http://www.w3.org/TR/2000/WD-xml-c14n-20000119.html#charescaping
"""

import xml.dom.minidom

escape_dict = {'&': "&amp;", ">": "&gt;", "<": "&lt;", '"': '&quot;', '\r': '&#xD;', '\n': '&#xA;', '\t': '&#x9;'}
def escape(data, entities={}):
    for k,v in escape_dict.iteritems():
        data = data.replace(k,v)
    return data

def unescape(data, entities={}):
    for k,v in escape_dict.iteritems():
        if k == '&': continue
        data = data.replace(v,k)
    # must do ampersand last
    return data.replace("&amp;", "&")

def _write_data(writer, data, isAttrib=False):
    "Writes datachars to writer."
    if isAttrib:
        data = escape(data)
    writer.write(data)
xml.dom.minidom._write_data = _write_data

def writexml(self, writer, indent="", addindent="", newl=""):
    # indent = current indentation
    # addindent = indentation to add to higher levels
    # newl = newline string
    writer.write(indent+"<" + self.tagName)

    attrs = self._get_attributes()
    a_names = attrs.keys()
    a_names.sort()

    for a_name in a_names:
        writer.write(" %s=\"" % a_name)
        _write_data(writer, attrs[a_name].value, isAttrib=True)
        writer.write("\"")
    if self.childNodes:
        writer.write(">%s"%(newl))
        for node in self.childNodes:
            node.writexml(writer,indent+addindent,addindent,newl)
        writer.write("%s</%s>%s" % (indent,self.tagName,newl))
    else:
        writer.write("/>%s"%(newl))
# For an introduction to overriding instance methods, see
#   http://irrepupavel.com/documents/python/instancemethod/
instancemethod = type(xml.dom.minidom.Element.writexml)
xml.dom.minidom.Element.writexml = instancemethod(
    writexml, None, xml.dom.minidom.Element)
