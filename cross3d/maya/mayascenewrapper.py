import maya.OpenMaya as om
from blur3d.api.abstract.abstractscenewrapper 	import AbstractSceneWrapper

class MayaSceneWrapper( AbstractSceneWrapper ):
	#--------------------------------------------------------------------------------
	#							Making OpenMaya pythonic
	#--------------------------------------------------------------------------------
	@classmethod
	def _MObjName(cls, nativeObject, fullName=True):
		""" A Maya Helper that returns the name of a object, because OpenMaya can't 
		expose the name in a single call.
		:param nativeObject: The OpenMaya.MObject to get the name of
		:param fullName: If True return the Name(Full Path), else return the displayName. Defaults to True
		:return: nativeObject's name as a string
		"""
		dagPath = om.MDagPath.getAPathTo(nativeObject)
		if fullName:
			return dagPath.fullPathName()
		return dagPath.partialPathName()
	
	@classmethod
	def _getShapeNode(cls, nativeObject):
		""" A Maya Helper that returns the first shape node of the provided transform node.
		If no shape node exists the nativeObject is returned
		:param nativeObject: The OpenMaya.MObject to get the shape node of
		:return: OpenMaya.MObject
		"""
		path = om.MDagPath.getAPathTo(nativeObject)
		numShapes = om.MScriptUtil()
		numShapes.createFromInt(0)
		numShapesPtr = numShapes.asUintPtr()
		path.numberOfShapesDirectlyBelow(numShapesPtr)
		if om.MScriptUtil(numShapesPtr).asUint():
			# TODO: Should this return the last shape, instead of the first?
			path.extendToShapeDirectlyBelow(0)
			return path.node()
		return nativeObject
	
	@classmethod
	def _getTransformNode(cls, nativeObject):
		""" A Maya Helper that returns the first transform node of the provided shape node.
		The nativeObject is returned if the nativeObject is a transform node.
		:param nativeObject: The OpenMaya.MObject to get the transform node of
		:return: OpenMaya.MObject
		"""
		path = om.MDagPath.getAPathTo(nativeObject)
		newPointer = path.transform()
		if newPointer != nativeObject:
			return newPointer
		return nativeObject
	
	#--------------------------------------------------------------------------------
	#							blur3d public methods
	#--------------------------------------------------------------------------------
	def displayName(self):
		""" Returns the display name for object. This does not include parent structure """
		return self._MObjName(self._nativePointer, False)

	def name(self):
		""" Return the full name of this object, including parent structure """
		return self._MObjName(self._nativePointer, True)
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneWrapper', MayaSceneWrapper )