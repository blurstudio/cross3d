"""
	Namespace:
		blur3d.api.classes.timecode

	Remarks:
		Module containing Timcode class for dealing with timecode,
			including conversions from/to different formats.

	Known Bugs:
		- Doesn't support negative timecodes
		- Perhaps should use more precision?  numpy float128?

	Author:
		Will Cavanagh
		willc@blur.com
		Blur Studio

	Date:
		2015.11.05
"""
import re
import math
from blur3d.constants import TimeUnit
from blur3d import pendingdeprecation

class Timecode(object):
	"""Timcode class for dealing with timecode, including conversions from/to different formats.

	Attributes:
		formatString: String used for generating and parsing string representations of this Timecode
			instance.
		framerate:	The framerate used for calculations involving this timecode instance.
		frames:	The frames place value for this timecode instance.
		hours:	The hours place value for this timecode instance.
		minutes:	The minutes place value for this timecode instance.
		seconds:	The seconds place value for this timecode instance.
	"""

	# Store some class-global constants for interpretting time and strings.
	_FORMAT_KEY = {
		'hh' : '{hours:02.0f}',
		'H' : '{hours:0.0f}',
		'Hf' : '{hours}',
		'mm' : '{minutes:02.0f}',
		'M' : '{minutes:0.0f}',
		'Mf' : '{minutes}',
		'ss' : '{seconds:02.0f}',
		'S' : '{seconds:0.0f}',
		'Sf' : '{seconds}',
		'ff' : '{frames:02.0f}',
		'F' : '{frames:0.0f}',
		'Ff' : '{frames}',
	}
	_PARSE_KEY = {
		'hh' : r'(?P<hours>\d{2})',
		'H'	 : r'(?P<hours>\d+)',
		'Hf' : r'(?P<hours>\d+(?:\.\d+)?)',
		'mm' : r'(?P<minutes>\d{2})',
		'M'  : r'(?P<minutes>\d+)',
		'Mf' : r'(?P<minutes>\d+(?:\.\d+)?)',
		'ss' : r'(?P<seconds>\d{2})',
		'S'  : r'(?P<seconds>\d+)',
		'Sf' : r'(?P<seconds>\d+(?:\.\d+)?)',
		'ff' : r'(?P<frames>\d{2})',
		'F'  : r'(?P<frames>\d+)',
		'Ff' : r'(?P<frames>\d+(?:\.\d+)?)',
	}
	_TIME_UNIT_CONVERSION = {
		TimeUnit.Frames : None,
		TimeUnit.Seconds : 1,
		TimeUnit.Milliseconds : 1000,
		TimeUnit.Ticks : 46186158000,
	}
	_DROP_FRAME_RATES = {29.97 : 2, 59.94 : 4}

	_SEC_PER_MIN = 60
	_MIN_PER_HOUR = 60
	_SEC_PER_HOUR = 3600

	def __init__(self, hours=0, minutes=0, seconds=0, frames=0, framerate=29.97, dropFrame=False):
		"""
			Args:
				hours(float):	The number of hours for the new Timecode instance.
				minutes(float):	The number of minutes for the new Timecode instance.
				seconds(float):	The number of seconds for the new Timecode instance.
				frames(float):	The number of frames for the new Timecode instance.
				framerate(float):	The framerate for the new Timecode instance.  If not specified,
					a default of 29.97 (NTSC) will be assumed.
		"""
		# Initialize hmsf and framerate to 0 and then use property functions to
		# set so that we can ensure we store a valid timecode.
		self._frames = 0
		self._framerate = framerate
		self._dropFrame = dropFrame
		self._formatString = 'hh:mm:ss:ff'
		if dropFrame and framerate in self._DROP_FRAME_RATES:
			if (seconds == 0) and (minutes % 10) and (frames < self._DROP_FRAME_RATES[framerate]):
				raise ValueError('Invalid timecode specified -- ensure input is Drop Frame.')
			self._nonDropFramerate = round(framerate)
			f = hours * self._SEC_PER_HOUR * self._nonDropFramerate
			f += minutes * self._SEC_PER_MIN * self._nonDropFramerate
			f -= (minutes // 10) * self._DROP_FRAME_RATES[framerate] * 9
			f -= (minutes % 10) * self._DROP_FRAME_RATES[framerate]
			f += seconds * self._nonDropFramerate
			f += frames
		else:
			f = hours * self._SEC_PER_HOUR * self.framerate
			f += minutes * self._SEC_PER_MIN * self.framerate
			f += seconds * self.framerate
			f += frames
		self._frames = f

	def __str__(self):
		return self.toString()

	def __add__(self, other):
		# We don't need to operate only on timecodes with matching framerates, but it seems safest
		# to require explicit conversion before operating to prevent accidental destruction of
		# framerate information.
		if other.framerate != self.framerate:
			raise ValueError('Timecode framerates do not match.  Perhaps call convertToFramerate first.')
		return Timecode.fromValue(
			self.totalFrames + other.totalFrames,
			timeUnit=TimeUnit.Frames,
			framerate=self.framerate,
			dropFrame=self.dropFrame
		)

	def __sub__(self, other):
		# We don't need to operate only on timecodes with matching framerates, but it seems safest
		# to require explicit conversion before operating to prevent accidental destruction of
		# framerate information.
		if other.framerate != self.framerate:
			raise ValueError('Timecode framerates do not match.  Perhaps call convertToFramerate first.')
		return Timecode.fromValue(
			self.totalFrames - other.totalFrames,
			timeUnit=TimeUnit.Frames,
			framerate=self.framerate,
			dropFrame=self.dropFrame
		)

	def __div__(self, other):
		# We don't need to operate only on timecodes with matching framerates, but it seems safest
		# to require explicit conversion before operating to prevent accidental destruction of
		# framerate information.
		if other.framerate != self.framerate:
			raise ValueError('Timecode framerates do not match.  Perhaps call convertToFramerate first.')
		return Timecode.fromValue(
			self.totalFrames / other.totalFrames,
			timeUnit=TimeUnit.Frames,
			framerate=self.framerate,
			dropFrame=self.dropFrame
		)

	def __mul__(self, other):
		# We don't need to operate only on timecodes with matching framerates, but it seems safest
		# to require explicit conversion before operating to prevent accidental destruction of
		# framerate information.
		if other.framerate != self.framerate:
			raise ValueError('Timecode framerates do not match.  Perhaps call convertToFramerate first.')
		return Timecode.fromValue(
			self.totalFrames * other.totalFrames,
			timeUnit=TimeUnit.Frames,
			framerate=self.framerate,
			dropFrame=self.dropFrame
		)

	def __eq__(self, other):
		"""Equivalency test.  For this we will compare the total frames and framerate directly.
			This means that two Timecode classes representing the same "time" value but in different
			framerates will evaluate as unequal, and for this comparison to evaluate to True
			(a.toSeconds() == b.toSeconds()) should be used instead.  Other comparison operators
			will compare the time value, as this is the most likely expected behavior."""
		if isinstance(other, Timecode):
			return (
				other.totalFrames == self.totalFrames and
				other.framerate == self.framerate
			)
		return False

	def __ne__(self, other):
		return not self.__eq__(other)

	def __lt__(self, other):
		if isinstance(other, Timecode):
			return self.toSeconds() < other.toSeconds()
		return False

	def __gt__(self, other):
		if isinstance(other, Timecode):
			return self.toSeconds() > other.toSeconds()
		return False

	def __le__(self, other):
		if isinstance(other, Timecode):
			return self.toSeconds() <= other.toSeconds()
		return False

	def __ge__(self, other):
		if isinstance(other, Timecode):
			return self.toSeconds() >= other.toSeconds()
		return False


	@classmethod
	@pendingdeprecation('Use fromValue instead.')
	def fromSeconds(cls, sec, framerate=29.97, dropFrame=False):
		"""DEPRECATED: Construct an instance of Timecode given a quantity of seconds."""
		instance = cls(framerate=framerate, dropFrame=dropFrame)
		instance.setFromSeconds(sec)
		return instance

	@classmethod
	def fromString(cls, timecodeString, formatString='hh:mm:ss:ff', framerate=29.97, dropFrame=False):
		"""Construct an instance of Timecode given a string representation of the desired timecode.

			Args:
				timecodeString(str):	The string representation of the desired timecode value.
				formatString(str):	An optional formatting string used to interpret the
					timecode's string representation.
				framerate(float):	The framerate for the new Timecode instance.  If not specified,
					a default of 29.97 (NTSC) will be assumed.

			Returns:
				Timecode: The newly constructed Timecode instance.
		"""
		pattern = re.compile(r'\b(' + '|'.join(cls._PARSE_KEY.keys()) + r')\b')
		parserRegex = pattern.sub(lambda x: cls._PARSE_KEY[x.group()], formatString)
		match = re.match(parserRegex, timecodeString)
		if not match:
			raise ValueError('Invalid format string specified.')
		groupdict = match.groupdict()
		if not (
			'hours' 	in groupdict and
			'minutes' 	in groupdict and
			'seconds' 	in groupdict and
			'frames' 	in groupdict
			):
			raise ValueError('Invalid format string specified.')
		instance = cls(
			hours=groupdict['hours'],
			minutes=groupdict['minutes'],
			seconds=groupdict['seconds'],
			frames=groupdict['frames'],
			framerate=framerate,
			dropFrame=dropFrame
		)
		instance.formatString = formatString
		return instance

	@classmethod
	def fromValue(cls, value, timeUnit=TimeUnit.Seconds, framerate=29.97, dropFrame=False):
		"""Construct an instance of Timecode given a float representation of the desired timecode
			in a specified TimeUnit.

			Args:
				value(float):	The float value representation of the desired timecode.
				timeUnit(TimeUnit):	The time units for the provided value.  If not specified,
					seconds will be assumed.
				framerate(float):	The framerate for the new Timecode instance.  If not specified,
					a default of 29.97 (NTSC) will be assumed.

			Returns:
				Timecode: The newly constructed Timecode instance.
		"""
		if not timeUnit in cls._TIME_UNIT_CONVERSION:
			raise ValueError('Invalid type for argument timeUnit.')
		if timeUnit == TimeUnit.Frames:
			value /= float(framerate)
		else:
			value /= float(cls._TIME_UNIT_CONVERSION[timeUnit])
		instance = cls(framerate=framerate, dropFrame=dropFrame)
		instance.setFromSeconds(value)
		return instance

	@property
	def dropFrame(self):
		"""Get the current dropFrame."""
		return self._dropFrame
	@dropFrame.setter
	def dropFrame(self, value):
		"""Set the dropFrame, a boolean value that will determine whether the timecode is displayed
			and calculated as Drop-Frame."""
		self._dropFrame = bool(value)

	@property
	def formatString(self):
		"""Get the current formatString."""
		return self._formatString
	@formatString.setter
	def formatString(self, value):
		"""Set the formatString, a string that stores the format that the Timecode will be
			represented as when converted to a string."""
		# TODO validate format string?
		self._formatString = value

	@property
	def framerate(self):
		"""Get Timcode Framerate."""
		return self._framerate

	@property
	def frames(self):
		"""Get Timecode Frames place."""
		if self.dropFrame and self.framerate in self._DROP_FRAME_RATES:
			return self._framesWithNonDrop() % self._nonDropFramerate
		else:
			return self._frames % self.framerate
	@frames.setter
	def frames(self, value):
		"""Set Timecode Frames place.  Any overflow or fractional part of the specified value will
			be added to the appropriate timecode component."""
		self._frames += (value - self.frames)

	@property
	def hours(self):
		"""Get Timecode Hours place."""
		if self.dropFrame and self.framerate in self._DROP_FRAME_RATES:
			return self._framesWithNonDrop() // self._nonDropFramerate // self._SEC_PER_HOUR
		else:
			return self._frames // self.framerate // self._SEC_PER_HOUR
	@hours.setter
	def hours(self, value):
		"""Set Timecode Hours place.  If a non-integer value is passed it will be cast to a float,
			converted to seconds and added to the current value before being converted to hmsf."""
		self._frames += (value - self.hours) * self._SEC_PER_HOUR * self.framerate

	@property
	def minutes(self):
		"""Get Timecode Minutes place."""
		if self.dropFrame and self.framerate in self._DROP_FRAME_RATES:
			return self._framesWithNonDrop() // self._nonDropFramerate // self._SEC_PER_MIN % self._MIN_PER_HOUR
		else:
			return self._frames // self.framerate // self._SEC_PER_MIN % self._MIN_PER_HOUR
	@minutes.setter
	def minutes(self, value):
		"""Set Timecode Minutes place.  Any overflow or fractional part of the specified value will
			be added to the appropriate timecode component."""
		self._frames += (value - self.minutes) * self._SEC_PER_MIN * self.framerate

	@property
	def seconds(self):
		"""Get Timecode Seconds place."""
		if self.dropFrame and self.framerate in self._DROP_FRAME_RATES:
			return self._framesWithNonDrop() // self._nonDropFramerate % self._SEC_PER_MIN
		else:
			return self._frames // self.framerate % self._SEC_PER_MIN
	@seconds.setter
	def seconds(self, value):
		"""Set Timecode Seconds place.  Any overflow or fractional part of the specified value will
			be added to the appropriate timecode component."""
		self._frames += (value - self.seconds) * self.framerate

	@property
	def totalFrames(self):
		"""Get the total number of frames represented by this timecode instance."""
		return self._frames
	@totalFrames.setter
	def totalFrames(self, value):
		"""Set the total number of frames for this timecode instance."""
		self._frames = value

	def _framesWithNonDrop(self):
		"""Get the number of frames for this timecode isntance converted to non-dropframe.  For
			example, for 29.97fps DF this will return the number of frames converted to 30fps."""
		frames = self._frames
		if self.dropFrame and self.framerate in self._DROP_FRAME_RATES:
			df = self._DROP_FRAME_RATES[self.framerate]
			framesPer10Min = round(self.framerate * 60 * 10)
			framesPer1Min = round(self.framerate) * 60 - df
			whole = self._frames // framesPer10Min
			partial = self._frames % framesPer10Min
			# 9 sets of DF for each 10 minute increment of frames that have passed
			frames += df * 9 * whole
			if partial > df:
				# Add an additional set of df for each minute left over
				# (we don't need to worry about the 10th minute here, because it
				# will excluded since we're using a modulus.)
				frames += df * ((partial - df) // framesPer1Min)
		return frames

	def convertToFramerate(self, newFramerate):
		"""Sets the Timecode value for the new framerate, based on the time value calculated based
			on the current current framerate.

		Args:
					newFramerate(float): The new framerate to be set.
		"""
		secs = self.toSeconds()
		secs *= (float(self.framerate) / float(newFramerate))
		self.setFromSeconds(secs)
		self._framerate = newFramerate

	def setFramerate(self, newFramerate):
		"""Sets the Timcode Framerate, leaving the frames value unaffected.

		Args:
					newFramerate(float): The new framerate to be set.
		"""
		self._framerate = newFramerate

	def setFromSeconds(self, sec):
		"""Set the timecode component values given a number of seconds.

		Args:
					secs(float): The number of seconds to set this Timecode instance based on.
		"""
		self._frames = int(sec * self.framerate)

	@pendingdeprecation('Use toValue instead.')
	def toFrames(self):
		"""DEPRECATED: Gets the total number of frames represented by the Timecode instance at its
			current framerate."""
		return self.toValue(timeUnit=TimeUnit.Frames)

	def toSeconds(self):
		"""Convert the Timecode object to a float quantity of seconds.

		Returns:
					float: This Timecode instance converted to a float quantity of seconds.
		"""
		secs = float(self._frames) / self.framerate
		return secs

	def toString(self, formatString=None):
		"""Convert the Timecode object to a string, using the provided formatString.  If no
			formatString is specified, the object's formatString attribute will be used instead.

		Args:
					formatString(str): The string that will be used to generate formatting.

		Returns:
					str: String representation of this Timecode instance, formatted based on the
						provided formatString.
		"""
		if not formatString:
			formatString = self.formatString
		pattern = re.compile(r'\b(' + '|'.join(self._FORMAT_KEY.keys()) + r')\b')
		formatting = pattern.sub(lambda x: self._FORMAT_KEY[x.group()], formatString)
		return formatting.format(
			hours=self.hours,
			minutes=self.minutes,
			seconds=self.seconds,
			frames=self.frames
		)

	def toValue(self, timeUnit=TimeUnit.Seconds):
		"""Convert the Timecode object to a float quantity of the specified TimeUnit.  If no
			timeUnit is specified, the Seconds will be used.

		Args:
					timeUnit(blur3d.constants.TimeUnit): The unit of time to quantify by.

		Returns:
					float: This Timecode instance's value in the specified TimeUnit.
		"""
		# If frames are requested, we can pass that directly.  Otherwise, we'll need to
		# convert from seconds to the desired time unit.
		if timeUnit == TimeUnit.Frames:
			return self._frames
		else:
			return self.toSeconds() * self._TIME_UNIT_CONVERSION[timeUnit]
