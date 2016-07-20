##
#   \namespace  cross3d.classes.framerange
#
#   \remarks    This module holds the FrameRange class to handle frame ranges.
#
#   \author     douglas
#   \author     Blur Studio
#   \date       11/30/11
#

#------------------------------------------------------------------------------------------------------------------------

class FrameRange(list):

	def __init__(self, args=None):
		"""
			\remarks	Initialize the class.
		"""
		if not args:
			args = [0, 0]
		elif len(args) == 1:
			args.append(args[0])
		else:
			args = args[0:2]
		try:
			args = list(args)
			args[0] = int(round(float(args[0])))
			args[1] = int(round(float(args[1])))
		except:
			raise Exception("Arguments %s are not valid." % str(args))
		super(FrameRange, self).__init__(args)

	def __repr__(self):
		"""
			\remarks	Affects the class representation.
		"""
		return 'cross3d.FrameRange( %s, %s )' % (self[0], self[1])

	def __eq__(self, other):
		if isinstance(other, FrameRange):
			return self[0] == other[0] and self[1] == other[1]
		return False

	def __nonzero__(self):
		return bool(range(self[0], self[1]))

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

	def isWithin(self, frameRange):
		if self[0] >= frameRange[0] and self[1] <= frameRange[1]:
			return True
		return False

	def contains(self, frameRange):
		if self[0] <= frameRange[0] and self[1] >= frameRange[1]:
			return True
		return False

	def offsets(self, frameRange):
		return FrameRange([(frameRange[0] - self[0]), (frameRange[1] - self[1])])

	def overlaps(self, frameRange, tolerance=0):
		"""
			\remarks	Returns weather the ranges overlaps.
			\param		separator <string>
		"""
		if self[0] + round(tolerance) >= frameRange[1] or self[1] - round(tolerance) <= frameRange[0]:
			return False
		return True

	def extends(self, frameRange):
		"""
			\remarks	Returns weather the range includes additional frames.
		"""
		return self[0] < frameRange[0] or self[1] > frameRange[1]

	def overlap(self, frameRange):
		"""
			\remarks	Returns the overlaping range if any.
		"""

		if self.overlaps(frameRange):

			# TODO: One frame overlap should be considered overlap. 
			# Probably have to use lesser or equal.
			if self[0] < frameRange[0]:
				start = frameRange[0]
			else:
				start = self[0]
			if self[1] > frameRange[1]:
				end = frameRange[1]
			else:
				end = self[1]
			return FrameRange([start, end])
		else:
			None

	def multiply(self, scalar):
		return FrameRange([round(self[0] * scalar), round(self[1] * scalar)])

	def merged(self, frameRange):
		"""
			\remarks	Returns a range that covers both framerange.
		"""
		return FrameRange([min(self[0], frameRange[0]), max(self[1], frameRange[1])])

	def padded(self, padding):
		"""
			\remarks	Returns the padded range.
		"""
		if isinstance(padding, (list, tuple)) and len(padding) >= 2:
			return FrameRange([self[0] - padding[0], self[1] + padding[1]])
		return FrameRange([self[0] - padding, self[1] + padding])

	def offseted(self, offset):
		"""
			\remarks Returns the offset range.
		"""
		return FrameRange([self[0] + offset, self[1] + offset])
