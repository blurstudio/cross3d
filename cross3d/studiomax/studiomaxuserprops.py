##
#	\namespace	cross3d.StudiomaxUserProps
#
#	\remarks	The cross3d.StudiomaxUserProps handles storing and retreving custom
#				properties from objects
#	
#	\author		mikeh
#	\author		Blur Studio
#	\date		05/23/11
#

from Py3dsMax import mxs
from PyQt4.QtCore import QDate, QString
from datetime import date
from cross3d.abstract.abstractuserprops 	import AbstractUserProps, AbstractFileProps
import os
import re
import json

class StudiomaxUserProps(AbstractUserProps):
	def __init__(self, nativePointer):
		super(StudiomaxUserProps, self).__init__(nativePointer)
		self._nativePointer = nativePointer
	
	def __delitem__(self, key):
		"""
			\remarks	There is no build in way to remove keys from userProp's so we create a copy of our userProps dictionary
						clear userProps on the object, remove the item we want to remove and restore the remaining data to the object.
		"""
		#key = self.typeCheck(key)
		data = self.lookupProps()
		if key in data:
			self.clear()
			data.pop(key)
			self.update(data)
	
	def __getitem__(self, key):
		return self.lookupProps()[key]
	
	def __setitem__(self, key, value):
		if isinstance(value, float):
			value = '%f' % value
		mxs.setUserProp(self._nativePointer, self.escapeKey(key), self.escapeValue(value))
		self.emitChange(key)

	def clear(self):
		"""
			\remarks	remove all userProps from the object
		"""
		mxs.setUserPropBuffer(self._nativePointer, '')
	
	def pop(self, key, default = None):
		#key = self.typeCheck(key)
		if not key in self.lookupProps():
			if default:
				return default
			raise KeyError(self.unescapeKey(key))
		out = self[key]
		del self[key]
		return out
	
	def popitem(self):
		data = self.lookupProps()
		if not data:
			raise KeyError('popitem(): dictionary is empty')
		item = data.popitem()
		del self[item[0]]
		return item

	def lookupProps(self):
		string = mxs.getUserPropBuffer(self._nativePointer)
		keyValues = string.split('\r\n')
		props = {}
		for kv in keyValues:
			split = kv.split(' = ', 1)
			if not len(split) == 2:
				split = kv.split('=', 1)
				if not len(split) == 2:
					split = kv.split(' ', 1)
					if not len(split) == 2:
						continue
			props[self.unescapeKey(split[0])] = self.unescapeValue(split[1])
		return props
	
	@staticmethod
	def unescapeValue(string):
		"""
			\remarks	replaces any html codes with their associated unstorable characters
			\return		<str>
		"""
		string = unicode(string)
		string, typ = AbstractUserProps._decodeString(string)
		string = string.replace('&#13;&#10;', '\r\n').replace('&#10;', '\n').replace('&#13;', '\r')
		if typ == float:
			return float(string)
		elif typ == int:
			return int(string)
		elif typ in (list, dict, tuple, bool):
			if typ == dict:
				try:
					return json.loads( string )
				except ValueError: pass
			try:
				return eval(string)
			except: pass
		return string

class StudiomaxFileProps(AbstractFileProps):
	def __new__(cls, fileName=''):
		# if a filename is passed in don't use the StudiomaxFileProps class, it is intended 
		# to read a file props from the open scene file using native maxscript calls.
		if fileName:
			return AbstractFileProps(fileName=fileName)
		return super(StudiomaxFileProps, cls).__new__(cls)
	
	def __init__(self, fileName=''):
		""" Read the custom properties of the currently open scene. If you provide a filename it
		will read the properties of that file, not the currently open file.
		:param fileName: If a valid file path is provided read the file props of that file instead
		of the currently open file using dsofile.dll. Defaults to a empty string.
		"""
		self.customName = mxs.pyhelper.namify('custom')
		super(StudiomaxFileProps, self).__init__(None)
	
	def __delitem__(self, key):
		index = mxs.fileProperties.findProperty(self.customName, key)
		if index:
			return mxs.fileProperties.deleteProperty(self.customName, key)
		raise KeyError('FileProps does not contain key: %s' % key)
	
	def __getitem__(self, key):
		index = mxs.fileProperties.findProperty(self.customName, key)
		if index:
			return self.__getValueForIndex__(index)
		raise KeyError('FileProps does not contain key: %s' % key)
	
	def __getValueForIndex__(self, index):
		value = mxs.fileProperties.getPropertyValue(self.customName, index)
		if isinstance(value, (unicode, str)):
			try:
				value = eval(value)
			except:
				pass
		return value
		
	def __setitem__(self, key, value):
		isDate = False
		if isinstance(value, QDate):
			value = value.toString('MM/dd/yyyy')
			isDate = True
		elif isinstance(value, date):
			value = value.strftime('%m/%d/%Y')
			isDate = True
		elif not isinstance(value, (float, int, str, unicode, QString)):
			value = repr(value)
		# addProperty is also setProperty
		if isDate:
			mxs.fileProperties.addProperty(self.customName, key, value, mxs.pyhelper.namify('date'))
		else:
			mxs.fileProperties.addProperty(self.customName, key, value)
		self.emitChange(key)
	
	def __repr__(self):
		return self.__str__()
	
	def clear(self):
		"""
		Removes all attributes and imedeately saves the changes. There is no QTimer delay.
		"""
		for i in range(1, mxs.fileProperties.getNumProperties(self.customName)):
			mxs.fileProperties.deleteProperty(self.customName, i)
	
	def lookupProps(self):
		out = {}
		for i in range(1, mxs.fileProperties.getNumProperties(self.customName) + 1):
			out.update({mxs.fileProperties.getPropertyName(self.customName, i): self.__getValueForIndex__(i)})
		return out
	
	def update(self, *args, **kwargs):
		"""
		Adds all provided items and imedeately saves the changes. There is no QTimer delay.
		"""
		for k, v in dict(*args, **kwargs).iteritems():
			self[k] = v

# register the symbol
import cross3d
cross3d.registerSymbol( 'UserProps', StudiomaxUserProps )
cross3d.registerSymbol( 'FileProps', StudiomaxFileProps )
