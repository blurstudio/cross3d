
import abc
import re
import sys
from numbers import Number

# =============================================================================
# CLASSES
# =============================================================================

class _MetaEnumGroup(type):
	"""An EnumGroup metaclass.
	"""
	def __new__(cls, className, bases, classDict):
		newCls = type.__new__(cls, className, bases, classDict)
		newCls.__init_enums__()
		newCls._cls = cls
		newCls._clsName = className
		newCls._clsBases = bases
		newCls._clsDict = classDict
		return newCls

	def __call__(self, number):
		number = int(number)
		e = None
		for enum in self._ENUMERATORS:
			if enum & number:
				if e:
					e = e | enum
				else:
					e = enum
		return e

	def __getitem__(self, key):
		if isinstance(key, Number):
			return list(self)[int(key)]
		else:
			return getattr(self, str(key))

	def __instancecheck__(cls, inst):
		if type(inst) == cls:
			return True
		if isinstance(inst, cls._cls):
			return True
		return False

	def __iter__(self):
		for e in self._ENUMERATORS:
			yield e

	def __len__(self):
		return len(self._ENUMERATORS)

	def __repr__(self):
		return '<{mdl}.{cls}({enums})>'.format(
			mdl=self._clsDict.get('__module__', 'unknown'),
			cls=self._clsName,
			enums=self.join(),
		)

	def __str__(self):
		return '{0}({1})'.format(self._clsName, self.join())

	def __getattr__(self, name):
		"""This is entirely for backwards compatibility.

		This should/will be removed once a full transition is made.
		This is primarily required because there will be a period
		of time when trax.api is going out using the new EnumGroup
		setup, but there will be a time when not everyone has the
		update installed.
		"""
		# Construct an old enum from our EnumGroup.  If we have
		# descriptions for our new-style Enums, which is not
		# guaranteed, then we will set them.  Otherwise we will
		# give it an empty string.
		kwargs = dict()
		descriptions = dict()
		for e in self._ENUMERATORS:
			kwargs[e.name] = e.number
			try:
				descriptions[e.name] = e.description
			except AttributeError:
				descriptions[e.number] = ''
		oldEnum = enum(**kwargs)
		for number, desc in descriptions.iteritems():
			oldEnum.setDescription(number, desc)
		# Try and return the attribute from the old-style enum.
		try:
			return getattr(oldEnum, name)
		except AttributeError:
			raise AttributeError(
				"'EnumGroup' object has no attribute '{}'".format(name)
			)

# =============================================================================

