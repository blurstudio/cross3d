##
#	\namespace	blurapi.libs.XML.xmldocument
#
#	\remarks	Defines the way to parse XML library information
#	
#	\author		beta@blur.com
#	\author		Blur Studio
#	\date		04/09/10
#

import os
import xml.dom.minidom

from xmlelement import XMLElement
from Qt.QtCore import QString


class XMLDocument(XMLElement):
	""" class to ease the handling of XML documents """
	
	def __init__(self, object=None):
		if (not object):
			object = xml.dom.minidom.Document()
		XMLElement.__init__(self, object)
		self.__file__ = ''
		# TODO: Remove when all uses are gone, should no longer be needed
		self.escapeDict = {}

	def findElementById(self, childId):
		split = child.split('::')
		outTemplate = None
		if (split):
			outTemplate = self.root().findChildById(split[0])
			index = 1

			while (index < len(split) and outTemplate):
				outTemplate = outTemplate.findChildById(split[index])
				index += 1
		return outTemplate

	def load(self, fileName):
		"""
		Loads the given xml file by calling xml.dom.minidom.parse, 
		setting this instances object to the resulting value.

		"""
		success = False
		fileName = unicode(fileName)
		if (os.path.exists(fileName)):
			try:
				newObject = xml.dom.minidom.parse(fileName)
			except Exception, e:
				print 'Unable to parse filename!!!!', fileName
				print e
				return False

			if (newObject):
				self.removeWitespaceNodes(newObject)
				self.__file__ = fileName
				self._object = newObject
				success = True
		return success

	def parse(self, xmlString):
		success = False
		if isinstance(xmlString, QString):
			xmlString = unicode(xmlString)
		else:
			xmlString = xmlString.encode('utf-8')
		if (xmlString):
			tempObject = xml.dom.minidom.parseString(xmlString)
			if (tempObject):
				self._object = tempObject
				success = True
		return success

	@staticmethod
	def removeWitespaceNodes(node):
		"""
		Removes any nodes that are simply whitespace. Because we are saving to disk using toprettyxml the
		new lines get read into the xml leading to files getting alot of empty whitespace.
		"""
		wsNodes = []
		hasElement = False
		for n in node.childNodes:
			if isinstance(n,xml.dom.minidom.Text) and not n.wholeText.replace('\n', '').replace('\t', '').replace(' ', ''):
				wsNodes.append(n)
			if isinstance(n,xml.dom.minidom.Element):
				hasElement = True
				XMLDocument.removeWitespaceNodes(n)
		if hasElement and wsNodes:
			for n in wsNodes:
				node.removeChild(n)

	def root(self):
		"""Returns the root xml node for this document.

		"""
		if (self._object and self._object.childNodes):
			return XMLElement(self._object.childNodes[0], self.__file__)
		return None

	def save(self, fileName, pretty=True, showDialog=False):
		"""
		Saves the xml document to the given file, converting it to a 
		pretty XML document if so desired.
		
		:param fileName: path to the save location
		:param pretty: if set to True, will format spaces and line breaks.
		:param showDialog: if set to True, if an error occurs while saving,
		                   a dialog will be displayed showing the errors.
		:type fileName: str
		:type pretty: bool
		:type showDialog: bool

		"""
		if (os.path.exists(os.path.split(fileName)[0])):
			self.__file__ = fileName
			try:
				if (pretty):
					text = self.formatXml(self.toxml())
				else:
					text = self.toxml(encoding=None)
			except:
				print 'Encoding error while saving XML'
				if showDialog:
					from Qt.QtGui	import QMessageBox
					QMessageBox.critical(None, 'Encoding Error', 'Unable to save xml data, please check for unsupported characters.')
				return False
			f = open(fileName, 'w')
			f.write(text)
			f.close()
			return True
		if showDialog:
			from Qt.QtGui	import QMessageBox
			QMessageBox.warning(None, 'Unable to Save', 'Unable to save xml data, please verify you have the correct privileges.')
		return False

	def toxml(self, encoding='utf-8'):
		if encoding == 'utf-8':
			return unicode(self._object.toxml('utf-8'), 'utf-8')
		else:
			return self._object.toxml('utf-8')

	def toprettyxml(self, *args, **kw):
		return self._object.toprettyxml(*args, **kw)

	@staticmethod
	def formatXml(xmltext, indented=4):
		from Qt.QtXml import QDomDocument
		doc = QDomDocument()
		doc.setContent(QString(xmltext))
		return unicode(doc.toString(indented))
