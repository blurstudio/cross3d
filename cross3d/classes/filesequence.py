##
#	\namespace	cross3d.classes.filesequence
#
#	\remarks	This file defines the FileSequence class that allows to manipulate a file sequence.
#
#	\author		douglas
#	\author		Blur Studio
#	\date		09/11/11
#

#------------------------------------------------------------------------------------------------------------------------

import os
import re
import copy
import glob
import shutil
import subprocess
import time
import warnings

import cross3d
from framerange import FrameRange
from cross3d.constants import VideoCodec, PaddingStyle

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
	def fromFileName(cls, fileName, step=1):
		"""
		Given a single file in a file sequence, create a FileSequence object that represents the current sequence on disk.

		Args:
			fileName(str) : The filename to pull the image sequence from.
			step(int) : The sequence step interval.

		"""
		from cross3d.migrate import imagesequence
		sequence = imagesequence.imageSequenceFromFileName(fileName)
		# If we're dealing with a single file, we'll need to manually format it as a sequence Path/Sequence0-0.abc
		# instead of accepting the filename without sequence formatting (as imageSequenceRepr returns.)
		if len(sequence) > 1:
			return cls(imagesequence.imageSequenceRepr(sequence, '{pre}{firstNum}-{lastNum}{post}'), step)
		else:
			# If the provided filename is not a sequence, create an invalid file sequence
			imageSequenceInfo = imagesequence.imageSequenceInfo(fileName)
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

			if cross3d.debugLevel >= cross3d.constants.DebugLevels.Mid:
				print 'MOVIE TO SEQUENCE COMMAND: {}'.format(command)

			# Raises subprocess.CalledProcessError if ffmpeg errors out.
			try:
				ffmpegOutput = subprocess.check_output(
					command,
					shell=shell,
					stderr=subprocess.STDOUT,
					stdin=subprocess.PIPE
				)
			except subprocess.CalledProcessError as e:
				# Provide a debuggable exception instead of just returned non-zero exit status exception message
				program = os.path.splitext(os.path.basename(ffmpeg))[0]
				raise RuntimeError(
					"{} failed.\nCommand '{}' return with error (code {}): {}".format(
						program, e.cmd, e.returncode, e.output
					)
				)
			
			if cross3d.debugLevel >= cross3d.constants.DebugLevels.Mid:
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

			# This will return something like "*".
			elif style == PaddingStyle.Wildcard:
				return '*'

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

	def framePath(self, frame):
		start = self.start()
		end = self.end()
		if start <= frame <= end:
			return self.uniquePath(PaddingStyle.Percent) % frame
		raise ValueError('The frame provided is outside the range of the FileSequence. {start}, {end}'.format(start=start, end=end))

	def uniquePath(self, paddingStyle=None):
		return os.path.join(self.basePath(), self.uniqueName(paddingStyle))

	def exists(self):
		paths = glob.glob(os.path.join(self.basePath(), self.baseName() + self.nameToken('separator') + '*.' + self.extension()))
		if len(paths) > 0:
			return True
		return False

	def existingPaths(self):
		existingPaths = []
		for path in self.paths():
			if os.path.exists(path):
				existingPaths.append(path)
		return existingPaths
		
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
		self.setRange(self.frameRange().offseted(offset))
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

		for source, cpy in zip(self.paths(), output.paths()):
			shutil.copy(source, cpy)

		return True

	def convert(self, output):
		if self.isComplete():
			if self.count() == output.count():
				inputExtension = self.extension()
				outputExtension = output.extension()
				from Qt.QtGui import QImage
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

		# Sometimes there is delay due to the servers. Wait for a reasonable ammount of time
		# before raising a exception.
		for i in xrange(15):
			if normalisedSequence.isComplete():
				break
			time.sleep(0.1)
		else:
			raise IOError('Normalized Sequence is missing frames! "{}"'.format(normalisedSequence.path()))

		outputBasePath = os.path.split(outputPath)[0]
		if not os.path.exists(outputBasePath):
			os.makedirs(outputBasePath)

		if videoCodec == VideoCodec.PhotoJPEG:
			command = [ffmpeg, '-r', str(fps), "-i", '"{}"'.format(normalisedSequence.uniquePath(PaddingStyle.Percent))]
			if os.path.exists(audioPath):
				# Updating the way the audio file is being added to the new quicktime. Instead of encoding the audio file with a specifc encoder
				# we are now copying it exactly like , so there isn't any change to the audio.
				command += ['-i', '"{}"'.format(audioPath), '-c:a','copy']
			# Resize the input if it is larger than 2k in either dimension. ffmpeg does not support 
			# larger resolutions. In my testing you can go up to 4000 for maxSize
			command += ["-vf", "scale=w='if(eq(min(iw,ih),iw),-1,min(iw,{maxSize}))':h='if(eq(min(iw,ih),ih),-1,min(ih,{maxSize}))'".format(maxSize=2048)]
			# Added the '-vframes' flag to limit how long the quicktime should be. -vframes takes in an argument which is the total number of frrames
			# the video file will be. I am setting this value to the filesequence's count.
			command += ['-c:v', 'mjpeg', '-qscale', '1', '-y', '-vframes' , str(self.count()), '"{}"'.format(outputPath)]

		# TODO: GIF Implementation is a bit wonky right now.
		elif videoCodec == VideoCodec.GIF:
			command = [ffmpeg, '-r', str(fps), "-i", '"{}"'.format(normalisedSequence.uniquePath(PaddingStyle.Percent)), '-pix_fmt', 'rgb24', '-y', '"{}"'.format(outputPath.replace('.mov', '.gif'))]

		# TODO: Implement H264.
		elif videoCodec == VideoCodec.H264:
			command = [ffmpeg]

		if cross3d.debugLevel >= cross3d.constants.DebugLevels.Mid:
			print 'SEQUENCE TO MOVIE COMMAND: {}'.format(' '.join(command))

		success = True
		try:
			output = subprocess.check_output(
				' '.join(command),
				shell=True,
				stderr=subprocess.STDOUT,
				stdin=subprocess.PIPE
			)
			if cross3d.debugLevel >= cross3d.constants.DebugLevels.Mid:
				# Show the output from ffmpeg
				print output
		except subprocess.CalledProcessError as e:
			success = False
			program = os.path.splitext(os.path.basename(ffmpeg))[0]
			warnings.warn(
				"{} failed.\nCommand '{}' return with error (code {}): {}".format(
					program, e.cmd, e.returncode, e.output
				)
			)

		if cross3d.debugLevel < cross3d.constants.DebugLevels.Mid:
			normalisedSequence.delete()

		return success

	def retime(self, outputPath, retimeCurve):
		"""Retimes the filesequence using the specified retimeCurve.  Outputs the retimed sequence
			to the specified location.
		
		Args:
			outputPath (str): The unique path to output the retimed FileSequence to.
			retimeCurve (cross3d.FCurve): The curve to evaluate to retime the file sequence
			by mapping frames to frames.
		
		Returns:
		    FileSequence: The newly created FileSequence.
		"""	
		# We cannot initialize a FileSequence with a unique path.
		retimedSequence = FileSequence('{}.0-0{}'.format(*os.path.splitext(outputPath)))

		# We'll prescan the input range to find the bounds of our target output
		start = None
		end = None

		invertedCurve = copy.deepcopy(retimeCurve)
		invertedCurve.invert()

		for frame in xrange(self.start(), self.end() + 1, self.step()):
			targetFrame = int(round(invertedCurve.valueAtTime(frame)))
			start = targetFrame if start is None else min(targetFrame, start)
			end = targetFrame if end is None else max(targetFrame, end)

		# We'll invert the curve so we can lookup in the opposite direction, and
		# find the source frames for our target range.
		for frame in xrange(start, end + 1):
			sourceFrame = int(round(retimeCurve.valueAtTime(frame)))
			sourceName = self.uniquePath(PaddingStyle.Percent) % min(self.end(), max(self.start(), sourceFrame)) 
			name = retimedSequence.uniquePath(PaddingStyle.Percent) % frame
			shutil.copy2(sourceName, name)

		# Update start/end of returned Sequence
		retimedSequence.setRange((start, end))
		return retimedSequence

	def link(self, output):
		if self.isComplete():
			if self.count() == output.count():
				for inp, output in zip(self.paths(), output.paths()):
					command = " ".join(["mklink", output, inp])
					subprocess.Popen(command, shell=True)
				return True
		return False