class Enum(object):
	"""A basic enumerator class.

	Enumerators are named values that act as identifiers.  Typically, a
	list of enumerators are component pieces of an `EnumGroup`.

	Example:
		class Suit(Enum):
			pass
		
		class Suits(EnumGroup):
			Hearts = Suit()
			Spades = Suit()
			Clubs = Suit()
			Diamonds = Suit()

	Enum objects can be combined and compared using binary "and" and "or"
	operations.

	Example:
		mySuits = Suits.Hearts | Suits.Spades
		
		if Suits.Hearts & mySuits:
			print "This is true!"
		
		if Suits.Clubs & mySuits:
			print "This is false!"

	Attributes:
		name: The name of the enumerator.
		number: The integer value representation of the enumerator.
		label: The enumerator's label.
		labelIndex: The enumerator's index within its parent EnumGroup.
	"""
	__metaclass__ = abc.ABCMeta
	_CREATIONORDER = 0

	def __init__(self, number=None, label=None, **kwargs):
		"""Initializes a new Enum object.

		In addition to the named arguments listed below, keyword arguments
		may be given that will be set as attributes on the Enum.

		Args:
			number(int): The integer representation of the Enum. The default
				is to have this number determined dynamically based on its
				place with the parent EnumGroup.
			label(str): The Enum's label. The default is to inherit the
				attribute name the Enum is associated with in its parent
				EnumGroup.
		"""
		self._creationOrder = Enum._CREATIONORDER
		Enum._CREATIONORDER += 1
		self._name = None
		self._number = number
		self._label = label
		self._labelIndex = None
		self._cmpLabel = None
		self._cmpName = None
		self._enumGroup = None
		if kwargs:
			self.__dict__.update(kwargs)

	@property
	def name(self):
		"""The name of the Enum."""
		return self._name

	@property
	def number(self):
		"""The number representation of the Enum."""
		return self._number

	@property
	def label(self):
		"""The Enum's label."""
		return self._label

	@property
	def labelIndex(self):
		"""The Enum's index within its parent EnumGroup."""
		return self._labelIndex

	def _setName(self, name):
		if name == None:
			self._name = None
			self._cmpName = None
		else:
			self._name = name
			self._cmpName = name.strip('_ ')

	def _setLabel(self, label):
		if label == None:
			self._label = None
			self._cmpLabel = None
		else:
			self._label = label
			self._cmpLabel = label.replace(' ','').replace('_','')

	def __add__(self, other):
		return self.__or__(other)

	def __and__(self, other):
		if isinstance(other, Enum):
			other = int(other)
		return int(self) & other

	def __call__(self):
		return int(self)

	def __cmp__(self, value):
		if not isinstance(value, Enum):
			return -1
		return self.number - value.number

	def __eq__(self, value):
		if value == None:
			return False
		if isinstance(value, Enum):
			return self.number == value.number
		if isinstance(value, int):
			return self.number == value
		if isinstance(value, str) or isinstance(value, unicode):
			if self._compareStr(value):
				return True
		return False

	def __hash__(self):
		return self.number

	def __index__(self):
		return self.number

	def __int__(self):
		return self.number

	def __invert__(self):
		return ~int(self)

	def __ne__(self, value):
		return not self.__eq__(value)
	
	def __nonzero__(self):
		return bool(int(self))

	def __or__(self, other):
		o = other
		if isinstance(other, Enum):
			o = int(other)
		value = int(self) | o
		label = '{0} {1}'.format(str(self), str(other))
		name = '{0}_{1}'.format(str(self), str(other))
		class CompositeEnum(Enum):
			def __init__(ss, number, lbl, name):
				super(CompositeEnum, ss).__init__(number, lbl)
				ss._name = name
		# Register our composite enum class as a virtual
		# subclass of this enum's class, plus the same for
		# the other enum if it's an Enum object.  This
		# will make the composite enum isinstance check true
		# against both.
		self.__class__.register(CompositeEnum)
		if isinstance(other, Enum):
			other.__class__.register(CompositeEnum)
		return CompositeEnum(value, label, name)

	def __rand__(self, other):
		if isinstance(other, Enum):
			other = int(other)
		return other & int(self)

	def __repr__(self):
		return '<{mdl}.{cls}.{name}>'.format(
			mdl=self.__class__.__module__,
			cls=self.__class__.__name__,
			name=str(self.name),
		)

	def __ror__(self, other):
		return self | other

	def __rxor__(self, other):
		return self ^ other

	def __str__(self):
		if self.name:
			return self.name
		else:
			return self.label

	def __xor__(self, other):
		if isinstance(other, Enum):
			other = int(other)
		return int(self) ^ other

	def _compareStr(self, inStr):
		return inStr.replace(' ','').replace('_','') in (self._cmpLabel, self._cmpName)

# =============================================================================

