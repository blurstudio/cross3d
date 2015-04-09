import os
import math
import hashlib
import blurdev
import xml.dom.minidom

from framerange import FrameRange
from blur3d.constants import ControllerType
from blurdev.XML.xmldocument import XMLDocument
from blurdev.XML.xmlelement import XMLElement

class Key(object):

	def __init__(self, **kwargs):
		self.value = float(kwargs.get('value', 0.0))
		self.time = float(kwargs.get('time', 0.0))

		# Tangent angles are sorted in radians.
		self.inTangentAngle = float(kwargs.get('inTangentAngle', 0.0))
		self.outTangentAngle = float(kwargs.get('outTangentAngle', 0.0))
		self.inTangentType = str(kwargs.get('inTangentType', 0))
		self.outTangentType = str(kwargs.get('outTangentType', 0))
		self.outTangentLength = float(kwargs.get('outTangentLength', 0.0))
		self.inTangentLength = float(kwargs.get('inTangentLength', 0.0))

		# Normalized tangents scale based on the distance to the key they are pointing to.
		self.normalizedTangents = bool(kwargs.get('normalizedTangents', True))

		# Broken key allows to have manipulate tangent individually.
		self.brokenTangents = bool(kwargs.get('brokenTangents', False))

class FCurve(object):

	def __init__(self, name='', tpe=ControllerType.BezierFloat):
		self._name = name
		self._type = tpe
		self._keys = []
		
	def offset(self, value, attr='time', rnd=False):
		for key in self._keys:
			v = getattr(key, attr) + float(value)
			v = round(v) if rnd else v
 			setattr(key, attr, v)

	def keys(self):
		return self._keys

	def scale(self, value, attr='time', pivot=0.0, rnd=False):
		for key in self._keys:

			# Scaling the attribute.
			v = (getattr(key, attr) - pivot) * value + pivot
			v = round(v) if rnd else v
			setattr(key, attr, v)

			# Getting the tangents time and value.
			inTangentTime = math.cos(key.inTangentAngle) * key.inTangentLength
			inTangentValue = math.sin(key.inTangentAngle) * key.inTangentLength
			outTangentTime = math.cos(key.outTangentAngle) * key.outTangentLength
			outTangentValue = math.sin(key.outTangentAngle) * key.outTangentLength

			# Scaling the right tangent components.
			if attr == 'time':
				inTangentTime *= value
				outTangentTime *= value
			elif attr == 'value':
				inTangentValue *= value
				outTangentValue *= value

			# Setting the tangent data on the keys.
			key.inTangentAngle = math.atan2(inTangentValue, inTangentTime)
			key.inTangentLength = math.sqrt(inTangentValue**2 + inTangentTime**2)
			key.outTangentAngle = math.atan2(outTangentValue, outTangentTime)
			key.outTangentLength = math.sqrt(outTangentValue**2 + outTangentTime**2)

	def remap(self, rng, attr='time', rnd=False):
		start = getattr(self._keys[0], attr)
		end = getattr(self._keys[-1], attr)

		# Difference is not the same as duration.
		difference = float(end - start)
		ratio = (rng[1] - rng[0]) / difference
		self.scale(ratio, attr=attr, rnd=rnd, pivot=start)
		self.offset(rng[0]-start, attr=attr, rnd=rnd)

	def round(self, attr='time'):
		for key in self._keys:
			v = getattr(key, attr)
 			setattr(key, attr, round(v))

	def invert(self, conversionRatio=1.0):
		""" Inverse time and values of each key.

		Args:
			conversionRatio(float): The conversion ratio to go from Y to X.
			For example you might want to inverse a curve where frames on X are expressed in seconds on Y.
			The X values will need to be divided by a frame rate to become meaningful Y values.
			On the other hand Y values will have to be multiplied by that same ratio to become meaningful X values.
		"""

		# Before we flip we rationalize the Y axis based on provided conversion ratio.
		if conversionRatio and conversionRatio != 1.0:
			self.scale(conversionRatio, attr='value')

		for key in self._keys:
			time = key.time
			value = key.value

			# Swapping time and value.
			key.time = value
			key.value = time

			# Flipping tangents based on a 45 degrees line.
			key.inTangentAngle = math.pi / 2.0 - key.inTangentAngle
			key.outTangentAngle = math.pi / 2.0 - key.outTangentAngle

		# We revert the scale of the Y axis.
		if conversionRatio and conversionRatio != 1.0:
			self.scale(1 / conversionRatio, attr='value')

	def range(self, attr='time'):
		keys = self._keys
		if len(keys) > 1:
			rng = (getattr(keys[0], attr), getattr(keys[-1], attr))
		else:
			rng = (0, 0)
		return FrameRange(rng)

	def name(self):
		return self._name

	def type(self):
		return self._type

	def setType(self, tpe):
		self._type = tpe

	def setName(self, name):
		self._name = name
	
	def addKey(self, **kwargs):
		key = Key(**kwargs)
		self._keys.append(key)
		return self._keys
	
	def __nonzero__(self):
		return bool(self._keys)

	def __eq__(self, other):
		""" Allows to compare to fCurve objects.
		"""
		if isinstance(other, FCurve):

			if blurdev.debug.debugLevel() >= blurdev.debug.DebugLevel.Mid: 
				with open(r'C:\temp\fCurve.xml', 'w') as fle:
					fle.write(self.toXML())
				with open(r'C:\temp\otherFCurve.xml', 'w') as fle:
					fle.write(other.toXML())

			return self.__hash__() == other.__hash__()
		return False

	def __hash__(self):
		return hashlib.sha224(self.toXML()).hexdigest()

	def __ne__(self, other):
		return not self.__eq__(other)

	def fromXML(self, xml):
		""" Loads curve data from an XML document.

		Args:
			xml(string): The xml we want to load on the curve.
		"""

		# If the document is a path we try to load the XML from that file.
		document = XMLDocument()
		document.parse(xml)

		# Getting the curve element.
		fCurveElement = document.root()

		self._name = fCurveElement.attribute('name')
		self._type = ControllerType.valueByLabel(fCurveElement.attribute('type'))
		self._keys = []

		for element in fCurveElement.children():

			kwargs = { 'time': element.attribute('time'),
					   'value': element.attribute('value'),
					   'inTangentAngle': element.findChild('inTangentAngle').value(),
					   'outTangentAngle': element.findChild('outTangentAngle').value(),
					   'inTangentType': element.findChild('inTangentType').value(),
					   'outTangentType': element.findChild('outTangentType').value(),
					   'inTangentLength': element.findChild('inTangentLength').value(), 
					   'outTangentLength': element.findChild('outTangentLength').value(),
					   'normalizedTangents': element.findChild('normalizedTangents').value() == 'True',
					   'brokenTangents': element.findChild('brokenTangents').value() == 'True' }

			self._keys.append(Key(**kwargs))

	def toXML(self):
		""" Translate the curve data into a XML.
		TODO: I hate the API for XML so I shove most of it here.

		Returns:
			str: The XML data for that curve.
		"""
		document = XMLDocument()
		fCurveElement = document.addNode('fCurve')
		fCurveElement.setAttribute('name', self._name)
		fCurveElement.setAttribute('type', ControllerType.labelByValue(self._type))

		for key in self._keys:

			keyElement = fCurveElement.addNode('key')
			keyElement.setAttribute('value', key.value)
			keyElement.setAttribute('time', key.time)

			properties = { 'inTangentAngle': key.inTangentAngle,
						   'outTangentAngle': key.outTangentAngle,
						   'inTangentType': key.inTangentType,
						   'outTangentType': key.outTangentType,
						   'inTangentLength': key.inTangentLength, 
						   'outTangentLength': key.outTangentLength,
						   'normalizedTangents': key.normalizedTangents,
						   'brokenTangents': key.brokenTangents }

			for prop in sorted(properties.keys()):
				propertyElement = keyElement.addNode(prop)
				propertyElement.setValue(properties[prop])

		return document.toxml()

	def write(self, path):
		if path and isinstance(path, basestring):
			dirname = os.path.dirname(path)
			if not os.path.exists(dirname):
				os.path.makedirs(dirname)

			with open(path, 'w') as fle:
				fle.write(self.toXML())

	def read(self, path):
		with open(path) as fle:
			self.fromXML(fle.read())
		return True

