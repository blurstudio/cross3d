##
#	\namespace	blur3d.api.StudiomaxUserProps
#
#	\remarks	The blur3d.api.StudiomaxUserProps handles storing and retreving custom
#				properties from objects
#	
#	\author		mikeh@blur.com
#	\author		Blur Studio
#	\date		05/23/11
#

from Py3dsMax import mxs
from PyQt4.QtCore import QDate, QString
from datetime import date
from blur3d.api.abstract.abstractuserprops 	import AbstractUserProps, AbstractFileProps
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
		string, typ = StudiomaxUserProps._decodeString(string)
		string = string.replace('&#13;&#10;', '\r\n').replace('&#10;', '\n').replace('&#13;', '\r')
		if typ == float:
			return float(string)
		elif typ == int:
			return int(string)
		elif typ in (list, dict, tuple):
			if typ == dict:
				try:
					return json.loads( string )
				except ValueError: pass
			try:
				return eval(string)
			except: pass
		return string
	
	@staticmethod
	def _decodeString(string):
		try:
			int(string)
			return string, int
		except:
			pass
		if string.endswith('d0') or string.find('.'):
			val = string.rstrip('d0')
			try:
				float(val)
				return val, float
			except:
				pass
		if re.match('\{.*\}', string):
			return string, dict
		if re.match('#\(.*\)', string):
			data = []
			s = string
			open, close = StudiomaxUserProps._posCounter(s)
			while (open != -1 or close != -1):
				#if open and close < len(string):
				s = s[:open-2]+'['+s[open:close]+']'+s[close+1:]
				open, close = StudiomaxUserProps._posCounter(s)
			return s, list
		if re.match('\(.*\)', string):
			return string, tuple
		return string, None
	
	@staticmethod
	def _posCounter(string, opening = '#(', closing = ')'):
		openBr = 0
		openPos = 0
		found = False
		for pos in range(0, len(string)):
			if string[pos-2:pos] == opening:
				openBr += 1
				if not found:
					openPos = pos
					found = True
			elif string[pos] == closing:
				openBr -= 1
			if found and not openBr:
				break
		else:
			return -1,-1
		return openPos, pos

class StudiomaxFileProps(AbstractFileProps):
	def __init__(self, fileName=''):
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
from blur3d import api
api.registerSymbol( 'UserProps', StudiomaxUserProps )
api.registerSymbol( 'FileProps', StudiomaxFileProps )