class EnumGroup(object):
	"""A container class for collecting, organizing, and accessing Enums.

	An EnumGroup class is a container for Enum objects.  It provides
	organizational convenience, and in most cases handles the generation
	and assignment of Enum numbers, names, and labels.

	Example:
		class Suit(Enum):
			pass
		
		class Suits(EnumGroup):
			Hearts = Suit()
			Spades = Suit()
			Clubs = Suit()
			Diamonds = Suit()

	The above example outlines defining an enumerator, and grouping
	four of them inside of a group.  This provides a number of things,
	including references by attribute, name, and index.  Also provided
	is an "All" attribute, if one is not explicitly assigned, it will be
	a CompositeEnum of all the defined enums, and compare true against 
	any members of the group via the binary "and" operator. Also provided 
	is an "Nothing" attribute, if one is not explicitly assigned, it 
	compares false against any members of the group and when converted to 
	a int its value will be zero.

	Example:
		# By attribute.
		Suits.Hearts
		
		# By name.
		Suits['Hearts']
		
		suitList = list(Suits)
		
		if Suits.Hearts & Suits.All:
			print "This is true!"

	An EnumGroup can also act as a factory for composite Enum objects.
	If a known composite value is available, like 3, which is the
	combination of enum values 1 and 2, a composite Enum object can
	be constructed.

	Example:
		comp = Suits(3)

		if Suits.Hearts & comp:
			print "This is true!"

		if Suits.Clubs & comp:
			print "This is false!"

	Attributes:
		All: The sum of all members.
	"""
	__metaclass__ = _MetaEnumGroup
	_ENUMERATORS = None
	_copyCount = 1
	All = 0
	Nothing = 0

	def __init__(self):
		raise InstantiationError(
			'Unable to instantiate static class EnumGroup.'
		)

	@classmethod
	def append(cls, *args, **kwargs):
		"""Appends additional enumerators to the EnumGroup.

		New members can be provided as ordered arguments where the
		each Enum's label is used to determine the attribute name, or
		by keyword arguments where the key is the attribute name and
		the Enum is the value.  When using an Enum's label to determine
		its name, any spaces in the label will be converted to underscores.

		Example:
			Suits.append(Suit(None, 'Funky'), Foo=Suit())

			# The "Funky" and "Foo" suits are now available.
			Suits.Funky
			Suits.Foo

		Raises:
			ValueError
		"""
		if [e for e in (list(args) + kwargs.values()) if not isinstance(e, Enum)] :
			raise ValueError('Given items must be of class Enum.')
		if [e for e in args if not e.label]:
			raise ValueError('Enums given as ordered arguments must have a label.')
		for e in args:
			setattr(cls, cls._labelToVarName(e.label), e)
		for n, e in kwargs.iteritems():
			setattr(cls, n, e)
		cls.__init_enums__()

	@classmethod
	def copy(cls, name=None):
		""" Returns a new class type from this class without any Enums assigned.
		
		If name is not provided it will automatically generate a new class name.
		For example if the EnumGroup class named DefaultEnums has been copied
		twice the new class name will be "DefaultEnums_3".
		If you provide name it will not check for duplicates.
		
		Args:
			name (str|None): The name to give the new class. Defaults to None
		
		Returns:
			EnumGroup: A new Class type.
		"""
		if not name:
			# Generate a unique name for the class if one was not provided
			name = '{name}_{count}'.format(name=cls.__name__, count=cls._copyCount)
			cls._copyCount += 1
		return type(name, cls.__bases__, dict(cls.__dict__)) 

	@classmethod
	def fromLabel(cls, label, default=None):
		"""Gets an enumerator based on the given label.

		If a default is provided and is not None, that value will be returned
		in the event that the given label does not exist in the EnumGroup.  If
		no default is provided, a ValueError is raised.

		Args:
			label(str): The label to look up.
			default(*): The default value to return if the label is not found.

		Raises:
			ValueError: Raised if default is None and the given label does not
				exist in the EnumGroup.

		Returns:
			Enum
		"""
		label = str(label)
		for e in cls._ENUMERATORS:
			if e.label == label:
				return e
		if default is not None:
			return default
		raise ValueError('No enumerators exist with the given label.')

	@classmethod
	def fromValue(cls, value, default=None):
		"""Gets an enumerator based on the given value.

		If a default is provided and is not None, that value will be returned
		in the event that the given label does not exist in the EnumGroup.  If
		no default is provided, a ValueError is raised.

		Args:
			value(int): The value to look up.
			default(*): The default value to return if the label is not found.

		Raises:
			ValueError: Raised if default is None and the given label does not
				exist in the EnumGroup.

		Returns:
			Enum
		"""
		value = int(value)
		for e in cls._ENUMERATORS:
			if int(e) == value:
				return e
		if default is not None:
			return default
		raise ValueError('No enumerators exist with the given value.')

	@classmethod
	def join(cls, include=None, separator=','):
		"""Joins all child Enums together into a single string.

		The string representation of each Enum is joined using the
		given separator.

		Args:
			include(int|Enum): Only enumerators that compare via bitwise "and" against
				the given int or Enum will be returned.  Default is EnumGroup.All.
			separator(str): The separator to use.  Default is ",".

		Returns:
			str: The joined enumerators.
		"""
		include = include == None and cls.All or include
		return str(separator).join([str(e) for e in cls._ENUMERATORS if e & int(include)])

	@classmethod
	def labels(cls):
		"""A generator containing all Enum labels in the EnumGroup."""
		return (e.label for e in cls._ENUMERATORS)

	@classmethod
	def names(cls):
		"""A generator containing all Enum names in the EnumGroup."""
		return (e.name for e in cls._ENUMERATORS)

	@classmethod
	def split(cls, string, separator=','):
		"""Splits the given string and returns the corresponding Enums.

		The string is split using the provided separator, and all names
		contained within must be attributes of the EnumGroup class that
		is performing the split.

		Args:
			string(str): The string containing the desired Enum names.
			separator(str): The separator to split on.  Default is ','.

		Raises:
			AttributeError

		Returns:
			list(Enum, ...): The list of resulting Enum objects.
		"""
		names = str(string).split(str(separator))
		return [getattr(cls, n) for n in names]

	@classmethod
	def values(cls):
		"""A generator containing all Enum values in the EnumGroup."""
		return (int(e) for e in cls._ENUMERATORS)

	@classmethod
	def __init_enums__(cls):
		enums = []

		orderedEnums = sorted(
			[(k,v) for k,v in cls.__dict__.iteritems() if isinstance(v,Enum)],
			key=lambda i:i[1]._creationOrder,
		)
		for name, value in orderedEnums:
			enums.append(value)
			value._enumGroup = cls
			value._setName(name)
			if value.label is None:
				value._setLabel(cls._varNameToLabel(name))
		enumNumbers = [enum.number for enum in enums if enum.number]
		num = 1
		for enum in enums:
			if enum._number == None:
				while num in enumNumbers:
					num *= 2
				enum._number = num
				enumNumbers.append(num)
		enums.sort()
		labelIndex = 0
		for enum in enums:
			if enum._label != None:
				enum._labelIndex = labelIndex
				labelIndex += 1
		cls._ENUMERATORS = enums
		# Build the All object if its not defined
		if isinstance(cls.All, int):
			for e in enums:
				if isinstance(cls.All, int):
					cls.All = e
				else:
					cls.All |= e
		# Build the Nothing object if its not defined
		if isinstance(cls.Nothing, int) and enums:
			processed = set()
			for i, enum in enumerate(enums):
				enumClass = enum.__class__
				if i == 0:
					# Create the Nothing instance from the first class type
					cls.Nothing = enumClass(0, 'Nothing')
				elif enumClass not in processed:
					# Register our Nothing enum's class as a virtual
					# subclass of any additional enum classes. This
					# will make the Nothing enum isinstance check true
					# against all Enums in this EnumGroup.
					enumClass.register(cls.Nothing.__class__)
				processed.add(enumClass)
			

	@classmethod
	def _varNameToLabel(cls, varName):
		label = str(varName)
		label = ' '.join(re.findall('[A-Z]+[^A-Z]*', label))
		label = re.sub(r'[_\s]+', ' ', label)
		return label

	@classmethod
	def _labelToVarName(cls, label):
		name = str(label)
		name = re.sub(r'\s+', '_', name)
		return name

