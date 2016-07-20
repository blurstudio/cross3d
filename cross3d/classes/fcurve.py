import os
import math
import hashlib
import xml.dom.minidom

from framerange import FrameRange
from valuerange import ValueRange
from cross3d.constants import ControllerType, TangentType, ExtrapolationType


class Key(object):

	def __init__(self, **kwargs):
		self.value = float(kwargs.get('value', 0.0))
		self.time = float(kwargs.get('time', 0.0))

		# Tangent angles are sorted in radians.
		self.inTangentAngle = float(kwargs.get('inTangentAngle', 0.0))
		self.outTangentAngle = float(kwargs.get('outTangentAngle', 0.0))
		self.inTangentType = int(kwargs.get('inTangentType', TangentType.Automatic))
		self.outTangentType = int(kwargs.get('outTangentType', TangentType.Automatic))
		self.outTangentLength = float(kwargs.get('outTangentLength', 0.0))
		self.inTangentLength = float(kwargs.get('inTangentLength', 0.0))

		# Normalized tangents scale based on the distance to the key they are pointing to.
		self.normalizedTangents = bool(kwargs.get('normalizedTangents', True))

		# Broken key allows to have manipulate tangent individually.
		self.brokenTangents = bool(kwargs.get('brokenTangents', False))

	@property
	def inTangentPoint(self):
		x = self.inTangentLength * math.cos(self.inTangentAngle)
		y = self.inTangentLength * math.sin(self.inTangentAngle)
		return self.time - x, self.value + y

	@property
	def outTangentPoint(self):
		x = self.outTangentLength * math.cos(self.outTangentAngle)
		y = self.outTangentLength * math.sin(self.outTangentAngle)
		return self.time + x, self.value + y


