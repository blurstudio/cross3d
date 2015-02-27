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
import subprocess

from framerange import FrameRange
from blur3d.constants import VideoCodec

#------------------------------------------------------------------------------------------------------------------------

class FileSequence( object ):
	@classmethod
	def sequenceForPath(cls, fileName, step=1):
		"""
		Given a single file in a file sequence, create a FileSequence object that represents the current sequence on disk.
		:param fileName: the filename to pull the image sequence from.
		
		.. seealso:: :func:`blurdev.media.imageSequenceFromFileName`
		.. note:: This is subject to the notes for blurdev.media.imageSequenceFromFileName
		"""
		import blurdev.media
		return cls(blurdev.media.imageSequenceReprFromFileName(fileName, '{pre}{firstNum}-{lastNum}{post}'), step)

	def __init__(self, path, step=1, frameRange=None):
		"""
			\remarks	Initialize the class.
		"""
		self._path = self.buildPath(path, frameRange) if frameRange else path
		self._step = step

	@classmethod
	def buildPath(cls, uniquePath, frameRange):
		extension = os.path.splitext(uniquePath)[1]
		if extension:
			return uniquePath.replace(extension, '.%i-%i%s' % (frameRange[0], frameRange[1], extension))
		raise Exception('Path needs an extension.')

	def path( self ):
		return os.path.abspath( self._path )
	
	def step( self ):
		return self._step
		
	def name( self ):
		return os.path.split( self._path )[1]
		
	def setName( self, baseName='', start='', end='', extension='' ):
		nameTokens = self.nameTokens()
		if baseName:
			nameTokens[ 'baseName' ] = baseName
		if start:
			nameTokens[ 'start' ] = start
		if end:
			nameTokens[ 'end' ] = end
		if extension:
			nameTokens[ 'extension' ] = extension
		self._path = os.path.join( self.basePath(), self.nameMask() % nameTokens )
		return True

	def nameMask( self ):
		return '%(baseName)s%(separator)s%(start)s-%(end)s.%(extension)s'
		
	def nameTokens( self ):
		regex = re.compile(r'^((?P<extension>[A-Za-z][A-Za-z][A-Za-z]).)((?P<range>(?P<end>[0-9]+)\-(?P<start>[0-9]+))(?P<separator>.))(?P<baseName>[A-Za-z0-9_.\-]+)$')
		match = regex.match( self.name()[::-1] )
		if match:
			dict =  match.groupdict()
			for key in dict.keys():
				dict[ key ] = dict[ key ][::-1]
			return dict
		return {}

	def nameToken( self, key ):
		return self.nameTokens().get( key, '' )

	def baseName( self ):
		return self.nameToken( 'baseName' )
		
	def uniqueName( self, rangePlaceHolder=None ):
		nameSplit = [ self.baseName(), self.extension() ]
		if rangePlaceHolder is not None:
			nameSplit.insert( 1, rangePlaceHolder )
		return '.'.join( nameSplit )

	def frameRange( self, returnsAsString=False ):
		if returnsAsString:
			return self.nameToken( 'range' )
		return FrameRange( [ self.start(), self.end() ] ) 

	def start( self ):
		try:
			return int( self.nameToken( 'start' ) )
		except ValueError:
			return 0

	def end( self ):
		try:
			return int( self.nameToken( 'end' ) )
		except ValueError:
			return 0

	def extension( self ):
		return self.nameToken( 'extension' )
		
	def count( self ):
		return self.end() - self.start() + 1
		
	def setRange( self, range ):
		tokens = self.nameTokens()
		tokens[ 'start' ] = str( range[0] )
		tokens[ 'end' ] = str( range[1] )
		fileName = self.nameMask() % tokens
		self._path = os.path.join( self.basePath(), fileName )
		return True
	
	def padding( self ):
		try:
			return len( str( self.nameTokens()[ 'start' ] ) )
		except KeyError:
			return 0
		
	def setPadding( self, padding ):
		"""
			/param <int> padding
		"""
		start = str( self.start() ).zfill( padding )
		end = str( self.end() ).zfill( padding )
		self.setName( start=start, end=end )
		return True
		
	def basePath( self ):
		return os.path.split( self._path )[0]

	def paddingCode( self ):
		return '%0' + str( self.padding() ) + 'd'

	def codeName( self ):
		return self.baseName() + self.nameToken('separator') + self.paddingCode() + '.' + self.extension()

	def codePath( self ):
		return os.path.join( self.basePath(), self.codeName() )
	
	def framePath(self, frame):
		start = self.start()
		end = self.end()
		if start <= frame <= end:
			return self.codePath() % frame
		raise ValueError('The frame provided is outside the range of the FileSequence. {start}, {end}'.format(start=start, end=end))
	
	def uniquePath( self, rangePlaceHolder=None ):
		return os.path.join( self.basePath(), self.uniqueName( rangePlaceHolder ) )
		
	def exists( self ):
		import glob
		paths = glob.glob( os.path.join( self.basePath(), self.baseName() + self.nameToken('separator') + '*.' + self.extension() ) )
		if len( paths ) > 0:
			return True
		return False

	def paths( self ):
		paths = []
		for frame in range( self.start(), self.end() + 1, self._step ):
			name = self.baseName() + self.nameToken('separator') + str( frame ).zfill( self.padding() ) + '.' + self.extension()
			paths.append( os.path.join( self.basePath(), name ) )
		return paths
		
	def isComplete( self ):
		if len( self.missingFrames() ) > 0:
			return False
		return True

	def missingFrames( self ):
		frames = []
		for frame in range( self.start(), self.end() + 1, self._step ):
			name = self.baseName() + self.nameToken('separator') + str( frame ).zfill( self.padding() ) + '.' + self.extension()
			path = os.path.join( self.basePath(), name )
			if not os.path.exists( path ):
				frames.append( frame )
		return frames

	def copy( self, output ):
		if self.isComplete():
			if self.count() == output.count():
				import shutil
				for i, o in zip( self.paths(), output.paths() ):
					shutil.copy( i, o )
				return True
			else:
				raise Exception('FileSequence.copy only supports outputting to a sequence with the same amount of frames.')
		else:
			raise Exception('FileSequence.copy only supports outputting to a complete sequence.')
	
	def convert( self, output ):
		if self.isComplete():
			if self.count() == output.count():
				inputExtension = self.extension()
				outputExtension = output.extension()
				from PyQt4.QtGui import QImage
				if inputExtension.lower() == 'exr' and outputExtension.lower() == 'jpg':
					for i, o in zip( self.paths(), output.paths()):
						QImage(i, 'exr_nogamma').save(o)
					return True
				else:
					raise Exception('FileSequence.convert does not supports %s to %s' % (inputExtension, outputExtension))
			else:
				raise Exception('FileSequence.convert only supports outputting to a sequence with the same amount of frames.')
		else:
			raise Exception('FileSequence.convert only supports outputting to a complete sequence.')

	def delete( self, deletesBasePath=False ):
		if deletesBasePath:
			basePath = self.basePath()
			if os.path.exists( basePath ):
				os.removedirs( basePath )
		for path in self.paths():
			if os.path.exists( path ):
				os.remove( path )

	def generateMovie( self, outputPath=None, fps=30, ffmpeg='ffmpeg', videoCodec=VideoCodec.PhotoJPEG):
		if not outputPath:
			outputPath = os.path.join(( self.basePath() ), self.baseName() + '.mov' )
		extension = os.path.splitext( outputPath )[1]
		if self.isComplete():
			normalisedSequencePath = os.path.join(  self.basePath(), self.baseName() + '_Temp.1-' + str( self.count() ) + '.' + self.extension() )
			normalisedSequence = FileSequence(normalisedSequencePath)
			
			# Managing EXR sequences.
			if (self.extension().lower() == 'exr'):
				normalisedSequencePath = os.path.join(  self.basePath(), self.baseName() + '_Temp.1-' + str( self.count() ) + '.' + 'jpg' )
				normalisedSequence = FileSequence(normalisedSequencePath)
				self.convert(normalisedSequence)
				
			# Managing all other cases.
			else:
				normalisedSequencePath = os.path.join(  self.basePath(), self.baseName() + '_Temp.1-' + str( self.count() ) + '.' + self.extension() )
				normalisedSequence = FileSequence(normalisedSequencePath)
				self.copy(normalisedSequence)
				
			while not normalisedSequence.isComplete():
				continue
			outputBasePath = os.path.split( outputPath )[0]
			if not os.path.exists( outputBasePath ):
				os.makedirs( outputBasePath )

			if videoCodec == VideoCodec.PhotoJPEG:
				command = [ffmpeg, '-r', str( fps ), "-i", normalisedSequence.codePath(), '-vcodec', 'mjpeg', '-qscale', '1', '-y', outputPath]

			# TODO: GIF Implementation is a bit wonky right now.
			elif videoCodec == VideoCodec.GIF:
				command = [ffmpeg, '-r', str( fps ), "-i", normalisedSequence.codePath(), '-pix_fmt', 'rgb24','-y', outputPath.replace('.mov', '.gif')]

			# TODO: Implement H264.
			elif videoCodec == VideoCodec.H264:
				command = [ffmpeg ]

			process = subprocess.Popen( command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE )
			process.communicate()
			normalisedSequence.delete()
			return True
		else:
			raise Exception( 'Input sequence %s is missing frames' % self._path )
		return False
		
	def link( self, output ):
		if self.isComplete():
			if input.count() == output.count():
				import subprocess
				for input, ouput in zip( input.paths(), output.paths() ):
					command = " ".join( [ "mklink", output, input ] )
					process = subprocess.Popen( command, shell = True )
				return True
		return False