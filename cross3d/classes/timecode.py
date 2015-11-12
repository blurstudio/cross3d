"""
	Namespace:
		blur3d.api.classes.timecode

	Remarks:
		Module containing Timcode class for dealing with timecode,
			including conversions from/to different formats.

	Author:
		Will Cavanagh
		willc@blur.com
		Blur Studio

	Date:
		2015.11.05
"""

import re
import math

class Timecode(object):
	"""The Timecode class provides blah blah blah

	Attributes:
		blah: something
	"""
	FORMAT_KEY = {
		'H' : '{hours:0.0f}',
		'hh' : '{hours:02.0f}',
		'mm' : '{minutes:02.0f}',
		'ss' : '{seconds:02.0f}',
		'ff' : '{frames:02.0f}'
	}
	PARSE_KEY = {
		'H'	 : '(?P<hours>\d+)',
		'hh' : '(?P<hours>\d{2})',
		'mm' : '(?P<minutes>\d{2})',
		'ss' : '(?P<seconds>\d{2})',
		'ff' : '(?P<frames>\d{2})'
	}
	SEC_PER_MIN = 60
	MIN_PER_HOUR = 60
	SEC_PER_HOUR = 3600


	def __init__(self, hours=0, minutes=0, seconds=0, frames=0, framerate=29.97):
		# Initialize hmsf and framerate to 0 and then use property functions to
		# set so that we can ensure we store a valid timecode.
		self._hours = 0
		self._minutes = 0
		self._seconds = 0
		self._frames = 0
		self._framerate = framerate
		self._formatString = 'hh:mm:ss:ff'
		self.hours = hours
		self.minutes = minutes
		self.seconds = seconds
		self.frames = frames

	def __str__(self):
		return ':'.join([str(self.hours), str(self.minutes), str(self.seconds), str(self.frames)])

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

	def __add__(self, other):
		# TODO if framerates don't match, raise exception?
		return Timecode.fromSeconds(self.toSeconds() + other.toSeconds(), framerate=self.framerate)

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
			self.setFromSeconds(self.toSeconds() + (value * self.SEC_PER_HOUR))

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
		self.setFromSeconds(self.toSeconds() + (value * self.SEC_PER_MIN))

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
		self.setFromSeconds(self.toSeconds() + (value / self.framerate))

	def setFromSeconds(self, sec):
		"""Set the timecode component values given a number of seconds.

		Args:
					secs(float): The number of seconds to set this Timecode instance based on.
		"""
		self._hours = int(sec // self.SEC_PER_HOUR)
		self._minutes = int(sec // self.SEC_PER_MIN % self.MIN_PER_HOUR)
		self._seconds = int(sec % self.SEC_PER_MIN)
		self._frames = (sec * self.framerate) % self.framerate

	@property
	def framerate(self):
		"""Get Timcode Framerate."""
		return self._framerate

	def setFramerate(self, newFramerate):
		"""Sets the Timcode Framerate, leaving the frames value unaffected, but converting any
			overflow created by the change into seconds."""
		self._framerate = newFramerate

	def convertToFramerate(self, newFramerate):
		frames = float(self.frames) / self.framerate
		self.frames = frames * newFramerate
		self._framerate = newFramerate

	@property
	def formatString(self):
		return self._formatString
	@formatString.setter
	def formatString(self, value):
		# TODO validate format string?
		self._formatString = value

	@classmethod
	def fromString(cls, string, formatString='hh:mm:ss:ff', framerate=29.97):
		pattern = re.compile(r'\b(' + '|'.join(cls.PARSE_KEY.keys()) + r')\b')
		parserRegex = pattern.sub(lambda x: cls.PARSE_KEY[x.group()], formatString)
		match = re.match(parserRegex, string)
		groupdict = match.groupdict()
		if not (
			'hours' 	in groupdict and
			'minutes' 	in groupdict and
			'seconds' 	in groupdict and
			'frames' 	in groupdict
			):
			raise ValueError('Invalid format string specified.')
		return cls(
			hours=groupdict['hours'],
			minutes=groupdict['minutes'],
			seconds=groupdict['seconds'],
			frames=groupdict['frames'],
			framerate=framerate
		)

	def toString(self, formatString=None):
		#if not formatString:
		#	formatString = self.formatString
		# TEMPORARY FIX FOR GENERATING REPORTS
		return '{hours:0.0f}:{minutes:02.0f}:{seconds:02.0f}:{frames:02.0f}'.format(
			hours=self.hours,
			minutes=self.minutes,
			seconds=self.seconds,
			frames=self.frames
		)

	@classmethod
	def fromSeconds(cls, sec, framerate=29.97):
		instance = cls(framerate=framerate)
		instance.setFromSeconds(sec)
		return instance

	# @classmethod
	# def fromFrames(cls, frm, framerate=29.97):
	# 	nHours = 0
	# 	nMinutes = 0
	# 	nSeconds = 0
	# 	nFrames = 0
	# 	return cls(
	# 		hours=nHours,
	# 		minutes=nMinutes,
	# 		seconds=nSeconds,
	# 		frames=nFrames,
	# 		framerate=framerate
	# 	)

	def toSeconds(self):
		secs = self.seconds
		secs += self.hours * self.SEC_PER_HOUR
		secs += self.minutes * self.SEC_PER_MIN
		secs += float(self.frames) / self.framerate
		return secs

	def toFrames(self):
		secs = self.seconds
		secs += self.hours * self.SEC_PER_HOUR
		secs += self.minutes * self.SEC_PER_MIN
		return self.frames + self.framerate * secs

def intmodf(value):
	"""Convenience wrapper around math.modf that returns a float remainder and int
		whole portion."""
	modf = math.modf(value)
	return (modf[0], int(modf[1]))