# =============================================================================
class Incrementer(object):
	""" A class that behaves similarly to c i++ or ++i.
	
	Once you init this class, every time you call it it will update count and return the previous 
	value like c's i++. If you pass True to pre, it will increment then return the new value like
	c's ++i.
	
	Args:
		start (int): Start the counter at this value. Defaults to Zero.
		increment (int): increment by this value. In most cases it should be 1 or -1. Defaults to one.
		pre (bool): If true calling the object will return the incremented value. If False it will 
			return the current value and increment for the next call. Defaults to False.
	
	Attributes:
		count: The current value.
		increment: The incremnt added to count
		pre: Should it preform a ++i or i++ operation when called.
	"""
	def __init__(self, start=0, increment=1, pre=False):
		super(Incrementer, self).__init__()
		self.count = start
		self.increment = increment
		self.pre = pre
	
	def __call__(self):
		if self.pre:
			self.count +=self.increment
			return self.count
		ret = self.count
		self.count +=self.increment
		return ret
# =============================================================================

class enum(object):
	"""DEPRECATED: Python based enumerator class.

	This class is deprecated and should be replaced by blurdev.enum.Enum and
	blurdev.enum.EnumGroup.

	A short example::

		>>> Colors = enum("Red", "Yellow", "Blue")
		>>> Color.Red
		1
		>>> Color.Yellow
		2
		>>> Color.Blue
		4
		>>> Color.labelByValue(Color.Blue)
		'Blue'
	"""
	INDICES = xrange(sys.maxint)  # indices constant to use for looping

	def __call__(self, key):
		return self.value(key)

	def __getattr__(self, key):
		if key == '__name__':
			return 'enum'
		else:
			raise AttributeError, key

	def __init__(self, *args, **kwds):
		""" Takes the provided arguments adds them as properties of this object. For each argument you
		pass in it will assign binary values starting with the first argument, 1, 2, 4, 8, 16, ....
		If you pass in any keyword arguments it will store the value.
		
		Note: Labels automatically add spaces for every capital letter after the first, so do not use
		spaces for args, or the keys of kwargs or you will not be able to access those parameters.
		
		:param *args: Properties with binary values are created
		:param **kwds: Properties with passed in values are created
		
		Example::
			>>> e = blurdev.enum.enum('Red', 'Green', 'Blue', White=7)
			>>> e.Blue
			4
			>>> e.White
			7
			>>> e.Red | e.Green | e.Blue
			7
		"""
		super(enum, self).__init__()
		self._keys = list(args) + kwds.keys()
		self._compound = kwds.keys()
		self._descr = {}
		key = 1
		for i in range(len(args)):
			self.__dict__[args[i]] = key
			key *= 2

		for kwd, value in kwds.items():
			self.__dict__[kwd] = value
		
		if not ('All' in args or 'All' in kwds):
			out = 0
			for k in self._keys:
				if isinstance(self.__dict__[k], int):
					out |= self.__dict__[k]
			self.__dict__['All'] = out

	def count(self):
		return len(self._keys)

	def description(self, value):
		""" Returns the description string for the provided value
		:param value: The binary value of the description you want
		"""
		return self._descr.get(value, '')

	def matches(self, a, b):
		""" Does a binary and on a and b
		:param a: First item
		:param b: Second item
		:returns: boolean
		"""
		return (a & b != 0)

	def hasKey(self, key):
		return key in self._keys

	def labels(self, byVal=False):
		""" Returns a list of all provided parameters.
		:param byVal: Sorts the labels by their values. Defaults to False
		:returns: A list of labels as strings
		"""
		if byVal:
			return [' '.join(re.findall('[A-Z]+[^A-Z]*', key)) for key in sorted(self.keys(), key=lambda i:getattr(self, i))]
		return [' '.join(re.findall('[A-Z]+[^A-Z]*', key)) for key in self.keys()]

	def labelByValue(self, value):
		""" Returns the label for a specific value. Labels automatically add spaces
		for every capital letter after the first.
		:param value: The value you want the label for
		"""
		return ' '.join(re.findall('[A-Z]+[^A-Z]*', self.keyByValue(value)))

	def isValid(self, value):
		""" Returns True if this value is stored in the parameters.
		:param value: The value to check
		:return: boolean. Is the value stored in a parameter.
		"""
		return self.keyByValue(value) != ''

	def keyByIndex(self, index):
		""" Finds the key based on a index. This index contains the *args in the order they were passed in
		then any **kwargs's keys in the order **kwargs.keys() returned. This index is created when the class
		is initialized.
		:param index: The index to lookup
		:returns: The key for the provided index or a empty string if it was not found.
		"""
		if index in range(self.count()):
			return self._keys[index]
		return ''

	def keyByValue(self, value):
		""" Return the parameter name for a specific value. If not found returns a empty string.
		:param value: The value to find the parameter name of.
		:returns: String. The parameter name or empty string.
		"""
		for key in self._keys:
			if self.__dict__[key] == value:
				return key
		return ''

	def keys(self):
		""" Returns a list of parameter names
		"""
		return self._keys

	def value(self, key, caseSensitive=True):
		""" Return the value for a parameter name
		:param key: The key to get the value for
		:param caseSensitive: Defaults to True
		:returns: The value for the key, or zero if it was not found
		"""
		if caseSensitive:
			return self.__dict__.get(str(key), 0)
		else:
			key = str(key).lower()
			for k in self.__dict__.keys():
				if k.lower() == key:
					return self.__dict__[k]
			return 0

	def values(self):
		""" Returns a list of all values for stored parameters
		"""
		return [self.__dict__[key] for key in self.keys()]

	def valueByLabel(self, label, caseSensitive=True):
		"""
		Return the binary value fromt the given label.
		:param label: The label you want the binary value of
		:param caseSensitive: Defaults to True
		:returns: the bindary value of the label as a int
		"""
		return self.value(''.join(str(label).split(' ')), caseSensitive=caseSensitive)

	def valueByIndex(self, index):
		""" Returns the stored value for the index of a parameter.
		.. seealso:: :meth:`keyByValue`
		.. seealso:: :meth:`value`
		"""
		return self.value(self.keyByIndex(index))

	def index(self, key):
		""" Return the index for a key.
		:param key: The key to find the index for
		:returns: Int, The index for the key or -1
		.. seealso:: :meth:`keyByValue`
		"""
		if key in self._keys:
			return self._keys.index(key)
		return -1

	def indexByValue(self, value):
		""" Return the index for a value.
		:param value: The value to find the index for
		:returns: Int, the index of the value or -1
		.. seealso:: :meth:`keyByValue`
		"""
		for index in range(len(self._keys)):
			if (self.__dict__[ self._keys[index] ] == value):
				return index
		return -1

	def toString(self, value, default='None', sep=' '):
		""" For the provided value return the parameter name(s) seperated by sep. If you provide
		a int that represents two or more binary values, it will return all parameter names that
		binary value represents seperated by sep. If no meaningful value is found it will return
		the provided default.
		:param value: The value to return parameter names of
		:param default: If no parameter were found this is returned. Defaults to 'None'
		:param sep: The parameters are joined by this value. Defaults to a space.
		:return: Returns a string of values or the provided default
		.. seealso:: :meth:`fromString`
		"""
		parts = []
		for key in self._keys:
			if (not key in self._compound and value & self.value(key)):
				parts.append(key)
		if parts:
			return sep.join(parts)
		return default

	def fromString(self, labels, sep=' '):
		""" Returns the value for a given string. This function binary or's the parameters, so it 
		may not work well when using **kwargs
		:param labels: A string of parameter names.
		:param sep: The seperator used to seperate the provided parameters.
		:returns: The found value
		.. seealso:: :meth:`value`
		.. seealso:: :meth:`toString`
		"""
		parts = str(labels).split(sep)
		value = 0
		for part in parts:
			value |= self.value(part)
		return value

	def setDescription(self, value, descr):
		""" Used to set a description string for a value.
		:param value: The parameter value to set the description on
		:param descr: The description string to set on a parameter
		"""
		self._descr[ value ] = descr

	matches = classmethod(matches)

# =============================================================================
# EXCEPTIONS
# =============================================================================

class InstantiationError(Exception):
	pass

# =============================================================================
