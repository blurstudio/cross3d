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
from blur3d.api.abstract.abstractuserprops 	import AbstractUserProps
import re

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
	def escapeValue(string):
		"""
			\remarks	replaces any unstorable characters in value with their html codes
			\return		<str>
		"""
		if isinstance(string, (float, list)):
			return string
		if not isinstance(string, (str, unicode, float)):
			string = unicode(string)
		return string.replace('\r\n', '&#13;&#10;').replace('\n', '&#10;').replace('\r', '&#13;')
	
	@staticmethod
	def unescapeValue(string):
		"""
			\remarks	replaces any html codes with their associated unstorable characters
			\return		<str>
		"""
		string = unicode(string)
		string, type = StudiomaxUserProps._decodeString(string)
		if type == float:
			return float(string)
		elif type == int:
			return int(string)
		elif type in (list, dict, tuple):
			return eval(string)
		return string.replace('&#13;&#10;', '\r\n').replace('&#10;', '\n').replace('&#13;', '\r')
	
	@staticmethod
	def _decodeString(string):
		if string.endswith('d0') or string.find('.'):
			val = string.rstrip('d0')
			try:
				float(val)
				return val, float
			except:
				pass
		if re.search('\{.+\}', string):
			return string, dict
		if re.search('#\(.+\)', string):
			data = []
			s = string
			open, close = StudiomaxUserProps._posCounter(s)
			while (open != -1 or close != -1):
				#if open and close < len(string):
				s = s[:open-2]+'['+s[open:close]+']'+s[close+1:]
				open, close = StudiomaxUserProps._posCounter(s)
			return s, list
		if re.search('\(.+\)', string):
			return string, tuple
		try:
			int(string)
			return string, int
		except:
			pass
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
			

# register the symbol
from blur3d import api
api.registerSymbol( 'UserProps', StudiomaxUserProps )