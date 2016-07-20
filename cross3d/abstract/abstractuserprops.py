# #
# 	\namespace	cross3d.UserProps
#
# 	\remarks	The cross3d.UserProps package creates an abstract wrapper from a 3d system
# 				to use storing and retreiving custom user props
#
# 	\author		mike
# 	\author		Blur Studio
# 	\date		05/26/11
#

import re
import json
import cross3d
from collections import OrderedDict
from PyQt4.QtCore import QTimer as _QTimer

dispatchObject = cross3d.dispatch.dispatchObject

class AbstractUserProps(dict):
	"""
	The cross3d.UserProps package creates an abstract wrapper from a 
	3d system to use storing and retreiving custom user props
	"""

	def __init__(self, nativePointer):
		dict.__init__(self)
		self._nativePointer = nativePointer

		# Handling and cleaning legacy tags. This is going away soon.
		# Pulls values from Tags and BlurTags the first time they are encountered
		# and then immediately deletes them so that they don't continue to overwrite
		# any values that are set on UserProps.
		# if 'BlurTags' in self.keys() and self['BlurTags']:
		# 	for key in self['BlurTags']:
		# 		self[key] = self['BlurTags'][key]
		# 	scene = cross3d.Scene()
		# 	obj = cross3d.SceneObject(scene, nativePointer)
		# 	self['BlurTags'] = {}
		# 	if not obj.model().isReferenced():
		# 		del self['BlurTags']

		# if 'Tags' in self.keys() and self['Tags']:
		# 	for key in self['Tags']:
		# 		self[key] = self['Tags'][key]
		# 	scene = cross3d.Scene()
		# 	obj = cross3d.SceneObject(scene, nativePointer)
		# 	self['Tags'] = {}
		# 	if not obj.model().isReferenced():
		# 		del self['Tags']

	def __contains__(self, key):
		return key in self.lookupProps()

	def __getitem__(self, key):
		return dict.__getitem__(self, key)

	def __iter__(self):
		return iter(self.keys())

	def __setitem__(self, key, value):
		dict.__setitem__(self, key, value)
		self.emitChange()

	def __str__(self):
		return '<{cls} {props}>'.format(cls=self.__class__.__name__, props=unicode(self.lookupProps()))

	def clear(self):
		self.lookupProps().clear()

	def copy(self):
		return self.lookupProps().copy()

	def emitChange(self, key=None):
		if key == 'Tags':
			dispatchObject('TagChanged', self._nativePointer)
		else:
			dispatchObject('customPropChanged', self._nativePointer)

	def keys(self):
		return self.lookupProps().keys()

	def items(self):
		return self.lookupProps().items()

	def iteritems(self):
		return self.lookupProps().iteritems()

	def iterkeys(self):
		return self.lookupProps().iterkeys()

	def itervalues(self):
		return self.lookupProps().itervalues()

	def has_key(self, key):
		return self.lookupProps().has_key(key)

	def get(self, key, default=None):
		return self.lookupProps().get(key, default)

	def lookupProps(self):
		"""
		This is the workhorse method for the class, it is responsible for 
		providing the dictionary of key value pares used for most of the 
		class. If it is unabstracted it will return a empty dictionary
		
		:return: dict
		
		"""
		return {}

	def toString(self, prefix='', seperator=':', postfix=' '):
		out = ''
		for key in self.keys():
			value = self[key]
			line = prefix + key + seperator + unicode(value) + postfix
			out += line
		return out

	def updateFromName(self, format=None):
		# TODO: REMOVE the dependency of this module
		from blur3d.naming import Name
		name = Name(self._nativePointer.name, format)
		for element in name.elements():
			key = element.objectName()
			text = element.text()
			if text == 'x':
				if key in self:
					del self[key]
			else:
				self[key] = text

	def pop(self, key, default=None):
		return self.lookupProps().pop(key, default)

	def popitem(self):
		return self.lookupProps().popitem()

	def setAllHidden(self, state):
		"""
		Make all user props visible or hidden if the software supports it.
		:param state: Should the propery be shown or hidden
		"""
		for key in self.keys():
			self.setHidden(key, state)

	def setdefault(self, key, default=None):
		props = self.lookupProps()
		if not key in props:
			self[key] = default
		return self[key]

	def setHidden(self, key, state):
		"""
		Hide the mecinism that stores user props in software that supports it.
		:param key: The key used to access the user prop
		:param state: If the item is hidden or shown
		"""
		return False

	def update(self, *args, **kwargs):
		for k, v in dict(*args, **kwargs).iteritems():
			self[k] = v

	def values(self):
		return self.lookupProps().values()

	@staticmethod
	def escapeKey(string):
		"""
		Replaces any unstorable characters in key with their html codes
		
		"""
		if not isinstance(string, (str, unicode)):
			string = unicode(string)
		return string.replace(' ', '&#32;').replace('\n', '&#10;').replace('\r', '&#13;')

	@staticmethod
	def escapeValue(string):
		"""
		Replaces any unstorable characters in value with their html codes

		"""
		if not isinstance(string, (str, unicode)):
			string = unicode(string)
		return string.replace('\r\n', '&#13;&#10;').replace('\n', '&#10;').replace('\r', '&#13;')

	@staticmethod
	def unescapeKey(string):
		"""
		Replaces any html codes with their associated unstorable characters

		"""
		if not isinstance(string, (str, unicode)):
			string = unicode(string)
		return string.replace('&#32;', ' ').replace('&#10;', '\n').replace('&#13;', '\r')

	@staticmethod
	def unescapeValue(string):
		"""
		Replaces any html codes with their associated unstorable characters

		"""
		string = unicode(string)
		try:
			return json.loads( string )
		except ValueError:
			pass
		string, typ = AbstractUserProps._decodeString(string)
		if typ == float:
			return float(string)
		elif typ == int:
			return int(string)
		elif typ in (list, dict, tuple, bool, OrderedDict):
			return eval(string)
		return string
	
	@staticmethod
	def _decodeString(string):
		try:
			int(string)
			return string, int
		except:
			pass
		if string.find('.') != -1:
			try:
				float(string)
				return string, float
			except:
				pass
		if string in ('True', 'False'):
			return string, bool
		if re.match('{.*}', string):
			return string, dict
		if re.match('\[.*\]', string):
			return string, list
		if re.match('#\(.*\)', string):
			data = []
			s = string
			sOpen, close = AbstractUserProps._posCounter(s)
			while (sOpen != -1 or close != -1):
				s = s[:sOpen-2]+'['+s[sOpen:close]+']'+s[close+1:]
				sOpen, close = AbstractUserProps._posCounter(s)
			return s, list
		if re.match('\(.*\)', string):
			return string, tuple
		if re.match('OrderedDict\(.*\)', string):
			return string, OrderedDict
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

