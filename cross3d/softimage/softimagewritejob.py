##
#   :namespace  blur3d.api.softimage.softimagewritejob
#
#   :remarks    [desc::commented]
#   
#   :author     enoch@blur.com
#   :author     Blur Studio
#   :date       07/10/12
#

from blur3d.api.abstract.abstractwritejob import AbstractWriteJob

class SoftimageWriteJob( AbstractWriteJob ):
	def __init__( self ):
		AbstractWriteJob.__init__( self )
		
	def objectsAsString( self ):
		return ','.join( [ unicode( object.name() ) for object in self._objects ] )

# convert to string
	def arguments( self ):
		jobItems = [ 'filename=%s' % self._fileName, 
					 'objects=%s' % self.objectsAsString(),
					 'in=%i' % self._inFrame,
					 'out=%i' % self._outFrame,
					 'step=%i' % self._step,
					 'substep=%i' % self._substep,
					 'normals=%s' % unicode( self._normals ).lower(),
					 'uvs=%s' % unicode( self._uvs ).lower(),
					 'facesets=%s' % unicode( self._faceSets ).lower(),
					 'bindpose=%s' % unicode( self._bindPose ).lower(),
					 'purepointcache=%s' % unicode( self._purePointCache ).lower(),
					 'dynamictopology=%s' % unicode( self._dynamicTopology ).lower(),
					 'globalspace=%s' % unicode( self._globalSpace ).lower() ]
					 
		return ';'.join( jobItems )
		
class SoftimagePointCacheWriteJob( SoftimageWriteJob ):
	def __init__( self ):
		SoftimageWriteJob.__init__( self )
		self._normals = False
		self._uvs = False
		self._faceSets = False
		self._bindPose = False
		self._purePointCache = True
		self._dynamicTopology = False
		self._globalSpace = True

#register the symbol
from blur3d import api
api.registerSymbol( 'WriteJob', SoftimageWriteJob )
api.registerSymbol( 'PointCacheWriteJob', SoftimagePointCacheWriteJob )