class FCurve(object):

	def __init__(self, **kwargs):
		self._name = unicode(kwargs.get('name', ''))
		self._type = int(kwargs.get('tpe', ControllerType.BezierFloat))
		self._keys = []
		self._inExtrapolation = int(kwargs.get('inExtrapolation', ExtrapolationType.Constant))
		self._outExtrapolation = int(kwargs.get('outExtrapolation', ExtrapolationType.Constant))

	def valueAtTime(self, time):
		"""Returns the value of the fcurve at the specified time
		
		Args:
		    time (float): time at which to evaluate the fcurve.
		
		Returns:
		    float: value of the fcurve at the specified time.
		"""
		# we need to ensure keys is sorted properly for this to work.
		sortedKeys = sorted(self._keys, key=lambda k: k.time)
		# If the time specified is out of the range of keyframes, we'll need to
		# extrapolate to find the value.  This will be split into its own fn since
		# it gets a bit messy.
		if time < sortedKeys[0].time or time > sortedKeys[-1].time:
			return self.extrapolateValue(time)
		i = 0
		t = sortedKeys[i].time
		maxI = len(sortedKeys) - 1
		while t < time and i < maxI:
			i += 1
			t = sortedKeys[i].time
		if t == time:
			# time is at a key -- we can just return that key's value.
			return sortedKeys[i].value
		else:
			# we should have two keys that our time falls between
			k0 = sortedKeys[i - 1]
			k1 = sortedKeys[i]
			return self.bezierEvaluation(k0, k1, time)

	def plot(self, startValue=None, endValue=None, resolution=1.0, plotHandles=True):
		"""Uses matplotlib to generate a plot of the curve, primarily useful for debugging purposes.
		
		Args:
			startValue (float): Starting value for portion of the curve to sample.
			endValue (float): Ending value for portion of the curve to sample.
			resolution (float): Frequency with which to sample the curve.
		"""

		fullRange = self.range()
		startValue = fullRange[0] if startValue is None else startValue
		endValue = fullRange[1] if endValue is None else endValue

		import numpy as np
		import matplotlib.pyplot as plt
		# plot handles, if asked
		if plotHandles:
			for key in self._keys:
				points = zip(key.inTangentPoint, (key.time, key.value), key.outTangentPoint)
				plt.plot(*points, marker='o', color='blue')
				plt.plot(*points, color='black')
		# plot line
		x = np.arange(startValue, endValue, resolution)
		f = np.vectorize(self.valueAtTime)
		plt.plot(x, f(x))
		plt.show()

	def plotted(self, rng, step=1):
		plotted = FCurve()
		for value in xrange(rng[0], rng[1], step):
			self.addKey(time=value, value=self.valueAtTime(value))
		return plotted

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
		self.offset(rng[0] - start, attr=attr, rnd=rnd)

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
		
		# TODO: This will only work for curves whos start at their minumum and ends at their maximum.
		keys = self._keys
		start = getattr(keys[0], attr) if len(keys) > 1 else 0
		end = getattr(keys[-1], attr) if len(keys) > 1 else 0
		return ValueRange(start, end)

	def setExtrapolation(self, extrapolation=[None, None]):
		self._inExtrapolation = extrapolation[0] or self._inExtrapolation
		self._outExtrapolation = extrapolation[1] or self._outExtrapolation

	def extrapolation(self):
		return (self._inExtrapolation, self._outExtrapolation)

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

	def __len__(self):
		return len(self.keys())

	def __nonzero__(self):
		return bool(self.__len__())

	def __eq__(self, other):
		""" Allows to compare to fCurve objects.
		"""
		if isinstance(other, FCurve):

			if cross3d.debugLevel >= cross3d.constants.DebugLevels.Mid:
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
		from cross3d.migrate.XML import XMLDocument
		document = XMLDocument()
		document.parse(xml)

		# Getting the curve element.
		fCurveElement = document.root()

		self._name = fCurveElement.attribute('name')
		self._type = ControllerType.valueByLabel(fCurveElement.attribute('type'))
		self._inExtrapolation = ExtrapolationType.valueByLabel(fCurveElement.attribute('inExtrapolation'))
		self._outExtrapolation = ExtrapolationType.valueByLabel(fCurveElement.attribute('outExtrapolation'))
		self._keys = []

		for element in fCurveElement.children():

			# This guarantees that the XML is somehow valid.
			if element.findChild('inTangentAngle'):

				# Getting tangent types.
				inTangentType = element.findChild('inTangentType').value()
				outTangentType = element.findChild('outTangentType').value()

				# TODO: Remove in a few month. That's for backward compatibility.
				tbc = {'custom': 'Bezier', 'linear': 'Linear', 'auto': 'Automatic', 'step': 'Stepped'}
				if inTangentType in tbc:
					inTangentType = tbc[inTangentType]
				if outTangentType in tbc:
					outTangentType = tbc[outTangentType]

				kwargs = {'time': element.attribute('time'),
					'value': element.attribute('value'),
					'inTangentAngle': element.findChild('inTangentAngle').value(),
					'outTangentAngle': element.findChild('outTangentAngle').value(),
					'inTangentType': TangentType.valueByLabel(inTangentType),
					'outTangentType': TangentType.valueByLabel(outTangentType),
					'inTangentLength': element.findChild('inTangentLength').value(),
					'outTangentLength': element.findChild('outTangentLength').value(),
					'normalizedTangents': element.findChild('normalizedTangents').value() == 'True',
					'brokenTangents': element.findChild('brokenTangents').value() == 'True'}

				self._keys.append(Key(**kwargs))

	def toXML(self):
		""" Translate the curve data into a XML.
		TODO: I hate the API for XML so I shove most of it here.

		Returns:
			str: The XML data for that curve.
		"""
		from cross3d.migrate.XML import XMLDocument
		document = XMLDocument()
		fCurveElement = document.addNode('fCurve')
		fCurveElement.setAttribute('name', self._name)
		fCurveElement.setAttribute('type', ControllerType.labelByValue(self._type))
		fCurveElement.setAttribute('inExtrapolation', ExtrapolationType.labelByValue(self._inExtrapolation))
		fCurveElement.setAttribute('outExtrapolation', ExtrapolationType.labelByValue(self._outExtrapolation))

		for key in self._keys:

			keyElement = fCurveElement.addNode('key')
			keyElement.setAttribute('value', key.value)
			keyElement.setAttribute('time', key.time)

			properties = {'inTangentAngle': key.inTangentAngle,
				'outTangentAngle': key.outTangentAngle,
				'inTangentType': TangentType.labelByValue(key.inTangentType),
				'outTangentType': TangentType.labelByValue(key.outTangentType),
				'inTangentLength': key.inTangentLength,
				'outTangentLength': key.outTangentLength,
				'normalizedTangents': key.normalizedTangents,
				'brokenTangents': key.brokenTangents}

			for prop in sorted(properties.keys()):
				propertyElement = keyElement.addNode(prop)
				propertyElement.setValue(properties[prop])

		return document.toxml()

	def write(self, path):
		if path and isinstance(path, basestring):
			dirname = os.path.dirname(path)
			if not os.path.exists(dirname):
				os.makedirs(dirname)

			with open(path, 'w') as fle:
				fle.write(self.toXML())

	def read(self, path):
		with open(path) as fle:
			self.fromXML(fle.read())
		return True

	def extrapolateValue(self, time):
		"""Returns the value at a given time outside the range of keyframes for the curve, using the
			curve's extrapolation mode for values outside the keyframe range in that direction.
		
		Args:
		    time (float): time at which to calculate the curve's value
		
		Returns:
		    float: Extrapolated value for the curve at the specified time.
		"""
		sortedKeys = sorted(self._keys, key=lambda k: k.time)
		if time >= sortedKeys[0].time and time <= sortedKeys[-1].time:
			raise ValueError('Unable to extrapolate value for time within keyframed curve.')
		t0, t1 = sortedKeys[0].time, sortedKeys[-1].time
		dt = t1 - t0
		dtx = 0
		if time < sortedKeys[0].time:
			# time is before start
			mode = self._inExtrapolation
			if mode == ExtrapolationType.Constant:
				return sortedKeys[0].value
			before = True
			dtx = t0 - time
		else:
			# time is after end
			mode = self._outExtrapolation
			if mode == ExtrapolationType.Constant:
				return sortedKeys[-1].value
			before = False
			dtx = time - t1
		if mode == ExtrapolationType.Linear:
			v = sortedKeys[0].value if before else sortedKeys[-1].value
			tangentLength = sortedKeys[0].outTangentLength if before else sortedKeys[-1].inTangentLength
			if tangentLength:
				# get the angle of the opposite tangent (max doesn't store tangents)
				# for the outer side in this case.
				theta = sortedKeys[0].outTangentAngle if before else sortedKeys[-1].inTangentAngle
				# Now get the inverse angle, since we want to move on the opposite vector
				theta = math.pi - theta
				# delta from the range to our unknown is our triangle's base,
				# theta is the angle, and our y value is the side.
				# Solve for y, and then offset by the value of the last keyframe.
				return dtx * math.tan(theta) + v
			else:
				if len(sortedKeys) == 1:
					return sortedKeys[0].value
				if before:
					x = sortedKeys[1].time - sortedKeys[0].time
					y = sortedKeys[0].value - sortedKeys[1].value
					offset = sortedKeys[0].value
				else:
					x = sortedKeys[-1].time - sortedKeys[-2].time
					y = sortedKeys[-1].value - sortedKeys[-2].value
					offset = sortedKeys[-1].value
				return (y / x) * dtx + offset

		elif mode == ExtrapolationType.Cycled:
			# We're just looping through the existing timeline now, so we can modulus the delta of
			# sample position with the delta of the start/end keyframe times
			tp = dtx % dt
			# If we fell off the beginning, we need to play through backwards
			if before:
				tp = dt - tp
			# Now we can just get the value for the time
			return self.valueAtTime(tp + t0)
		elif mode == ExtrapolationType.CycledWithOffset:
			# This is going to work the same as cycled, except we'll need to add an offset.
			# our position will be the same, but we'll also need a repetition count to multuiply by
			# our offset.
			tp = dtx % dt
			tc = math.floor(dtx / dt) + 1
			offset = tc * (sortedKeys[-1].value - sortedKeys[0].value)
			offset *= (-1 if before else 1)
			# If we fell off the beginning, we need to play through backwards.
			if before:
				tp = dt - tp
			# Now we can just get the value for the time and add our offset
			return self.valueAtTime(tp + t0) + offset
		elif mode == ExtrapolationType.PingPong:
			# Again this will be similar to Cycled, however now we'll need to reverse the looping
			# direction with each cycle.
			tp = dtx % dt
			oddRep = not bool(math.floor(dtx / dt) % 2)
			# If it's an odd numbered repetition, we need to reverse it.
			if (not oddRep and before) or (oddRep and not before):
				tp = dt - tp
			# Now we can just get the value for the time
			return self.valueAtTime(tp + t0)
		else:
			raise ValueError('Unable to extrapolate values: invalid ExtrapolationType found.')

	@staticmethod
	def bezierEvaluation(key0, key1, frame):
		"""Finds the point on a cubic bezier spline at time frame between two keys.
		
		Args:
		    key0 (Key): Starting key for the spline
		    key1 (Key): Ending key for the spline
		    t (float): Time (as a frame) to solve for
		
		Returns:
		    Tuple: Tuple of float values for the x (time) and y (value) coordinates of the resulting
		    		point.
		"""
		# Implementation by Tyler Fox, modified by Will Cavanagh.
		# Based on method described at
		# http://edmund.birotanker.com/monotonic-bezier-curves-for-animation.html
		p0x, p0y = key0.time, key0.value
		p1x, p1y = key0.outTangentPoint
		p2x, p2y = key1.inTangentPoint
		p3x, p3y = key1.time, key1.value

		totalXRecip = 1.0 / (p3x - p0x)
		f = (p1x - p0x) * totalXRecip
		g = (p3x - p2x)  * totalXRecip
		xVal = (frame - p0x) * totalXRecip

		d = 3*f + 3*g - 2
		n = 2*f + g - 1
		r = (n*n - f*d) / (d*d)
		q = ((3*f*d*n - 2*n*n*n) / (d*d*d)) - xVal/d

		discriminant = q*q - 4*r*r*r

		if discriminant >= 0:
			pm = (discriminant**0.5)/2 #plus/minus portion of equation
			# We're able to only use the + portion of the +/- and get an accurate
			# outcome.  Saves steps / logic.
			w = (-q/2 + pm)**(1/3.0)
			u = w + r/w
		else:
			theta = math.acos(-q / ( 2*r**(3/2.0)) )
			phi = theta/3 + 4*math.pi/3 
			u = 2 * r**(0.5) * math.cos(phi)

		t = u + n/d
		t1 = 1-t
		return (t1**3*p0y + 3*t1**2*t*p1y + 3*t1*t**2*p2y + t**3*p3y)
