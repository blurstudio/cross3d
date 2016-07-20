"""
	Namespace:
		cross3d.classes.timecode

	Remarks:
		Module containing Timcode class for dealing with timecode,
			including conversions from/to different formats.

	Known Bugs:
		- Doesn't support negative timecodes

	Author:
		Will Cavanagh
		willc
		Blur Studio

	Date:
		2015.11.05
"""
import re
import math
from cross3d.constants import TimeUnit

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

	_SEC_PER_MIN = 60
	_MIN_PER_HOUR = 60
	_SEC_PER_HOUR = 3600

	def __init__(self, hours=0, minutes=0, seconds=0, frames=0, framerate=29.97):
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
		self._hours = 0
		self._minutes = 0
		self._seconds = 0
		self._frames = 0
		self._framerate = framerate
		self._formatString = 'hh:mm:ss:ff'
		secs = float(hours) * float(self._SEC_PER_HOUR)
		secs += float(minutes) * float(self._SEC_PER_MIN)
		secs += float(seconds)
		secs += float(frames) / float(framerate)
		self.setFromSeconds(secs)

		self.hours = hours
		self.minutes = minutes
		self.seconds = seconds
		self.frames = frames

	def __str__(self):
		return self.toString()

	def __add__(self, other):
		# We don't need to operate only on timecodes with matching framerates, but it seems safest
		# to require explicit conversion before operating to prevent accidental destruction of
		# framerate information.
		if other.framerate != self.framerate:
			raise ValueError('Timecode framerates do not match.  Perhaps call convertToFramerate first.')
		return Timecode.fromValue(self.toSeconds() + other.toSeconds(), framerate=self.framerate)

	def __sub__(self, other):
		# We don't need to operate only on timecodes with matching framerates, but it seems safest
		# to require explicit conversion before operating to prevent accidental destruction of
		# framerate information.
		if other.framerate != self.framerate:
			raise ValueError('Timecode framerates do not match.  Perhaps call convertToFramerate first.')
		return Timecode.fromValue(self.toSeconds() - other.toSeconds(), framerate=self.framerate)

	def __div__(self, other):
		# We don't need to operate only on timecodes with matching framerates, but it seems safest
		# to require explicit conversion before operating to prevent accidental destruction of
		# framerate information.
		if other.framerate != self.framerate:
			raise ValueError('Timecode framerates do not match.  Perhaps call convertToFramerate first.')
		return Timecode.fromValue(self.toSeconds() / other.toSeconds(), framerate=self.framerate)

	def __mul__(self, other):
		# We don't need to operate only on timecodes with matching framerates, but it seems safest
		# to require explicit conversion before operating to prevent accidental destruction of
		# framerate information.
		if other.framerate != self.framerate:
			raise ValueError('Timecode framerates do not match.  Perhaps call convertToFramerate first.')
		return Timecode.fromValue(self.toSeconds() * other.toSeconds(), framerate=self.framerate)

	def __eq__(self, other):
		"""Equivalency test.  For this we will compare all values directly.  This means that
			two Timecode classes representing the same "time" value but in different
			framerates will evaluate as unequal, and for this comparison to evaluate to True
			(a.toSeconds() == b.toSeconds()) should be used instead.  Other comparison operators
			will compare the time value, as this is the most likely expected behavior."""
		if isinstance(other, Timecode):
			return (
				other.hours == self.hours and
				other.minutes == self.minutes and
				other.seconds == self.seconds and
				other.frames == self.frames and 
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
	def fromString(cls, timecodeString, formatString='hh:mm:ss:ff', framerate=29.97):
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
			framerate=framerate
		)
		instance.formatString = formatString
		return instance

	@classmethod
	def fromValue(cls, value, timeUnit=TimeUnit.Seconds, framerate=29.97):
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
		instance = cls(framerate=framerate)
		instance.setFromSeconds(value)
		return instance

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
		return self._frames
	@frames.setter
	def frames(self, value):
		"""Set Timecode Frames place.  Any overflow or fractional part of the specified value will
			be added to the appropriate timecode component."""
		value = float(value)
		# We're supposed to be overwriting our frames place, so reset it.
		self._frames = 0
		self.setFromSeconds(self.toSeconds() + (value / float(self.framerate)))

	@property
	def hours(self):
		"""Get Timecode Hours place."""
		return self._hours
	@hours.setter
	def hours(self, value):
		"""Set Timecode Hours place.  If a non-integer value is passed it will be cast to a float,
			converted to seconds and added to the current value before being converted to hmsf."""
		if isinstance(value, int):
			self._hours = value
		else:
			value = float(value)
			# We're supposed to be overwriting our hours place, so reset it.
			self._hours = 0
			self.setFromSeconds(self.toSeconds() + (value * float(self._SEC_PER_HOUR)))

	@property
	def minutes(self):
		"""Get Timecode Minutes place."""
		return self._minutes
	@minutes.setter
	def minutes(self, value):
		"""Set Timecode Minutes place.  Any overflow or fractional part of the specified value will
			be added to the appropriate timecode component."""
		value = float(value)
		# We're supposed to be overwriting our minutes place, so reset it.
		self._minutes = 0
		self.setFromSeconds(self.toSeconds() + (value * float(self._SEC_PER_MIN)))

	@property
	def seconds(self):
		"""Get Timecode Seconds place."""
		return self._seconds
	@seconds.setter
	def seconds(self, value):
		"""Set Timecode Seconds place.  Any overflow or fractional part of the specified value will
			be added to the appropriate timecode component."""
		value = float(value)
		# We're supposed to be overwriting our seconds place, so reset it.
		self._seconds = 0
		self.setFromSeconds(self.toSeconds() + value)

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
		"""Sets the Timcode Framerate, leaving the frames value unaffected, but converting any
			overflow created by the change into seconds.

		Args:
					newFramerate(float): The new framerate to be set.
		"""
		self._framerate = newFramerate
		# This will make sure that any overflow in our frames caused by a framerate change is
		# accounted for.
		self.setFromSeconds(self.toSeconds())

	def setFromSeconds(self, sec):
		"""Set the timecode component values given a number of seconds.

		Args:
					secs(float): The number of seconds to set this Timecode instance based on.
		"""
		self._hours = int(sec // self._SEC_PER_HOUR)
		self._minutes = int(sec // self._SEC_PER_MIN % self._MIN_PER_HOUR)
		self._seconds = int(sec % self._SEC_PER_MIN)
		f = (sec * self.framerate) % self.framerate
		# check for floating point error in the mod function
		if math.fabs(f - self.framerate) < 1E-10:
			self._frames = 0.0
		else:
			self._frames = f

	def toSeconds(self):
		"""Convert the Timecode object to a float quantity of seconds.

		Returns:
					float: This Timecode instance converted to a float quantity of seconds.
		"""
		secs = self.seconds
		secs += self.hours * self._SEC_PER_HOUR
		secs += self.minutes * self._SEC_PER_MIN
		secs += float(self.frames) / self.framerate
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
					timeUnit(cross3d.constants.TimeUnit): The unit of time to quantify by.

		Returns:
					float: This Timecode instance's value in the specified TimeUnit.
		"""
		# We won't have framerate stored in our unit conversion dictionary since it depends on this
		# instance's framerate.
		if timeUnit == TimeUnit.Frames:
			return self.toSeconds() * self.framerate
		return self.toSeconds() * self._TIME_UNIT_CONVERSION[timeUnit]
