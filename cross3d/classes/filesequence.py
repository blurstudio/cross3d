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

from framerange import FrameRange

#------------------------------------------------------------------------------------------------------------------------

class FileSequence( object ):

	def __init__( self, path, step=1 ):
		"""
			\remarks	Initialize the class.
		"""
		self._path = path
		self._step = step

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
		return '%(baseName)s.%(start)s-%(end)s.%(extension)s'
		
	def nameTokens( self ):
		import re
		regex = re.compile(r'^((?P<extension>[A-Za-z][A-Za-z][A-Za-z]).)((?P<range>(?P<end>[0-9]+)\-(?P<start>[0-9]+)).)(?P<baseName>[A-Za-z0-9_.]+)$')
		match = regex.match( self.name()[::-1] )
		if match:
			dict =  match.groupdict()
			for key in dict.keys():
				dict[ key ] = dict[ key ][::-1]
			return dict
		return None

	def nameToken( self, key ):
		if self.nameTokens().has_key( key ):
			return self.nameTokens()[ key ]
		else:
			return None

	def baseName( self ):
		return self.nameToken( 'baseName' )
		
	def uniqueName( self, rangePlaceHolder='' ):
		nameSplit = [ self.baseName(), self.extension() ]
		if rangePlaceHolder:
			nameSplit.insert( 1, rangePlaceHolder )
		return '.'.join( nameSplit )

	def frameRange( self, returnsAsString=False ):
		if returnsAsString:
			return self.nameToken( 'range' )
		return FrameRange( [ self.start(), self.end() ] ) 
	 
	def start( self ):
		return int( self.nameToken( 'start' ) )

	def end( self ):
		return int( self.nameToken( 'end' ) )

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
		return len( str( self.nameTokens()[ 'start' ] ) )
		
	def setPadding( self, padding ):
		start = str( self.start() ).zfill( padding )
		end = str( self.end() ).zfill( padding )
		self.setName( start=start, end=end )
		return True
		
	def basePath( self ):
		return os.path.split( self._path )[0]

	def paddingCode( self ):
		return '%' + str( self.padding() ) + 'd'

	def codeName( self ):
		return self.baseName() + '.' + self.paddingCode() + '.' + self.extension()

	def codePath( self ):
		return os.path.join( self.basePath(), self.codeName() )
		
	def uniquePath( self, rangePlaceHolder='' ):
		return os.path.join( self.basePath(), self.uniqueName( rangePlaceHolder ) )
		
	def exists( self ):
		import glob
		paths = glob.glob( os.path.join( self.basePath(), self.baseName() + '.*.' + self.extension() ) )
		if len( paths ) > 0:
			return True
		return False

	def paths( self ):
		paths = []
		for frame in range( self.start(), self.end() + 1, self._step ):
			name = self.baseName() + '.' + str( frame ).zfill( self.padding() ) + '.' + self.extension()
			paths.append( os.path.join( self.basePath(), name ) )
		return paths
		
	def isComplete( self ):
		if len( self.missingFrames() ) > 0:
			return False
		return True

	def missingFrames( self ):
		frames = []
		for frame in range( self.start(), self.end() + 1, self._step ):
			name = self.baseName() + '.' + str( frame ).zfill( self.padding() ) + '.' + self.extension()
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
			return False

	def delete( self, deletesBasePath=False ):
		if deletesBasePath:
			basePath = self.basePath()
			if os.path.exists( basePath ):
				os.removedirs( basePath )
		for path in self.paths():
			if os.path.exists( path ):
				os.remove( path )

	def generateMovie( self, outputPath=None, fps=30, ffmpeg='ffmpeg' ):
		print outputPath
		if not outputPath:
			outputPath = os.path.join(( self.basePath() ), self.baseName() + '.mov' )
		extension = os.path.splitext( outputPath )[1]
		if self.isComplete():
			normalisedSequencePath = os.path.join(  self.basePath(), self.baseName() + '_Temp.1-' + str( self.count() ) + '.' + self.extension() )
			normalisedSequence = FileSequence( normalisedSequencePath )
			self.copy( normalisedSequence )
			while not normalisedSequence.isComplete():
				continue
			import subprocess
			command = [ ffmpeg, '-r', str( fps ), "-i", normalisedSequence.codePath(), '-vcodec', 'mjpeg', '-qscale', '1', '-y', outputPath ]
			process = subprocess.Popen( command )
			process.communicate()
			normalisedSequence.delete()
			return True
		else:
			raise( 'Input sequence ' + str( self._path ) + ' is missing frames' )
		return True
		
	def link( self, output ):
		if self.isComplete():
			if input.count() == output.count():
				import subprocess
				for input, ouput in zip( input.paths(), output.paths() ):
					command = " ".join( [ "mklink", output, input ] )
					process = subprocess.Popen( command, shell = True )
				return True
		return False