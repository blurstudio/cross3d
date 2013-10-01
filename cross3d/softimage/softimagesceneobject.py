##
#	\namespace	blur3d.api.softimage.softimagesceneobject
#
#	\remarks	The SoftimageSceneObject class provides the implementation of the AbstractSceneObject class as it applies
#				to Softimage
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/04/11 
#

from PySoftimage import xsi
from blur3d.constants import ObjectType
from blur3d.api.abstract.abstractsceneobject import AbstractSceneObject

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneObject( AbstractSceneObject ):

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def _findNativeChild( self, name, recursive = False, parent = None ):
		"""
			\remarks	implements the AbstractSceneObject._findNativeChildren method to look up a specific native children for this object
			\return		<PySotimage.xsi.Object> nativeObject
		"""
		return self.nativePointer().FindChild( name, '', '', recursive )

	def _nativeChildren( self, recursive = False, wildcard = '', type = '', parent = '', childrenCollector = [] ):
		"""
			\remarks	implements the AbstractSceneObject._nativeChildren method to look up the native children for this object
			\param		recursive <bool> wildcard <string> type <string parent <string> childrenCollector <list>
			\sa			children
			\return		<list> [ <PySoftimage.xsi.Object> nativeObject, .. ]
		"""
		nativeType = ''
		if type != '':
			nativeType = self._nativeTypeOfObjectType( type )
		#return [ obj for obj in self._nativePointer.FindChildren( name, nativeType, parent, recursive ) ]
		return self._nativePointer.FindChildren( wildcard, nativeType, '', recursive )
	
	def _nativeParent( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeParent method to look up the native parent for this object
			\sa			parent, setParent, _setNativeParent
			\return		<PySoftimage.xsi.Object> nativeObject || None
		"""
		return self._nativePointer.Parent
	
	def _setNativeParent( self, nativeParent ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeParent method to set the native parent for this object
			\sa			parent, setParent, _nativeParent
			\param		<PySoftimage.xsi.Object> nativeObject || None
			\return		<bool> success
		"""
		xsi.Application.ParentObj(nativeParent, self._nativePointer)
		return True
		
	def _nativeModel( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeModel method to look up the native model for this object
			\sa			children
			\return		<list> [ <PySotimage.xsi.Model> nativeObject, .. ]
		"""
		obj = self.nativePointer()
		ignoreSceneRoot = True
		if str( obj.Type ) == "#model":
			if ignoreSceneRoot is True and obj.Name == "Scene_Root": 
				model = None
			else:
				model = obj
		else:
			if ignoreSceneRoot is True and obj.Model.Name == "Scene_Root":
				model = None
			else:
				model = obj.Model
		return model
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def getCacheName(self, type):
		typeDic = {	"Pc":".pc2",
					"Tmc":".tmc",
					"Abc":".abc",
					"Icecache":".icecache"}
					
					
		obj = self._nativePointer
		name = obj.Fullname
		cacheName = name.replace("." , "" )
		cacheName = cacheName +  typeDic[type]
		
		
		return cacheName
		
		
	def deleteProperty( self, propertyName ):
		"""
			\remarks	implements the AbstractSceneObject.deleteProperty that deletes a property of this object.
			\return		<bool> success
		"""
		xsi.DeleteObj( '.'.join( [ self.name(), propertyName ] ) )
		return True
	
	def uniqueId( self ):
		"""
			\remarks	implements the AbstractSceneObject.uniqueId to look up the unique name for this object and returns it
			\sa			displayName, setDisplayName, setName
			\return		<str> name
		"""
		return self._nativePointer.ObjectID
	
	def applyCache(self, path, type):
		"""Applies cache to object
		param <string>path , <string>types "Pc","Tmc","Icecache", "Abc", Type 
		return cache object
		"""
		obj = self._nativePointer
		if type == "Pc":
			
			cache = obj.ActivePrimitive.ConstructionHistory.Find( "BlurPCOperator" )
			if not cache:
				#print(self._nativePointer)
				xsi.BlurPCAddDeformer(self._nativePointer)
				cache = obj.ActivePrimitive.ConstructionHistory.Find( "BlurPCOperator" )
				cache.Parameters("Filename").Value = path
				#xsi.setValue((cache.Fullname +".Filename"), path)
				return cache
			else:
				cache.Parameters("Filename").Value = path
				return cache
		
		elif type == "Tmc":
			kine = obj.Kinematics.Global
			tmcop = kine.NestedObjects("TmcOp")

			
			if not tmcop:
				cache = xsi.ApplyTmcOp(self._nativePointer)
				tmcop = kine.NestedObjects("TmcOp")
			
			tmcop.Parameters("Filename").Value = path
						
			return tmcop
		
		elif type =="Icecache":
			cache = xsi.AddFileCacheSource(obj, path)
			return cache
			
			
		elif type == "abc":
			print("unsupported")
			return None
		
		else:
			print("unsupported cache Type")
			return None
			
	def resetTransforms(self, pos=True, rot=True, scl=True):
		"""
			Resets the transforms to zero.
		"""
		if pos and rot and scl:
			xsi.ResetTransform(self._nativePointer, "siObj", "siSRT", "siXYZ")
		else:
			if pos:
				xsi.ResetTransform(self._nativePointer, "siObj", "siTrn", "siXYZ")
			if rot:
				xsi.ResetTransform(self._nativePointer, "siObj", "siRot", "siXYZ")
			if pos:
				xsi.ResetTransform(self._nativePointer, "siObj", "siScl", "siXYZ")
		return True
		
	def rotation(self, local=False):
		"""
		Returns the rotation of the current object.
		:param local: If True return the local rotation. Default False.
		"""
		if local:
			trans = self._nativePointer.Kinematics.Local
		else:
			trans = self._nativePointer.Kinematics.Global
		return trans.rotx.Value, trans.roty.Value, trans.rotz.Value
	
	def setHidden(self, state):
		"""Hides/unhides this object
		"""
		self._nativePointer.Properties('Visibility').Parameters('viewvis').SetValue(not state)
		self._nativePointer.Properties('Visibility').Parameters('rendvis').SetValue(not state)
		return True

	def key(self, target='keyable'):
		"""
			Set keys on the object parameters.
		"""
		xsi.SaveKeyOnKeyable(self._nativePointer)
		
	def translation(self, local=False):
		"""
		Returns the translation of the current object.
		:param local: If True return the local translation. Default False.
		"""
		if local:
			trans = self._nativePointer.Kinematics.Local
		else:
			trans = self._nativePointer.Kinematics.Global
		return trans.posx.Value, trans.posy.Value, trans.posz.Value
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												static methods
	#------------------------------------------------------------------------------------------------------------------------
	
	@staticmethod
	def _nativeTypeOfObjectType( objectType ):
		"""
			\remarks	reimplements the AbstractSceneObject._nativeTypeOfObjectType method to return the nativeType of the ObjectType supplied
			\param		<blur3d.api.constants.ObjectType> objectType || None
			\return		<bool> success
		"""	
		if objectType == ObjectType.Geometry:
			return 'polymsh'
		elif objectType == ObjectType.Light:
			return 'light'
		elif objectType == ObjectType.Camera:
			return 'camera'
		elif objectType == ObjectType.Model:
			return '#model'
		elif objectType == ObjectType.Group:
			return '#group'
		elif objectType == ObjectType.NurbsSurface:
			return 'surfmsh'
		elif objectType == ObjectType.Curve:
			return 'crvlist'
		else:
			return None
		return AbstractSceneObject._nativeTypeOfObjectType( objectType )
	
	@staticmethod
	def _typeOfNativeObject( nativeObject ):
		"""
			\remarks	reimplements the AbstractSceneObject._typeOfNativeObject method to returns the ObjectType of the nativeObject applied
			\param		<PySoftimage.xsi.Object> nativeObject || None
			\return		<bool> success
		"""
		
		type = nativeObject.Type

		if type in 'polymsh':
			return ObjectType.Geometry
			
		if type == 'surfmsh':
			return ObjectType.NurbsSurface
			
		if type == 'crvlist':
			return ObjectType.Curve
			
		elif type == 'light':
			return ObjectType.Light
		
		elif type == 'camera':
			return ObjectType.Camera
			
		elif type == '#model':
			return ObjectType.Model
			
		elif type == '#Group':
			return ObjectType.Group
	
		return AbstractSceneObject._typeOfNativeObject( nativeObject )

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObject', SoftimageSceneObject )