class AbstractFileProps(AbstractUserProps):
	def __init__(self, fileName=''):
		self._dso = None
		self.fileName = fileName
		self._closeScheduled = False
		self._saveScheduled = False
		super(AbstractFileProps, self).__init__(None)

	def __delitem__(self, key):
		if self.dso().open(self.fileName):
			self._saveScheduled = True
			if self.dso().removeCustomProperty(key):
				self._close()
				return True
			raise KeyError('FileProps does not contain key: %s' % key)
		else:
			raise cross3d.Exceptions.FileNotDSO

	def __getitem__(self, key):
		if self.dso().open(self.fileName):
			self._scheduleClose()
			out = self.dso().customProperty(key)
			if out:
				return self.unescapeValue(out.value())
			raise KeyError('FileProps does not contain key: %s' % key)
		else:
			raise cross3d.Exceptions.FileNotDSO

	def __setitem__(self, key, value):
		if self.dso().open(self.fileName):
			self._saveScheduled = True
			prop = self.dso().customProperty(key)
			if prop:
				prop.setValue(value)
			else:
				self.dso().addCustomProperty(key, value)
			self._close()
			self.emitChange()
		else:
			raise cross3d.Exceptions.FileNotDSO

	def __repr__(self):
		return self.__str__()

	def _close(self):
		if self._saveScheduled:
			self._saveScheduled = False
			self.dso().save()
		self.dso().close()
		self._closeScheduled = False

	def _scheduleClose(self, save=False):
		if save:
			self._saveScheduled = save
		if not self._closeScheduled:
			_QTimer.singleShot(0, self._close)
			self._closeScheduled = True

	def clear(self):
		"""
		Removes all attributes and immediately saves the changes. There is no QTimer delay.
		"""
		if self.dso().open(self.fileName):
			self.dso().clear()
			self._saveScheduled = True
			self._close()
			self.emitChange()
		else:
			raise cross3d.Exceptions.FileNotDSO

	def close(self):
		"""
		Immediately closes the connection to the file.
		"""
		if self.dso().open(self.fileName):
			self._close()
		else:
			raise cross3d.Exceptions.FileNotDSO

	def dso(self):
		if not self._dso:
			from cross3d.migrate import dsofile
			self._dso = dsofile.DSOFile()
		return self._dso

	def lookupProps(self):
		dso = self.dso()
		if self.dso().open(self.fileName):
			self._scheduleClose()
			ret = {}
			[ret.update({prop.name(): self.unescapeValue(prop.value())}) for prop in self.dso().customProperties()]
			return ret
		else:
			raise cross3d.Exceptions.FileNotDSO

	def update(self, *args, **kwargs):
		"""
		Adds all provided items and imedeately saves the changes. There is no QTimer delay.
		"""
		if self.dso().open(self.fileName):
			for k, v in dict(*args, **kwargs).iteritems():
				self[k] = v
			self._saveScheduled = True
			self._close()
		else:
			raise cross3d.Exceptions.FileNotDSO

# register the symbol
cross3d.registerSymbol('UserProps', AbstractUserProps, ifNotFound=True)
cross3d.registerSymbol('FileProps', AbstractFileProps, ifNotFound=True)
