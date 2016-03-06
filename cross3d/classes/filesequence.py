##
#	\namespace	blur3d.api.classes.filesequence
#
#	\remarks	This file defines the FileSequence class that allows to manipulate a file sequence.
#
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		09/11/11
#

#------------------------------------------------------------------------------------------------------------------------

import os
import re
import glob
import shutil
import blurdev
import subprocess

from framerange import FrameRange
from blur3d.constants import VideoCodec
from blur3d.constants import PaddingStyle
from blurdev.decorators import pendingdeprecation

#------------------------------------------------------------------------------------------------------------------------


class FileSequence(object):

	# This regurlar expression is supporting the following things.

	# Path/Sequence0-100.abc
	# Path/Sequence0:100.abc

	# Path/Sequence.0-100.abc
	# Path/Sequence.0:100.abc

	# Path/Sequence[0:100].abc
	# Path/Sequence[0-100].abc

	_regex = re.compile(r'^(?P<baseName>[A-Za-z0-9 _.\-\[\]]+?)((?P<separator>[^\da-zA-Z\[]?)\[?(?P<range>(?P<start>[0-9]+)[\-\:](?P<end>[0-9]+)))\]?(\.(?P<extension>[a-zA-Z0-9]+))$')

	@classmethod
	@pendingdeprecation('Use fromFileName instead.')
	def sequenceForPath(cls, fileName, step=1):
		return cls.fromFileName(fileName, step)

	@classmethod
	def fromFileName(cls, fileName, step=1):
		"""
		Given a single file in a file sequence, create a FileSequence object that represents the current sequence on disk.

		Args:
			fileName(str) : The filename to pull the image sequence from.
			step(int) : The sequence step interval.

		"""
		import blurdev.media
		sequence = blurdev.media.imageSequenceFromFileName(fileName)
		# If we're dealing with a single file, we'll need to manually format it as a sequence Path/Sequence0-0.abc
		# instead of accepting the filename without sequence formatting (as imageSequenceRepr returns.)
		if len(sequence) > 1:
			return cls(blurdev.media.imageSequenceRepr(sequence, '{pre}{firstNum}-{lastNum}{post}'), step)
		else:
			# If the provided filename is not a sequence, create an invalid file sequence
			imageSequenceInfo = blurdev.media.imageSequenceInfo(fileName)
			if imageSequenceInfo:
				return cls('{pre}{frame}-{frame}{post}'.format(
					**imageSequenceInfo.groupdict()),
					step
				)
			else:
				return cls(fileName)

	@classmethod
	def fromMovie(cls, inpt, output, padding=4, ffmpeg='ffmpeg', shell=False):
		''' Output is a path like this "C:\Output.jpg
		'''
		if os.path.exists(inpt):

			# Creating the output directory if it does not exist.
			directoryPath, fileName = os.path.split(output)
			if not os.path.exists(directoryPath):
				os.makedirs(directoryPath)

			baseName, extension = os.path.splitext(fileName)
			output = os.path.join(directoryPath, r'{}.%{}d{}'.format(baseName, padding, extension))
			command = [ffmpeg, '-i', '"{}"'.format(inpt), '-an', '-f', 'image2', '"{}"'.format(output)]

			# On some machines, if you pass a list, ffmpeg will fail. Converting to a string
			# prevents this.
			command = ' '.join(command)

			if blurdev.debug.debugLevel() >= blurdev.debug.DebugLevel.Mid:
				print 'MOVIE TO SEQUENCE COMMAND: {}'.format(command)

			# Raises subprocess.CalledProcessError if ffmpeg errors out.
			ffmpegOutput = subprocess.check_output(
				command,
				shell=shell,
				stderr=subprocess.STDOUT,
				stdin=subprocess.PIPE
			)
			
			if blurdev.debug.debugLevel() >= blurdev.debug.DebugLevel.Mid:
				print 'FFMPEG OUTPUT', '-'*50
				print ffmpegOutput

			files = glob.glob(os.path.join(directoryPath, r'{}.*{}'.format(baseName, extension)))
			return FileSequence.fromFileName(files[0])

		raise Exception('Provide and existing input.')

	def __init__(self, path='', step=1, frameRange=None):
		"""
			\remarks	Initialize the class.
		"""
		self._path = unicode(self.buildPath(path, frameRange) if frameRange else path)
		self._step = step

	@classmethod
	def isValidSequencePath(cls, path):
		return bool(cls._regex.match(os.path.basename(path)))

	@classmethod
	def buildPath(cls, uniquePath, frameRange):
		extension = os.path.splitext(uniquePath)[1]
		if extension:
			return uniquePath.replace(extension, '.%i-%i%s' % (frameRange[0], frameRange[1], extension))
		raise Exception('Path needs an extension.')

	def path(self):
		''' From "Path/Sequence.0-100.jpg" it will return "Path/Sequence.0-100.jpg".
		'''
		return os.path.abspath(self._path)

	def step(self):
		return self._step

	def name(self):
		return os.path.split(self._path)[1]

	def setName(self, baseName='', start='', end='', extension='', separator=''):
		nameTokens = self.nameTokens()
		if baseName:
			nameTokens['baseName'] = baseName
		if start:
			nameTokens['start'] = start
		if end:
			nameTokens['end'] = end
		if extension:
			nameTokens['extension'] = extension
		if separator:
			nameTokens['separator'] = separator
		self._path = os.path.join(self.basePath(), self.nameMask() % nameTokens)
		return True

	def nameMask(self):
		return '%(baseName)s%(separator)s%(start)s-%(end)s.%(extension)s'

	def nameTokens(self):
		match = self._regex.match(self.name())
		if match:
			dict = match.groupdict()
			for key in dict.keys():
				dict[key] = dict[key]
			return dict
		return {}

	def separator(self):
		return self.nameTokens().get('separator', '')

	def setSeparator(self, separator):
		self.setName(separator=separator)

	def nameToken(self, key):
		return self.nameTokens().get(key, '')

	def baseName(self):
		''' From "Path/Sequence.0-100.jpg" it will return "Sequence".
		'''
		return self.nameToken('baseName')

	def setBaseName(self, baseName):
		self.setName(baseName=baseName)

	def uniqueName(self, paddingStyle=None):
		''' From "Path/Sequence.0-100.jpg" it will return "Sequence.jpg".
		'''
		padding = paddingStyle if paddingStyle is None else unicode(self.padding(paddingStyle))
		if padding is None:
			return '{}.{}'.format(self.baseName(), self.extension())
		return '{}{}{}.{}'.format(self.baseName(), self.separator(), self.padding(paddingStyle), self.extension())

	def frameRange(self, returnsAsString=False):
		if returnsAsString:
			return self.nameToken('range')
		return FrameRange([self.start(), self.end()])

	def start(self):
		try:
			return int(self.nameToken('start'))
		except ValueError:
			return 0

	def end(self):
		try:
			return int(self.nameToken('end'))
		except ValueError:
			return 0

	def setExtension(self, extension):
		if not extension:
			return False

		# Removing the dot if provided.
		if len(extension) > 1:
			extension = extension[1:] if extension[0] == '.' else extension

		split = os.path.splitext(self._path)
		self._path = '{}.{}'.format(split[0], extension)
		return True

	def extension(self):
		''' From "Path/Sequence.0-100.jpg" it will return "jpg".
		'''
		return self.nameToken('extension')

	def count(self):
		return self.end() - self.start() + 1

	def setRange(self, rng):
		tokens = self.nameTokens()
		tokens['start'] = str(rng[0])
		tokens['end'] = str(rng[1])
		fileName = self.nameMask() % tokens
		self._path = os.path.join(self.basePath(), fileName)
		return True

	def padding(self, style=PaddingStyle.Number):
		try:
			padding = len(str(self.nameTokens()['start']))

			# This will return something like "####".
			if style == PaddingStyle.Pound:
				pounded = ''
				for i in range(padding):
					pounded += '#'
				return pounded

			# This will return something like "%4d".
			elif style == PaddingStyle.Percent:
				return '%{}d'.format(padding)

			# This will return something like "".
			elif style == PaddingStyle.Blank:
				return ''

			# This will return something like "4".
			return padding

		except KeyError:
			return 0

	def setPadding(self, padding):
		"""
			/param <int> padding
		"""
		start = str(self.start()).zfill(padding)
		end = str(self.end()).zfill(padding)
		self.setName(start=start, end=end)
		return True

	def basePath(self):
		''' From "Path/Sequence.0-100.jpg" it will return "Path".
		'''
		return os.path.split(self._path)[0]

	def setBasePath(self, basePath):
		self._path = os.path.join(basePath, os.path.split(self._path)[1])

	@pendingdeprecation('Use padding method instead using the padding style argument.')
	def paddingCode(self):
		return '%0' + str(self.padding()) + 'd'

	@pendingdeprecation('Use uniqueName instead with paddingStyle argument.')
	def codeName(self):
		''' From "Path/Sequence.0-100.jpg" it will return "Sequence.%0d.jpg".
		'''
		return self.baseName() + self.nameToken('separator') + self.paddingCode() + '.' + self.extension()

	@pendingdeprecation('Use uniquePath instead with paddingStyle argument.')
	def codePath(self):
		''' From "Path/Sequence.0-100.jpg" it will return "Path/Sequence.%0d.jpg".
		'''
		return os.path.join(self.basePath(), self.codeName())

	def framePath(self, frame):
		start = self.start()
		end = self.end()
		if start <= frame <= end:
			return self.codePath() % frame
		raise ValueError('The frame provided is outside the range of the FileSequence. {start}, {end}'.format(start=start, end=end))

	def uniquePath(self, paddingStyle=None):
		return os.path.join(self.basePath(), self.uniqueName(paddingStyle))

	def exists(self):
		paths = glob.glob(os.path.join(self.basePath(), self.baseName() + self.nameToken('separator') + '*.' + self.extension()))
		if len(paths) > 0:
			return True
		return False

	def paths(self):
		paths = []
		for frame in range(self.start(), self.end() + 1, self._step):
			name = self.baseName() + self.nameToken('separator') + str(frame).zfill(self.padding()) + '.' + self.extension()
			paths.append(os.path.normpath(os.path.join(self.basePath(), name)))
		return paths

	def isComplete(self):
		if len(self.missingFrames()) > 0:
			return False
		return True

	def missingFrames(self):
		frames = []
		for frame in range(self.start(), self.end() + 1, self._step):
			name = self.baseName() + self.nameToken('separator') + str(frame).zfill(self.padding()) + '.' + self.extension()
			path = os.path.join(self.basePath(), name)
			if not os.path.exists(path):
				frames.append(frame)
		return frames

	def offsetRange(self, offset):
		self.setRange(self.frameRange().offset(offset))
		return True

	def move(self, output):
		self.copy(output)
		self.delete()
		self._path = output.path()

	def copy(self, output):
		if output.path() == self.path() and output.frameRange().overlaps(self.frameRange()):
			raise Exception('Cannot copy to same location.')

		if self.count() != output.count():
			Exception('Cannot copy to sequence with different frame count.')

		# We need to delete everything we are going to copy.
		# Otherwise shutil might cry.
		output.delete()

		for source, copy in zip(self.paths(), output.paths()):
			shutil.copy(source, copy)

		return True

	def convert(self, output):
		if self.isComplete():
			if self.count() == output.count():
				inputExtension = self.extension()
				outputExtension = output.extension()
				from PyQt4.QtGui import QImage
				if inputExtension.lower() == 'exr' and outputExtension.lower() == 'jpg':
					for i, o in zip(self.paths(), output.paths()):
						QImage(i, 'exr_nogamma').save(o)
					return True
				else:
					raise Exception('FileSequence.convert does not supports %s to %s' % (inputExtension, outputExtension))
			else:
				raise Exception('FileSequence.convert only supports outputting to a sequence with the same amount of frames.')
		else:
			raise Exception('FileSequence.convert only supports outputting to a complete sequence.')

	def delete(self, deletesBasePath=False):
		if deletesBasePath:
			basePath = self.basePath()
			if os.path.exists(basePath):
				os.removedirs(basePath)
		for path in self.paths():
			if os.path.exists(path):
				os.remove(path)

	def generateMovie(self, outputPath=None, fps=30, ffmpeg='ffmpeg', videoCodec=VideoCodec.PhotoJPEG, audioPath=''):

		# If the output path is not provided we will put the movie in the same folder as the source.
		if not outputPath:
			outputPath = os.path.join((self.basePath()), self.baseName() + '.mov')

		# This method does not support all formats.
		if self.extension().lower() not in ['jpg','jpeg','png','tif','tiff', 'tga', 'exr']:
			raise IOError('Input sequence %s cannot be converted to a movie.' % self._path)

		if not self.isComplete():
			raise IOError('Input sequence %s is missing frames' % self._path)

		# Managing EXR sequences.
		if self.extension().lower() == 'exr':
			normalisedSequencePath = os.path.join(self.basePath(), self.baseName() + '_Temp.1-' + str(self.count()) + '.' + 'jpg')
			normalisedSequence = FileSequence(normalisedSequencePath)
			self.convert(normalisedSequence)

		# Managing all other cases.
		else:
			normalisedSequencePath = os.path.join(self.basePath(), self.baseName() + '_Temp.1-' + str(self.count()) + '.' + self.extension())
			normalisedSequence = FileSequence(normalisedSequencePath)
			self.copy(normalisedSequence)

		# Sometimes there is delay due to the servers.
		while not normalisedSequence.isComplete():
			continue

		outputBasePath = os.path.split(outputPath)[0]
		if not os.path.exists(outputBasePath):
			os.makedirs(outputBasePath)

		if videoCodec == VideoCodec.PhotoJPEG:
			command = [ffmpeg, '-r', str(fps), "-i", normalisedSequence.codePath()]
			if os.path.exists(audioPath):
				command += ['-i', audioPath, '-c:a', 'libvo_aacenc', '-b:a', '192k']
			command += ['-c:v', 'mjpeg', '-qscale', '1', '-y', outputPath]

		# TODO: GIF Implementation is a bit wonky right now.
		elif videoCodec == VideoCodec.GIF:
			command = [ffmpeg, '-r', str(fps), "-i", normalisedSequence.codePath(), '-pix_fmt', 'rgb24', '-y', outputPath.replace('.mov', '.gif')]

		# TODO: Implement H264.
		elif videoCodec == VideoCodec.H264:
			command = [ffmpeg]

		if blurdev.debug.debugLevel() >= blurdev.debug.DebugLevel.Mid:
			print 'SEQUENCE TO MOVIE COMMAND: {}'.format(' '.join(command))

		process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
		process.communicate()

		if blurdev.debug.debugLevel() < blurdev.debug.DebugLevel.Mid:
			normalisedSequence.delete()

		return True

	def link(self, output):
		if self.isComplete():
			if self.count() == output.count():
				for inp, output in zip(self.paths(), output.paths()):
					command = " ".join(["mklink", output, inp])
					subprocess.Popen(command, shell=True)
				return True
		return False
