##
#   \namespace  cross3d.classes.valuerange
#
#   \remarks    This module holds the ValueRange class to handle value ranges.
#
#   \author     douglas
#   \author     Blur Studio
#   \date       02/17/16
#

#------------------------------------------------------------------------------------------------------------------------

class ValueRange(list):

	def __init__(self, *args):
		"""
			\remarks	Initialize the class.
		"""
		args = list(args)

		if not len(args) == 2:
			raise TypeError('ValueRange object takes two floats. You provided {} arguments.'.format(len(args)))

		try:
			args[0] = float(args[0])
			args[1] = float(args[1])

		except ValueError:
			raise TypeError('ValueRange object takes two floats.')

		super(ValueRange, self).__init__(args)

	def __repr__(self):
		"""
			\remarks	Affects the class representation.
		"""
		return 'cross3d.ValueRange( %s, %s )' % (self[0], self[1])

	def __eq__(self, other):
		if isinstance(other, ValueRange):
			return self[0] == other[0] and self[1] == other[1]
		return False

	def __mult__(self, other):
		if isinstance(other, (float, int)):
			return ValueRange(self[0] * other, self[1] * other)
		raise ValueError('Unable to multiply a ValueRange by {}.'.format(str(type(other))))

	def __nonzero__(self):
		return bool(self.duration())

	def round(self):
		self[0] = round(self[0])
		self[1] = round(self[1])

	def rounded(self):
		return ValueRange(round(self[0]), round(self[1]))

	def string(self, separator='-'):
		"""
			\remarks	Returns the range in its string form.
			\param		separator <string>
		"""
		return '%i%s%i' % (self[0], separator, self[1])

	def start(self):
		return self[0]

	def end(self):
		return self[1]

	def duration(self):
		return self[1] - self[0] + 1

	def isWithin(self, valueRange):
		if self[0] >= valueRange[0] and self[1] <= valueRange[1]:
			return True
		return False

	def contains(self, valueRange):
		if self[0] <= valueRange[0] and self[1] >= valueRange[1]:
			return True
		return False

	def offsets(self, valueRange):
		return ValueRange((valueRange[0] - self[0]), (valueRange[1] - self[1]))

	def overlaps(self, valueRange, tolerance=0):
		"""
			\remarks	Returns weather the ranges overlaps.
			\param		separator <string>
		"""
		if self[0] + tolerance >= valueRange[1] or self[1] - tolerance <= valueRange[0]:
			return False
		return True

	def extends(self, valueRange):
		"""
			\remarks	Returns weather the range includes additional frames.
		"""
		return self[0] < valueRange[0] or self[1] > valueRange[1]

	def overlap(self, valueRange):
		"""
			\remarks	Returns the overlaping range if any.
		"""
		if self.overlaps(valueRange):
			if self[0] < valueRange[0]:
				start = valueRange[0]
			else:
				start = self[0]
			if self[1] > valueRange[1]:
				end = valueRange[1]
			else:
				end = self[1]
			return ValueRange(start, end)
		else:
			None

	def multiplied(self, multiplier):
		return ValueRange(self[0] * multiplier, self[1] * multiplier)

	def merged(self, valueRange):
		"""
			\remarks	Returns a range that covers both framerange.
		"""
		return ValueRange(min(self[0], valueRange[0]), max(self[1], valueRange[1]))

	def padded(self, padding):
		"""
			\remarks	Returns the padded range.
		"""
		if isinstance(padding, (list, tuple)) and len(padding) >= 2:
			return ValueRange(self[0] - padding[0], self[1] + padding[1])
		return ValueRange(self[0] - padding, self[1] + padding)

	def offseted(self, offset):
		"""
			\remarks Returns the offset range.
		"""
		return ValueRange(self[0] + offset, self[1] + offset)
