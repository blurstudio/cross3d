"""
This is a dso file parser used to read custom metadata for files that support 
the OLE data model originally created for Microsoft Word.  Both 3dsMax and 
Softimage support this for .max, .scn, and .emdl.

This class is a convience wrapper that uses win32com.client to 
communicate with a DLL.  The 32bit version of the dll can be found 
`here <http://support.microsoft.com/kb/224351>`_.  The 64bit version of the 
dll can be found  
`here <http://www.keysolutions.com/blogs/kenyee.nsf/d6plinks/KKYE-79KRU6>`_.

Note: The 64bit version may have a few caveats that may affect you.

To install the dll on a system call "regsvr32 dsofile.dll" from cmd.exe 
in the folder of the dll's I renamed the 64bit dll to dsofile64.dll

Max documentation for editing dso properties:
	http://docs.autodesk.com/3DSMAX/16/ENU/MAXScript-Help/index.html?url=files/GUID-A8663B8E-7E30-474E-B3DB-E21585F125B1.htm,topicNumber=d30e705809

"""

from win32com.client import Dispatch as _Dispatch
from .enum import enum as _enum


class DSOCustProperty(object):

	def __init__(self, property):
		super(DSOCustProperty, self).__init__()
		self._property = property
	
	def name(self):
		return self._property.Name
	
	def setName(self, name):
		self._property.Name = name
	
	def setType(self, typ):
		self._property.Type = typ
	
	def setValue(self, value):
		self._property.Value = value
	
	def type(self):
		return self._property.Type
	
	def value(self):
		return self._property.Value

		
class DSOFile(object):
	"""Enumerated type representing the value types."""
	
	PropertyTypes = _enum('String', 'Long', 'Double', 'Bool', 'Date')
	SummaryKeys = _enum('Title', 'subject', 'Author', 'Keywords', 'Comments', 'Template', 'LastSavedBy', 'RevisionNumber', 'TotalEditTime',
		'DateLastPrinted', 'DateCreated', 'DateLastSaved', 'PageCount', 'WordCount', 'CharacterCount', 'Thumbnail', 'ApplicationName',
		'DocumentSecurity', 'Category', 'PresentationFormat', 'ByteCount', 'LineCount', 'ParagraphCount', 'SlideCount', 'NoteCount',
		'HiddenSlideCount', 'MultimediaClipCount', 'Manager', 'Company', 'CharacterCountWithSpaces', 'SharedDocument', 'Version', 'DigitalSignature')
	
	
	def __init__(self):
		super(DSOFile, self).__init__()
		self.dso = _Dispatch('DSOFile.OleDocumentProperties')
	
	def __del__(self):
		# the dso must be closed if open, or it will lock the custom properties of the file
		self.dso.close()
	
	def addCustomProperty(self, key, value):
		"""Adds a custom property with the given key, value pair.
		"""
		return self.dso.CustomProperties.Add(key, value)
	
	def clear(self):
		for item in self.dso.CustomProperties:
			item.remove()
	
	def close(self):
		self.dso.close()
	
	def customProperties(self):
		out = []
		for prop in self.dso.CustomProperties:
			out.append(DSOCustProperty(prop))
		return out
	
	def customProperty(self, key):
		"""
		Finds the key with the provided name and returns a custom Property. 
		If the key is not found it returns None.
		
		:rtype: :class:`DSOCustProperty`
		"""
		for item in self.dso.CustomProperties:
			if item.Name == key:
				return DSOCustProperty(item)
		return None
	
	def customPropertyNames(self):
		out = []
		for item in self.dso.CustomProperties:
			out.append(item.Name)
		return out
	
	def open(self, filename):
		"""
		:return: Returns True if the provided file supports dso.
		:rtype: bool
		"""
		if self.dso.IsOleFile:
			# The file is already open
			return True
		self.dso.Open(filename)
		if self.dso.IsOleFile:
			return True
		self.close()
		return False
	
	def removeCustomProperty(self, key):
		prop = self.customProperty(key)
		if prop:
			prop._property.remove()
			return True
		return False
	
	def save(self):
		self.dso.save()
	
	def summaryProperty(self, key):
		if isinstance(key, (int, long)):
			key = self.SummaryKeys.labelByValue(key)
		return getattr(self.dso.SummaryProperties, key)
