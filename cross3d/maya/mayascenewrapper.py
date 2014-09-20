import re
import maya.OpenMaya as om
from blur3d.api.abstract.abstractscenewrapper 	import AbstractSceneWrapper

class MayaSceneWrapper( AbstractSceneWrapper ):
	#--------------------------------------------------------------------------------
	#							Making OpenMaya pythonic
	#--------------------------------------------------------------------------------
	@classmethod
	def _asMOBject(cls, obj):
		''' When passed a object name it will convert it to a MObject. If passed a MObject, it will return the MObject
		:param obj: A MObject or object name to return as a MObject
		'''
		if isinstance(obj, basestring):
			sel = om.MSelectionList()
			sel.add(obj)
			obj = om.MObject()
			sel.getDependNode(0, obj)
		return obj
	
	@classmethod
	def _createAttribute(cls, mObj, name, dataType=None, shortName=None, default=None):
		name = cls._normalizeAttributeName(name)
		if dataType == None and default != None:
			if isinstance(default, basestring):
				dataType = om.MFnData.kString
			# TODO: add support for other types
		if dataType == None:
			# MCH 09/17/14 # TODO Evaluate if this is a valid default?
			dataType = om.MFnData.kAny
		if shortName == None:
			shortName = cls._normalizeAttributeShortName(name)
		depNode = om.MFnDependencyNode(mObj)
		sAttr = om.MFnTypedAttribute()
		if False: #if default:
			# TODO: Handle creating the default object
			attr = sAttr.create(name, shortName, dataType, default)
		else:
			attr = sAttr.create(name, shortName, dataType)
		depNode.addAttribute(attr)
	
	@classmethod
	def _getAttribute(cls, mObj, name):
		plug = cls._getPlug(mObj, name)
		# OpenMaya doesn't provide a QObject.toPyObject like function, but pymel does.
		import pymel.core
		return pymel.core.datatypes.getPlugValue(plug)
	
	@classmethod
	def _getPlug(cls, mObj, name):
		""" For a given OpenMaya.MObject return the OpenMaya.MPlug object with that attribute name.
		If the property does not exist, raises "RuntimeError: (kInvalidParameter): Cannot find item of required type"
		:param mObj: The source MObject
		:param name: The name of the attribute to get from mObj.
		:return: A OpenMaya.MPlug object
		"""
		depNode = om.MFnDependencyNode(mObj)
		attr = depNode.attribute(name)
		return om.MPlug(mObj, attr)
	
	@classmethod
	def _hasAttribute(cls, mObj, name):
		depNode = om.MFnDependencyNode(mObj)
		return depNode.hasAttribute(name)
	
	@classmethod
	def _normalizeAttributeName(cls, name):
		""" Removes invalid characters for attribute names from the provided string.
		:param name: The string used as the name of a attribute.
		:return: string
		"""
		return re.sub(r'\W', '', name)
	
	@classmethod
	def _normalizeAttributeShortName(cls, name):
		""" Creates a shortName for the provided attribute name by calling MayaSceneWrapper._normalizeAttributeName.
		It then adds the first character to any capital letters in the rest of the name. The name is then lowercased.
		:param name: The string used to generate the short name.
		:return: string
		"""
		name = cls._normalizeAttributeName(name)
		if len(name):
			name = name[0] + re.sub(r'[a-z]', '', name[1:])
		return name.lower()
	
	@classmethod
	def _setAttribute(cls, mObj, name, value):
		plug = cls._getPlug(mObj, name)
		if isinstance(value, basestring):
			plug.setString(value)
		elif isinstance(value, bool):
			plug.setBool(value)
#		elif isinstance(value, double):
#			plug.setDouble(value)
		elif isinstance(value, float):
			plug.setFloat(value)
		elif isinstance(value, int):
			plug.setInt(value)
#		elif isinstance(value, MAngle):
#			plug.setMAngle(value)
#		elif isinstance(value, MDataHandle):
#			plug.setMDataHandle(value)
#		elif isinstance(value, MDistance):
#			plug.setMDistance(value)
#		elif isinstance(value, MObject):
#			plug.setMObject(value)
#		elif isinstance(value, MPxData):
#			plug.setMPxData(value)
#		elif isinstance(value, MTime):
#			plug.setMTime(value)
#		elif isinstance(value, int):
#			plug.setNumElements(value)
#		elif isinstance(value, ShortInt):
#			plug.setShort(value)
		
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