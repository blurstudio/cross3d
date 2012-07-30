##
#   :namespace  blur3d.api.abstract.abstractwritejob
#
#   :remarks    [desc::commented]
#   
#   :author     enoch@blur.com
#   :author     Blur Studio
#   :date       07/10/12
#


class AbstractWriteJob( object ):
	
	def __init__( self ):
		super( AbstractWriteJob, self ).__init__()
		
		self._fileName = ''
		self._objects = []
		self._inFrame = 0
		self._outFrame= 0
		self._step = 0
		self._substep = 0
		self._normals = False
		self._uvs = False
		self._faceSets = False
		self._bindPose = False
		self._purePointCache = False
		self._dynamicTopology = False
		self._globalSpace = False

# getters
	def fileName( self ):
		return self._fileName

	def objects( self ):
		return self._objects
		
	def inFrame( self ):
		return self._inFrame
		
	def outFrame( self ):
		return self._outFrame
		
	def step( self ):
		return self._step
		
	def subStep( self ):
		return self._subStep
		
	def normals( self ):
		return self._normals
		
	def uvs( self ):
		return self._uvs
		
	def faceSets( self ):
		return self._faceSets
		
	def bindPose( self ):
		return self._bindPose
		
	def globalSpace( self ):
		return self._globalSpace
		
	def purePointCache( self ):
		return self._purePointCache
		
	def dynamicTopology( self ):
		return self._dynamicTopology
		
	def objectsAsString( self, objects ):
		return ','.join( [ unicode( object.name() ) for object in objects ] )

# setters
	def setFileName( self, fileName ):
		import os
		self._fileName = os.path.abspath( fileName )
		
	def setObjects( self, objects ):
		self._objects = objects

	def setInFrame( self, inFrame ):
		self._inFrame = inFrame
		
	def setOutFrame( self, outFrame ):
		self._outFrame= outFrame
		
	def setStep( self, step ):
		self._step = step
		
	def setSubStep( self, subStep ):
		self._substep = subStep
		
	def setNormals( self, normals ):
		self._normals = normals
		
	def setUvs( self, uvs ):
		self._uvs = uvs
		
	def setFaceSets( self, faceSets ):
		self._faceSets = faceSets
		
	def setBindPose( self, bindPose ):
		self._bindPose = bindPose
		
	def setPurePointCache( self, purePointCache ):
		self._purePointCache = purePointCache
		
	def setDynamicTopology( self, dynamicTopology ):
		self._dynamicTopoology = dynamicTopology 
		
	def setGlobalSpace( self, globalSpace ):
		self._globalSpace = globalSpace
			
# convert to string
	def arguments( self ):
		return

class AbstractPointCacheWriteJob( AbstractWriteJob ):
	def __init__( self ):
		AbstractWriteJob.__init__( self )
		self._normals = False
		self._uvs = False
		self._faceSets = False
		self._bindPose = False
		self._purePointCache = True
		self._dynamicTopology = False
		self._globalSpace = True


# register the symbol
from blur3d import api
api.registerSymbol( 'WriteJob', AbstractWriteJob, ifNotFound = True )
api.registerSymbol( 'PointCacheWriteJob', AbstractPointCacheWriteJob, ifNotFound = True )