"""
	Namespace:
		blur3d.api.classes.timecode

	Remarks:
		Module for dealing with timecode, including conversions.

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
	SEC_PER_HOUR = 3600
	SEC_PER_MIN = 60

	def __init__(self, hours=0, minutes=0, seconds=0, frames=0, framerate=29.97):
		# Initialize hmsf and framerate to 0 and then use property functions to
		# set so that we can ensure we 
		self._hours = 0
		self._minutes = 0
		self._seconds = 0
		self._frames = 0
		self._framerate = 0
		self.hours = hours
		self.minutes = minutes
		self.seconds = seconds
		self.frames = frames
		self.framerate = framerate

	@property
	def hours(self):
		return self._hours
	@hours.setter
	def hours(self, value):
		if isinstance(value, int):
			self._hours = value
		else:
			self._hours = math.floor(float(value))

	@property
	def minutes(self):
		return self._minutes
	@minutes.setter
	def minutes(self, value):
		if isinstance(value, int):
			self._minutes = value
		else:
			# This is probably wrong...
			self._hours = value // 60
			self._minutes = value % 60
			self._seconds = value * 60 % 60
			self._frames = value * 60 * self.framerate % self.framerate

	@property
	def seconds(self):
		return self._seconds
	@seconds.setter
	def seconds(self, value):
		if isinstance(value, int):
			self._seconds = value
		else:
			# This is probably wrong...
			self._hours = int(value // self.SEC_PER_HOUR)
			self._minutes = int(value // self.SEC_PER_MIN % self.SEC_PER_MIN)
			self._seconds = int(value % self.SEC_PER_MIN)
			self._frames = (value * self.framerate) % self.framerate

	@property
	def frames(self):
		return self._frames
	@frames.setter
	def frames(self, value):
		if isinstance(value, int):
			self._frames = value
		else:
			# TODO THIS
			pass

	@property
	def framerate(self):
		return self._framerate
	@framerate.setter
	def framerate(self, value):
		self._framerate = float(value)

	def __str__(self):
		return ':'.join([str(self.hours), str(self.minutes), str(self.seconds), str(self.frames)])

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
			hours=int(groupdict['hours']),
			minutes=int(groupdict['minutes']),
			seconds=int(groupdict['seconds']),
			frames=int(groupdict['frames']),
			framerate=framerate
		)

	@classmethod
	def fromSeconds(cls, sec, framerate=29.97):
		nHours = int(sec // cls.SEC_PER_HOUR)
		nMinutes = int(sec // cls.SEC_PER_MIN % cls.SEC_PER_MIN)
		nSeconds = int(sec % cls.SEC_PER_MIN)
		nFrames = (sec * framerate) % framerate
		return cls(
			hours=nHours,
			minutes=nMinutes,
			seconds=nSeconds,
			frames=nFrames,
			framerate=framerate
		)

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