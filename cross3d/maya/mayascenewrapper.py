import re
import maya.OpenMaya as om
import maya.cmds as cmds
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
	def _getAttributeDataType(cls, data):
		""" Returns the OpenMaya.MFnData id for the given object. Returns OpenMaya.MFnData.kInvalid
		if the object type could not be identified.
		:param data: the object to get the data type of
		:return: int value for the dataType
		"""
		dataType = om.MFnData.kInvalid
		if isinstance(data, basestring):
			dataType = om.MFnData.kString
		elif isinstance(value, float):
			dataType = om.MFnData.kFloatArray
		elif isinstance(value, int):
			dataType = om.MFnData.kIntArray
		# TODO: add support for other types
		return dataType
	
	@classmethod
	def _createAttribute(cls, mObj, name, dataType=None, shortName=None, default=None):
		""" Create a attribute on the provided object. Returns the attribute name and shortName. You 
		should provide dataType or default when calling this method so a valid dataType is selected. 
		MayaSceneWrapper._normalizeAttributeName is called on name to ensure it is storing the 
		attribute with a valid attribute name. If shortName is not provided, the name will have 
		MayaSceneWrapper._normalizeAttributeShortName called on it.
		:param mObj: The OpenMaya.MObject to create the attribute on
		:param name: The name used to access the attribute
		:param dataType: The type of data to store in the attribute. Defaults to None.
		:param shortName: The shortName used by scripting. Defaults to None.
		:param default: The default value assigned to the attribute. Defaults to None.
		:return: (name, short name) Because the attribute name and shortName are normalized, this
					returns the actual names used for attribute names.
		"""
		name = cls._normalizeAttributeName(name)
		if dataType == None and default != None:
			dataType == cls._getAttributeDataType(default)
			if dataType == om.MFnData.kInvalid:
				# No vaid dataType was found, default to None so we can handle it diffrently
				dataType == None
				from blurdev import debug
				debug.debugMsg('Unable To determine the attribute type.\n{}'.format(str(default)))
		if dataType == None:
			# MCH 09/17/14 # TODO Evaluate if this is a valid default?
			dataType = om.MFnData.kAny
		if shortName == None:
			shortName = cls._normalizeAttributeShortName(name, uniqueOnObj=mObj)
		depNode = om.MFnDependencyNode(mObj)
		sAttr = om.MFnTypedAttribute()
		if False: #if default:
			# TODO: Handle creating the default object
			attr = sAttr.create(name, shortName, dataType, default)
		else:
			attr = sAttr.create(name, shortName, dataType)
		depNode.addAttribute(attr)
		return name, shortName
	
	@classmethod
	def _getAttribute(cls, mObj, name):
		""" For the given OpenMaya.MObject and attribute name return the pythonic value stored on 
		the attribute.
		:param mObj: The OpenMaya.MObject
		:param name: The attribute name to return the value of
		:return: Python value stored on the attribute
		"""
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
	def _normalizeAttributeShortName(cls, name, uniqueOnObj=None):
		""" Creates a shortName for the provided attribute name by calling MayaSceneWrapper._normalizeAttributeName.
		It then adds the first character to any capital letters in the rest of the name. The name is then lowercased.
		If uniqueOnObj is provided with a object, it will ensure the returned attribute name is 
		unique by attaching a 3 digit padded number to it. It will be the lowest available number.
		:param name: The string used to generate the short name.
		:param uniqueOnObj: Ensure the name is unque. Defaults to None.
		:return: string
		"""
		name = cls._normalizeAttributeName(name)
		if len(name):
			name = name[0] + re.sub(r'[a-z]', '', name[1:])
		name = name.lower()
		if uniqueOnObj:
			# Ensure a uniqe object name by adding a value to the number
			names = set(cmds.listAttr(cls._mObjName(uniqueOnObj), shortNames=True))
			name = api.Scene._findUniqueName(name, names, incFormat='{name}{count}')
		return name
	
	@classmethod
	def _setAttribute(cls, mObj, name, value):
		""" Stores a pythonic value as a attribute on the provided object. This does not call
		MayaSceneWrapper._normalizeAttributeName, so make sure you have a valid attribute name.
		This does not create the attribute, so make sure it is created first.
		Note: Only string, float and int dataType's are currently supported.
		:param mObj: A OpenMaya.MObject to set the attribute value to
		:param name: The name of the attribute to store the value in
		:param value: The value to store in the attribute
		"""
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
		if nativeObject.apiType() == om.MFn.kTransform:
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
		if nativeObject.apiType() == om.MFn.kWorld:
			# The world node doesn't play well with the getting transform code
			return nativeObject
		path = om.MDagPath.getAPathTo(nativeObject)
		newPointer = path.transform()
		if newPointer != nativeObject:
			return newPointer
		return nativeObject
	
	@classmethod
	def _mObjName(cls, nativeObject, fullName=True):
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
	#							blur3d private methods
	#--------------------------------------------------------------------------------
	def _nativeProperty(self, key, default=None):
		"""
			\remarks	return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty, AbstractScene._fromNativeValue
			\param		key			<str>
			\param		default		<variant>	(auto-converted from the application's native value)
			\return		<variant>
		"""
		ret = cmds.getAttr("{name}.{key}".format(name=self.name(), key=key))
		return ret
		return default

	def _setNativeProperty(self, key, nativeValue):
		"""
			\remarks	set the value of the property defined by the inputed key
			\sa			hasProperty, property, setProperty, AbstractScene._toNativeValue
			\param		key		<str>
			\param		value	<variant>	(pre-converted to the application's native value)
			\retrun		<bool> success
		"""
		cmds.setAttr("{name}.{key}".format(name=self.name(), key=key), nativeValue)
	
	#--------------------------------------------------------------------------------
	#							blur3d public methods
	#--------------------------------------------------------------------------------
	def displayName(self):
		""" Returns the display name for object. This does not include parent structure """
		return self._mObjName(self._nativePointer, False)

	def name(self):
		""" Return the full name of this object, including parent structure """
		return self._mObjName(self._nativePointer, True)
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneWrapper', MayaSceneWrapper )