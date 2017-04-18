##
#	\namespace	cross3d.studiomax.studiomaxscene
#
#	\remarks	The StudiomaxScene class will define all the operations for Studiomax scene interaction.
#
#	\author		eric
#	\author		Blur Studio
#	\date		03/15/10
#

import os
import re
import glob
import getpass
import win32con
import win32api
import traceback
import math

import cross3d
from Py3dsMax import mxs
from Qt.QtCore import QTimer
from cross3d import UserProps, application, FrameRange, constants
from cross3d.abstract.abstractscene import AbstractScene
from cross3d.constants import UpVector, ExtrapolationType, RendererType


# register custom attriutes for MAXScript that hold scene persistent data
from mxscustattribdef import MXSCustAttribDef

#-----------------------------------------------------------------------------


class EnvironmentMapHolder(MXSCustAttribDef):

	@classmethod
	def define(cls):
		cls.setAttrName('OnionMapHolder')
		cls.defineParam('environmentMap', 'textureMap', paramId='eMap')

EnvironmentMapHolder.register()

#-----------------------------------------------------------------------------


class EnvironmentMapsHolder(MXSCustAttribDef):

	def init(self):
		MXSCustAttribDef.init(self)
		self.setValue('environmentMaps', [])

	@classmethod
	def define(cls):
		cls.setAttrName('OnionAltMapsHolder')
		cls.defineParam('environmentMaps', 'textureMapTab', paramId='aMps')
		cls.defineParam('currentIndex', 'integer', paramId='mi')

EnvironmentMapsHolder.register()

#-----------------------------------------------------------------------------


class CustomProperties(MXSCustAttribDef):

	def init(self):
		MXSCustAttribDef.init(self)
		self.setValue('keys', [])
		self.setValue('values', [])

	@classmethod
	def define(cls):
		cls.setAttrName('BlurCustomProperties')
		cls.defineParam('keys', 'stringTab')
		cls.defineParam('values', 'stringTab')

CustomProperties.register()

#-----------------------------------------------------------------------------


class SceneMetaData(MXSCustAttribDef):
	version = 1.63

	def __init__(self, mxsInstance):
		MXSCustAttribDef.__init__(self, mxsInstance)

		self._mapsHolder = None
		self._mapHolder = None
		self._custProperties = None

	def customProperties(self):
		# pull the custom properties value
		if (not self._custProperties):
			root = mxs.rootNode
			data = CustomProperties.find(root)
			if (not data):
				data = CustomProperties.createUnique(root)
			self._custProperties = data

		return self._custProperties

	def environmentMapCache(self):
		# pull the map holder value
		if (not self._mapHolder):
			root = mxs.rootNode
			data = EnvironmentMapHolder.find(root)
			if (not data):
				data = EnvironmentMapHolder.createUnique(root)
			self._mapHolder = data

		return self._mapHolder

	def environmentMapsCache(self):
		# pull the map holder value
		if (not self._mapsHolder):
			root = mxs.rootNode
			data = EnvironmentMapsHolder.find(root)
			if (not data):
				data = EnvironmentMapsHolder.createUnique(root)
			self._mapsHolder = data

		return self._mapsHolder

	def init(self):
		MXSCustAttribDef.init(self)

		self.setValue('version', SceneMetaData.version)
		self.setValue('layerGroupNames', ['Main'])
		self.setValue('layerGroupStates', [True])

	@classmethod
	def define(cls):
		cls.setAttrName('OnionData')

		# define overall parameters
		cls.defineParam('version', 'float', paramId='v')

		# define layer groups
		cls.defineParam('layerGroupNames', 'stringTab', paramId='gn')
		cls.defineParam('layerGroupStates', 'boolTab', paramId='go')

		# define the scene material override list
		cls.defineParam('materialLibraryList', 'materialTab', paramId='mtl')

		# define the material cache
		cls.defineParam('baseMaterialCache', 'materialTab', paramId='ms')

SceneMetaData.register()

#------------------------------------------------------------------------------------------------------------------------


class StudiomaxScene(AbstractScene):

	# This is the time at which the application FBX export preset was changed by our exportObjectsToFBX method.
	# It allows use to detect if the preset file was changed in between two exports and make sure we reload the preset if necessary.
	# After a long and painful research, showing the GUI of the native exporter seems to be the only way to have max load the preset file stored in the user folder.
	_fbxIOPresetModifiedTime = 0
	_orignalFBXPresets = {}

	def __init__(self):
		AbstractScene.__init__(self)

		# create custom properties
		self._metaData = None
		self._mapCache = None
		self._connectDefined = False

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	def _cacheNativeMaterial(self, cacheType, nativeMaterial):
		"""
			\remarks	implements the AbstractScene._cacheNativeMaterial method to cache the inputed material in the scene
			\param		cacheType		<cross3d.constants.MaterialCacheType>
			\param		nativeMaterial	<Py3dsMax.mxs.Material>
			\return		<bool> changed
		"""
		from cross3d.constants import MaterialCacheType

		# cache alternate materials
		if (cacheType == MaterialCacheType.BaseMaterial):
			data = self.metaData()
			cache = list(data.value('baseMaterialCache', []))

			# record the scene data
			if (nativeMaterial and not nativeMaterial in cache):
				cache.append(nativeMaterial)
				data.setValue('baseMaterialCache', cache)
				return True

		return False

	def _cachedNativeMaterial(self, cacheType, materialId, default=None):
		"""
			\remarks	implements the AbstractScene._cachedNativeMaterial method to return the cached material for the inputed material id
			\param		cacheType		<cross3d.constants.MaterialCacheType>
			\param		materialId		<str>
			\param		default			<variant>	value to return if the id was not found
			\return		<Py3dsMax.mxs.Material> nativeMaterial
		"""
		unique_id = mxs.blurUtil.uniqueId
		cache = self._cachedNativeMaterials(cacheType)

		for mtl in cache:
			if (mtl == None):
				continue

			uid = str(unique_id(mtl))
			unm = str(mtl.name)

			if (materialId == uid or materialId == unm):
				return mtl
		return None

	def _cachedNativeMaterials(self, cacheType):
		"""
			\remarks	implements the AbstractScene._cachedNativeMaterials method to return the cached material for the inputed material cache type
			\param		cacheType	<cross3d.constants.MaterialCacheType>
			\return		<list> [ <Py3dsMax.mxs.Material> nativeMaterial, .. ]
		"""
		from cross3d.constants import MaterialCacheType

		# return override material list
		if (cacheType == MaterialCacheType.MaterialOverrideList):
			return self.metaData().value('materialLibraryList')

		# return alternate material cache
		if (cacheType == MaterialCacheType.BaseMaterial):
			return self.metaData().value('baseMaterialCache')

		return []

	def _cacheNativeMap(self, cacheType, nativeMap):
		"""
			\remarks	implements the AbstractScene._cacheNativeMap method to cache the inputed map in the scene
			\param		cacheType	<cross3d.constants.MapCacheType>
			\param		nativeMap	<Py3dsMax.mxs.TextureMap>
			\return		<bool> changed
		"""
		from cross3d.constants import MapCacheType

		# return alternate environment map caches
		if (cacheType == MapCacheType.EnvironmentMap):
			data = self.metaData().environmentMapsCache()
			maps = list(data.value('environmentMaps'))
			maps.append(nativeMap)
			data.setValue('environmentMaps', maps)

		return False

	def _cachedNativeMap(self, cacheType, uniqueId, default=None):
		"""
			\remarks	implements the AbstractScene._cachedNativeMap method to return the cached map for the inputed map id
			\param		cacheType		<cross3d.constants.MapCacheType>
			\param		uniqueId			<str>
			\param		default			<variant>	value to return if the id was not found
			\return		<Py3dsMax.mxs.TextureMap> nativeMap
		"""
		unique_id = mxs.blurUtil.uniqueId
		cache = self._cachedNativeMaps(cacheType)

		for nativeMap in cache:
			if (nativeMap == None):
				continue

			uid = str(unique_id(nativeMap))
			unm = str(nativeMap.name)

			if (uniqueId == uid or uniqueId == unm):
				return nativeMap
		return None

	def _cachedNativeMaps(self, cacheType):
		"""
			\remarks	implements the AbstractScene._cachedNativeMaps method to return the cached maps for the given type from the scene
			\param		cacheType		<cross3d.constants.MapCacheType>
			\return		<list> [ <Py3dsMax.mxs.TextureMap> nativeMap, .. ]
		"""
		from cross3d.constants import MapCacheType

		# return alternate environment map caches
		if (cacheType == MapCacheType.EnvironmentMap):
			data = self.metaData().environmentMapsCache()
			return data.value('environmentMaps')

		return []

	def _clearNativeMaterialOverride(self, nativeObjects):
		"""
			\remarks	implements AbstractScene._clearNativeMaterialOverride method to clear the native override materials from the inputed objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		from cross3d.constants import MaterialCacheType
		from cross3d.studiomax import StudiomaxAppData

		# store the methods we're going to use
		get_userprop = mxs.getUserProp
		set_userprop = mxs.setUserProp
		get_appdata = mxs.getAppData
		del_appdata = mxs.deleteAppData
		superclassof = mxs.superClassOf
		geoclass = mxs.GeometryClass

		for obj in nativeObjects:
			# ignore non-geometric objects
			if (not superclassof(obj) == geoclass):
				continue

			# pull the app data
			mid = get_appdata(obj, int(StudiomaxAppData.AltMtlIndex))

			# pull the user properties
			if (mid == None):
				mid = get_userprop(obj, 'basematerial')

			# record the base material if it is not already recorded
			if (mid and mid != 'undefined'):
				# clear the cache data
				del_appdata(obj, int(StudiomaxAppData.AltMtlIndex))
				set_userprop(obj, 'basematerial', 'undefined')

				# restore the original material
				if (mid == '0'):
					obj.material = None
				else:
					obj.material = self._cachedNativeMaterial(MaterialCacheType.BaseMaterial, mid)

		return True

	def _clearNativePropSetOverride(self, nativeObjects):
		"""
			\remarks	implements the AbstractScene._clearNativePropSetOverride method to clear the inputed objects of any overriding property set information
			\param		nativeObjects		<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		# store the methods we're going to use
		from cross3d import SceneObjectPropSet
		from cross3d.studiomax import StudiomaxAppData

		get_appdata = mxs.getAppData
		del_appdata = mxs.deleteAppData
		get_userprop = mxs.getUserProp
		set_userprop = mxs.setUserProp
		altpropindex = int(StudiomaxAppData.AltPropIndex)

		for obj in nativeObjects:
			# restore base properties
			props = get_appdata(obj, altpropindex)
			if (not props):
				props = get_userprop(obj, 'baseprops')

			# restore the property set
			if (props and props != 'undefined'):
				nprop = SceneObjectPropSet(self, None)
				nprop._setValueString(props)
				for key in nprop.propertyNames():
					if (nprop.isCustomProperty(key)):
						set_userprop(obj, key, str(self._toNativeValue(nprop.value(key))))
					else:
						obj.setProperty(key, self._toNativeValue(nprop.value(key)))

				# if this propset is empty, this is all we need to do
				set_userprop(obj, 'baseprops', 'undefined')
				del_appdata(obj, altpropindex)

		return True

	def _createNativeModel(self, name='Model', nativeObjects=[], referenced=False):
		name = 'Model' if not name else name
		output = mxs.Point(cross=False, name=name)
		userProps = UserProps(output)
		userProps['model'] = True

		if nativeObjects:
			for nativeObject in nativeObjects:
				nativeObject.name = '.'.join([name, nativeObject.name])
		nativeObjects.append(output)
		return output

	def _createNativeLayer(self, name, nativeObjects=[]):
		"""
			\remarks	implements the AbstractScene._createNativeLayer method to return a new Studiomax layer
			\param		name			<str>
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<Py3dsMax.mxs.Layer> nativeLayer || None
		"""
		name = unicode(name)
		lay = self._findNativeLayer(name)
		if not lay:
			lay = mxs.layerManager.newLayerFromName(name)
		if lay:
			from cross3d import SceneLayer
			SceneLayer(self, lay)._addNativeObjects(nativeObjects)
		return lay

	def _createNativeLayerGroup(self, name, nativeLayers=[]):
		"""
			\remarks	implements the AbstractScene._createNativeLayerGroup method to create a new layer group in this scene based on the inputed name with the given layers
			\param		name			<str>
			\return		<str> nativeLayerGroup || None
		"""
		names = list(self.metaData().value('layerGroupNames'))
		states = list(self.metaData().value('layerGroupStates'))
		if (not name in names):
			names.append(str(name))
			states.append(True)
			self.metaData().setValue('layerGroupNames', names)
			self.metaData().setValue('layerGroupStates', states)
			return name
		return ''

	def _createNativeCamera(self, name='Camera', type='Standard', target=None, rotationOrder=None):
		"""
			\remarks	implements the AbstractScene._createNativeCamera method to return a new Studiomax camera
			\param		name			<str>
			\return		<variant> nativeCamera || None
		"""
		if type == 'Physical':
			if application.version() < 18:
				nativeCamera = mxs.VRayPhysicalCamera(target=target) if target else mxs.VRayPhysicalCamera()
			else:
				nativeCamera = mxs.Physical(target=target) if target else mxs.Physical()
		else:
			nativeCamera = mxs.FreeCamera()

		nativeCamera.name = name
		return nativeCamera

	def _createNativeRenderer(self, rendererType):
		"""
			\remaks		implements AbstractScene._createNativeRenderer to create a new renderer based on the inputed rendererType for this scene
			\param		rendererType		<cross3d.constants.RendererType>
			\return		<Py3dsMax.mxs.Renderer> nativeRenderer || None
		"""
		from cross3d.constants import RendererType

		# create a scanline renderer
		if (rendererType == RendererType.Scanline):
			return mxs.Default_Scanline_Renderer()

		# create a Mental Ray renderer
		elif (rendererType == RendererType.MentalRay):
			return mxs.mental_ray_renderer()

		# create a VRay renderer
		elif (rendererType == RendererType.VRay):
			renderers = mxs.rendererClass.classes

			# find the installed V_Ray renderer
			for renderer in renderers:
				clsname = str(renderer)
				if (not clsname.startswith('V_Ray_RT') and clsname.startswith('V_Ray_')):
					return renderer()

		# create a specific renderer
		else:
			renderers = mxs.rendererClass.classes

			# find the installed V_Ray renderer
			for renderer in renderers:
				clsname = str(renderer)
				if (clsname == rendererType):
					return renderer()

		return None

	def _createNativeTarget(self, name='Camera.Target'):
		"""
			\remarks	builds and returns an mxs.targetobject
			\return		<Py3dsMax.mxs.Targetobject> || None
		"""
		return mxs.targetobject(name=name)

	def _currentNativeCamera(self):
		"""
			\remarks	implements AbstractScene._currentNativeCamera method to return the current native camera that is in the viewport for the scene
			\return		<Py3dsMax.mxs.Camera> || None
		"""
		return mxs.viewport.getCamera()

	def _currentNativeRenderer(self):
		"""
			\remarks	implements AbstractScene._currentNativeRenderer method to return the current native renderer for this scene instance
			\return		<Py3dsMax.mxs.Renderer> nativeRenderer || None
		"""
		return mxs.renderers.current

	def _exportNativeObjects(self, objects, filename=''):
		"""
			\remarks	implements the AbstractScene._exportNativeObjects method to save out individual objects to a file
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		filename		<str>
			\return		<bool> success
		"""
		return mxs.saveNodes(objects, filename)

	def _findNativeObject(self, name='', uniqueId=0):
		"""
			\remarks	implements the AbstractScene._findNativeObject to look up an object based on the inputed name
			\sa			findNativeObject
			\param		name	<str>
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		name = str(name)
		output = None
		if (name):
			output = mxs.getNodeByName(str(name))

		if (not output and uniqueId):
			output = mxs.refByUniqueId(uniqueId)

		return output

	def _findNativeLayer(self, name='', uniqueId=0):
		"""
			\remarks	implements the AbstractScene._findNativeLayer to look up a layer based on the inputed name
			\sa			findNativeLayer
			\param		name	<str>
			\return		<Py3dsMax.mxs.Layer> nativeLayer || None
		"""
		if (name == 'World Layer'):
			name = '0'

		output = None
		if (name):
			output = mxs.layerManager.getLayerFromName(str(name))

		if (not output and uniqueId):
			output = mxs.layerManager.refByUniqueId(uniqueId)

		return output

	def _findNativeLayerGroup(self, name='', uniqueId=0):
		"""
			\remarks	implements the AbstractScene._findNativeLayerGroup to look up a layer group based on the inputed name
			\sa			findNativeLayer
			\param		name	<str>
			\return		<str> nativeLayerGroup || None
		"""
		names = list(self.metaData().value('layerGroupNames'))
		name = str(name)
		if (name in names):
			return name
		return None

	def _findNativeMaterial(self, materialName='', materialId=0):
		"""
			\remarks	implements the AbstractScene._findNativeMaterial to look up an material based on the inputed name
			\sa			findNativeMaterial
			\param		materialName	<str>
			\return		<Py3dsMax.mxs.Material> nativeMaterial || None
		"""
		materialName = str(materialName)
		if (not (materialName or materialId)):
			return None

		uniqueid = mxs.blurUtil.uniqueId
		for material in self._nativeMaterials():
			if (material.name == materialName or uniqueid(material) == materialId):
				return material

		cross3d.logger.debug('could not find material (%s - %s)' % (materialName, materialId))

		return None

	def _findNativeMap(self, name='', uniqueId=0):
		"""
			\remarks	implements the AbstractScene._findNativeMap to look up an map based on the inputed name
			\sa			findNativeMap
			\param		name	<str>
			\return		<Py3dsMax.mxs.Map> nativeMap || None
		"""
		name = str(name)

		if (not (name or uniqueId)):
			return None

		uniqueid = mxs.blurUtil.uniqueId
		for nmap in self._collectNativeMaps():
			if (nmap.name == name or uniqueid(nmap) == uniqueId):
				return nmap

		return None

	def _freezeNativeObjects(self, nativeObjects, state):
		"""
			\remarks	implements the AbstractScene._freezeNativeObjects method to freeze(lock)/unfreeze(unlock) the inputed objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		if (state):
			mxs.freeze(nativeObjects)
		else:
			mxs.unfreeze(nativeObjects)
		# this does not seem to update the viewports so call scene update
		application.refresh()
		return True

	def _hideNativeObjects(self, nativeObjects, state):
		"""
			\remarks	implements the AbstractScene._hideNativeObjects method to hide/unhide the inputed objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		state			<bool>
			\return		<bool> success
		"""
		if (state):
			mxs.hide(nativeObjects)
		else:
			mxs.unhide(nativeObjects)
		# this does not seem to update the viewports so call scene update
		application.refresh()
		return True

	def _fromNativeValue(self, nativeValue):
		"""
			\remarks	re-implements the AbstractScene._fromNativeValue method to convert
						some native maxscript values to proper python/pyqt values
			\param		nativeValue		<variant>
			\return		<variant>
		"""
		classof = mxs.classof
		cls = classof(nativeValue)

		# return the value as a QColor
		if (cls == mxs.Color):
			from Qt.QtGui import QColor
			return QColor(nativeValue.r, nativeValue.g, nativeValue.b)

		# convert value from a Time
		if (cls == mxs.Time):
			return int(nativeValue)

		# convert from name to a String
		if (cls == mxs.Name):
			return str(nativeValue)

		# return the standard value
		# by default, we assume all conversions have already occurred
		return nativeValue
#		return AbstractScene._fromNativeValue( self, nativeValue )

	def _getNativeObject(self):
		"""
			\remarks	[abstract]	invokes the application's ability to let a user select a Object from the scene
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		return mxs.selectByName(single=True)

	def _getNativeMaterial(self):
		"""
			\remarks	implements the AbstractScene._getNativeMaterial method to invoke the application's ability to let a user select a Material from the scene
			\return		<Py3dsMax.mxs.Material> nativeMaterial || None
		"""
		return mxs.materialBrowseDlg(mxs.pyhelper.namify("mats"))

	def _getNativeMap(self):
		"""
			\remarks	implements the AbstractScene._getNativeMap method to invoke the application's ability to let a user select a Map from the scene
			\return		<Py3dsMax.mxs.TextureMap> nativeMap || None
		"""
		return mxs.materialBrowseDlg(mxs.pyhelper.namify("maps"))

	def _loadNativeMaterialsFromLibrary(self, filename=''):
		"""
			\remarks	[abstract] loads a bunch of materials from the inputed library location, or prompts the user to select a library when not provided
			\param		filename	<str>
			\return		<list> [ <Py3dsMax.mxs.TextureMap> nativeMaterial, .. ]
		"""
		from Qt.QtGui import QFileDialog
		filename = QFileDialog.getOpenFileName(None, 'Load Material Library', '', 'Material Library files (*.mat)')
		if (filename):
			is_kindof = mxs.isKindOf
			TextureMap = mxs.TextureMap
			mlib = mxs.loadTempMaterialLibrary(str(filename))
			output = [mtl for mtl in mlib if not is_kindof(mtl, TextureMap)]

			# clear the material library - this is a memory intensive section
			del mlib
			mxs.gc()

			return output
		return []

	def _saveNativeMaterialsToLibrary(self, filename=''):
		"""
			\remarks	saves materials to the given library, or prompts the user to select a save location if none is given
			\param		filename	<str>
			\return		<bool>		success
		"""
		from Qt.QtGui import QFileDialog
		filename = QFileDialog.getSaveFileName(None, 'Save Material Library', '', 'Material Library files (*.mat)')
		filename = str(filename)
		if (filename):
			if not filename.endswith('.mat'):
				filename = '{base}.mat'.format(base=filename)
			mxs.saveTempMaterialLibrary(mxs.sceneMaterials, filename)
		return True

	def _nativeActiveLayer(self):
		"""
			\remarks	implements the AbstractScene._nativeActiveLayer method to return the native active layer from the scene
			\param		name			<str>
			\return		<Py3dsMax.mxs.Layer> nativeLayer || None
		"""
		return mxs.layerManager.current

	def _nativeAtmospherics(self):
		"""
			\remarks	implements the AbstractScene._nativeAtmospherics method to return a list of the atmospheric instances in this scene
			\return		<list> [ <Py3dsMax.mxs.Atmospheric> nativeAtmospheric, .. ]
		"""
		get_atmos = mxs.getAtmospheric
		get_effect = mxs.getEffect
		return [get_atmos(i + 1) for i in range(mxs.numAtmospherics)] + [get_effect(i + 1) for i in range(mxs.numEffects)]

	def _nativeCustomProperty(self, key, default=None):
		"""
			\remarks	implements the AbstractScene._nativeCustomProperty method to return a value for the inputed key for a custom scene property
			\param		key		<str>
			\param		default	<variant>
			\return		<variant>
		"""
		key = str(key)
		props = self.metaData().customProperties()
		keys = list(props.value('keys'))
		if (key in keys):
			values = list(props.value('values'))
			return values[keys.index(key)]
		return default

	def _nativeEnvironmentMap(self):
		"""
			\remarks	implements the AbstractScene._nativeEnvironmentMap method to return the native map for the environment of this scene
			\return		<Py3dsMax.mxs.TextureMap> nativeMap || None
		"""
		return mxs.environmentMap

	def _nativeEnvironmentMapOverride(self):
		"""
			\remarks	implements the AbstractScene._nativeEnvironmentMapOverride method to return the native map for the environment of this scene
			\return		<Py3dsMax.mxs.TextureMap> nativeMap || None
		"""
		data = self.metaData().environmentMapsCache()
		index = data.value('currentIndex')
		if (index):
			maps = list(data.value('environmentMaps'))
			return maps[index - 1]
		return None

	def _nativeFxs(self):
		"""
			\remarks	implements the AbstractScene._nativeFx method to return a list of the fx instances in this scene
			\return		<list>
		"""
		from cross3d.constants import ObjectType
		tps = [o for o in self.objects() if o.objectType() & ObjectType.Thinking]

		def _crawlForSubDyns(dynset):
			if not dynset:
				return []
			from copy import copy
			subs = mxs.cross3dhelper.getSubDyns(dynset)
			subs = [s for s in subs if hasattr(s, 'name') and s.name.startswith('DS:')]
			finalList = copy(subs)
			for sub in subs:
				if mxs.cross3dhelper.getSubDyns(sub):
					finalList.extend(_crawlForSubDyns(sub))
			return finalList

		fxInstances = []
		for tp in tps:
			fxInstances.extend(_crawlForSubDyns(tp.nativePointer().dynamic_master))

		return fxInstances

	def _nativeLayers(self, wildcard=''):
		"""
			\remarks	implements the AbstractScene._nativeLayers method to return a list of the native layers in this scene
			\return		<list> [ <Py3dsMax.mxs.Layer> nativeLayer, .. ]
		"""
		layerManager = mxs.layerManager
		count = layerManager.count
		getLayer = layerManager.getLayer
		layers = [getLayer(i) for i in range(count)]

		if wildcard:

			# This will replace any "*" into ".+" therefore converting basic star based wildcards into a regular expression.
			expression = re.sub(r'(?<!\\)\*', r'.*', wildcard)
			if not expression[-1] == '$':
				expression += '$'

			holder = []
			for layer in layers:
				if re.match(expression, layer.name, re.I):
					holder.append(layer)
			return holder

		else:
			return layers

	def _nativeLayerGroups(self):
		"""
			\remarks	implements the AbstractScene._nativeLayerGroups method to return a list of the native layer groups in this scene
			\return		<list> [ <str> nativeLayerGroup, .. ]
		"""
		# If there's no metadata value for group names, then there are
		# no layer groups.
		try:
			return self.metaData().value('layerGroupNames')
		except RuntimeError:
			return []

	def _nativeMaterials(self, baseMaterials=False):
		#get_instances	= mxs.getClassInstances
		#mclasses 		= mxs.Material.classes
		#output			= []

		# collect all the materials
		# for mclass in mclasses:
		#	output += get_instances(mclass)
		output = list(mxs.sceneMaterials)

		# include material list
		mlist = list(self.metaData().value('materialLibraryList'))
		for m in mlist:
			if (m and not m in output):
				output.append(m)

		# include material cache
		mcache = list(self.metaData().value('baseMaterialCache'))
		for m in mcache:
			if (m and not m in output):
				output.append(m)

		# include layer materials
		for layer in self.layers():
			for m in layer._nativeAltMaterials():
				if (m and not m in output):
					output.append(m)

		# define the material cache
		return output

	def _nativeMaps(self):
		get_instances = mxs.getClassInstances
		output = get_instances(mxs.BitmapTexture)

		# include material list
		mlist = list(self.metaData().environmentMapsCache().value('environmentMaps'))
		for m in mlist:
			if (m and not m in output):
				output.append(m)

		return output

	def _nativeObjects(self, getsFromSelection=False, wildcard='', objectType=0):
		"""
			\remarks	implements the AbstractScene._nativeObjects method to return the native objects from the scene
			\return		<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
		"""

		# TODO: Needs to be severely optimzed. Using "nativeType = SceneObject._abstractToNativeObjectType.get(type)".

		if getsFromSelection:
			objects = mxs.selection
		else:
			objects = mxs.objects

		# Processing the wildcard.
		if wildcard:

			# This will replace any "*" into ".+" therefore converting basic star based wildcards into a regular expression.
			expression = re.sub(r'(?<!\\)\*', r'.*', wildcard)
			if not expression[-1] == '$':
				expression += '$'
			holder = []
			for obj in objects:
				if re.match(expression, obj.name, flags=re.I):
					holder.append(obj)
			ret = holder

		else:
			ret = objects

		if objectType:
			holder = []
			from cross3d import SceneObject
			for obj in ret:
				if SceneObject._typeOfNativeObject(obj) == objectType:
					holder.append(obj)
			ret = holder

		return ret

	def _nativeSelection(self, wildcard=''):
		return self._nativeObjects(getsFromSelection=True, wildcard=wildcard)

	def _nativeRootObject(self):
		"""
			\remarks	implements the AbstractScene._nativeRootObject to return the native root object of the scene
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		return mxs.rootNode

	def _nativeWorldLayer(self):
		"""
			\remarks	implements the AbstractScene._nativeWorldLayer to return the native world layer of the scene
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		return mxs.layerManager.getLayer(0)

	def _removeNativeObjects(self, nativeObjects):
		"""
			\remarks	implements the AbstractScene._removeNativeObjects to remove the inputed objects from the scene
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		mxs.delete(nativeObjects)
		return True

	def _renameNativeObjects(self, nativeObjects, names, display=True):
		"""
			\remarks	implements the AbstractScene._renameNativeObjects to rename the inputed objects from the scene
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		names			<list> [ <str> name, .. ]
			\param		display			<bool> 	flags whether or not the names are display names or object names
			\return		<bool> success
		"""
		# make sure we have the proper number of names and objects
		if (len(names) != len(nativeObjects)):
			return False

		# keep the model names when changing display only
		if (display):
			for i, obj in enumerate(nativeObjects):
				n = obj.name
				if ('.' in n):
					splt = n.split('.')
					splt[-1] = names[i]
					names[i] = '.'.join(splt)

		# set the names
		mxs.blurUtil.setNames(nativeObjects, names)
		return True

	def _setCachedNativeMaps(self, cacheType, nativeMaps):
		"""
			\remarks	implements the AbstractScene._cachedNativeMaps method to set the cached maps for the given type from the scene
			\param		cacheType		<cross3d.constants.MapCacheType>
			\param		nativeMaps		<list> [ <Py3dsMax.mxs.TextureMap> nativeMap, .. ]
			\return		<bool> success
		"""
		from cross3d.constants import MapCacheType

		# return alternate environment map caches
		if (cacheType == MapCacheType.EnvironmentMap):
			data.setValue('environmentMaps', nativeMaps)
			return True

		return True

	def _setCachedNativeMaterials(self, cacheType, nativeMaterials):
		"""
			\remarks	implements the AbstractScene._cachedNativeMaterials method to set the cached materials for the given type from the scene
			\param		cacheType			<cross3d.constants.MaterialCacheType>
			\param		nativeMaterials		<list> [ <Py3dsMax.mxs.Material> nativeMaterial, .. ]
			\return		<bool> success
		"""
		from cross3d.constants import MaterialCacheType

		# return override material list
		if (cacheType == MaterialCacheType.MaterialOverrideList):
			self.metaData().setValue('materialLibraryList', nativeMaterials)
			return True

		# return alternate material cache
		if (cacheType == MaterialCacheType.BaseMaterial):
			self.metaData().setValue('baseMaterialCache', nativeMaterials)
			return True

		return False

	def _setCurrentNativeRenderer(self, nativeRenderer):
		"""
			\remarks	implements the AbstractScene._setCurrentNativeRenderer method to set the current renderer to the inputed native renderer
			\param		nativeRenderer	<variant>
			\return		<bool> success
		"""
		mxs.pyhelper.setCurrentRenderer(nativeRenderer)
		return True

	def _setNativeCustomProperty(self, key, value):
		"""
			\remarks	implements the AbstractScene._nativeCustomProperty method to set a value for the inputed key for a custom scene property
			\param		key		<str>
			\param		value	<variant>
			\return		<bool> success
		"""
		key = str(key)
		value = str(value)
		props = self.metaData().customProperties()
		keys = list(props.value('keys'))
		values = list(props.value('values'))

		# replace an existing property
		if (key in keys):
			values[keys.index(key)] = value

		# set a new property
		else:
			keys.append(key)
			values.append(value)

		props.setValue('keys', keys)
		props.setValue('values', values)

		return True

	def _setNativeEnvironmentMap(self, nativeMap):
		"""
			\remarks	implements the AbstractScene._setNativeEnvironmentMap method to set the environment map for this scene
			\param		nativeMap 	<Py3dsMax.mxs.Material> || None
			\return		<bool> success
		"""
		mxs.environmentMap = nativeMap
		return True

	def _setNativeEnvironmentMapOverride(self, nativeMap):
		"""
			\remarks	implements the AbstractScene._setNativeEnvironmentMapOverride method to set the environment map override for this scene
			\param		nativeMap 	<Py3dsMax.mxs.TextureMap> || None
			\return		<bool> success
		"""
		data = self.metaData().environmentMapsCache()
		basedata = self.metaData().environmentMapCache()

		# if we are going into an override state
		if (nativeMap):
			# record the current map to the backup cache
			if (data.value('currentIndex') == 0):
				basedata.setValue('environmentMap', mxs.environmentMap)

			# make sure the map is cached as an override option
			maps = list(data.value('environmentMaps'))
			if (not nativeMap in maps):
				maps.append(nativeMap)
				data.setValue('environmentMaps', nativeMap)

			# set the override in the system
			data.setValue('currentIndex', maps.index(nativeMap) + 1)
			mxs.environmentMap = nativeMap
			return True

		# otherwise, restore the base state
		else:
			mxs.environmentMap = basedata.value('environmentMap')
			basedata.setValue('environmentMap', None)
			data.setValue('currentIndex', 0)
			return True

	def _setNativePropSetOverride(self, nativeObjects, nativePropSet):
		"""
			\remarks	implements the AbstractScene._setNativePropSetOverride method to set the inputed objects with an overriding property set
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		nativePropSet	<cross3d.SceneObjectPropSet>
			\return		<bool> success
		"""
		from cross3d import SceneObjectPropSet
		from cross3d.studiomax import StudiomaxAppData

		get_appdata = mxs.getAppData
		del_appdata = mxs.deleteAppData
		set_appdata = mxs.setAppData
		get_prop = mxs.getProperty
		set_prop = mxs.setProperty
		get_userprop = mxs.getUserProp
		set_userprop = mxs.setUserProp
		altpropindex = int(StudiomaxAppData.AltPropIndex)
		empty = not nativePropSet.isActive()
		values = [(key, nativePropSet.value(key), nativePropSet.isCustomProperty(key)) for key in nativePropSet.activeProperties()]

		for obj in nativeObjects:
			# restore base properties
			props = get_appdata(obj, altpropindex)
			if (not props):
				props = get_userprop(obj, 'baseprops')

			# restore the property set
			if (props and props != 'undefined'):
				nprop = SceneObjectPropSet(self, None)
				nprop._setValueString(props)
				for key in nprop.propertyNames():
					if (nprop.isCustomProperty(key)):
						set_userprop(obj, key, str(self._toNativeValue(nprop.value(key))))
					else:
						obj.setProperty(key, self._toNativeValue(nprop.value(key)))

				# if this propset is empty, this is all we need to do
				if (empty):
					set_userprop(obj, 'baseprops', 'undefined')
					del_appdata(obj, altpropindex)
					continue

			# record the base state if it is not already recorded
			elif (not empty):
				nprop = SceneObjectPropSet(self, None)
				nprop.activateProperties(True)

				# go through and pull the values
				for key in nprop.propertyNames():
					# The gbufferchannel property should be treated like a
					# native property, but removing it from the custom property
					# list breaks myriad other things.  The simple solution is to
					# allow it to act as both by putting the additional condition
					# here.  If this were not there any time you unset an altprop
					# on a layer object ids would revert to a 0 value even if the
					# user had set them to something else by hand via the Max
					# interface.
					if nprop.isCustomProperty(key) and key != 'gbufferchannel':
						value = get_userprop(obj, key)
					else:
						value = obj.property(key)

					if (value != None):
						nprop.setValue(key, self._fromNativeValue(value))

				# collect the initial base properties
				valueString = nprop._valueString()
				set_userprop(obj, 'baseprops', valueString)
				set_appdata(obj, altpropindex, valueString)

			# pass this object if it is null
			else:
				continue

			# apply this property if it is not empty
			for key, value, custom in values:
				if (custom):
					set_userprop(obj, key, str(self._toNativeValue(value)))
				else:
					obj.setProperty(key, self._toNativeValue(value))

		return True

	def _setNativeMaterialOverride(self, nativeObjects, nativeMaterial, options=None, advancedState=None):
		"""
			\remarks	implements AbstractScene._setNativeMaterialOverride to apply this material as an override to the inputed objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		nativeMaterial	<Py3dsMax.mxs.Material> nativeMaterial
			\param		options			<cross3d.constants.MaterialOverrideOptions>
			\param		advancedState	<dict> { <int> baseMaterialId: ( <blur3d.gui.SceneMaterial> override, <bool> ignored ) }
			\return		<bool> success
		"""
		from cross3d.constants import MaterialOverrideOptions, MaterialCacheType
		from cross3d.studiomax import matlib
		from cross3d.studiomax import StudiomaxAppData

		# use the advanced state for the override system
		if (advancedState == None):
			advancedState = {}

		# store the methods we're going to use
		get_userprop = mxs.getUserProp
		set_userprop = mxs.setUserProp
		get_appdata = mxs.getAppData
		set_appdata = mxs.setAppData
		superclassof = mxs.superClassOf
		geoclass = mxs.GeometryClass
		unique_id = mxs.blurUtil.uniqueId
		processed = {}

		for obj in nativeObjects:
			# ignore non-geometric objects
			if (not superclassof(obj) == geoclass):
				continue

			# pull the app data
			mid = get_appdata(obj, int(StudiomaxAppData.AltMtlIndex))

			# pull the user properties
			if (mid == None):
				mid = get_userprop(obj, 'basematerial')

			# record the base material if it is not already recorded
			if (not mid or mid == 'undefined'):
				baseMaterial = obj.material

				if (baseMaterial):
					uid = unique_id(baseMaterial)
					set_appdata(obj, int(StudiomaxAppData.AltMtlIndex), str(uid))
					set_userprop(obj, 'basematerial', str(uid))
					self._cacheNativeMaterial(MaterialCacheType.BaseMaterial, baseMaterial)
				else:
					set_appdata(obj, int(StudiomaxAppData.AltMtlIndex), '0')
					set_userprop(obj, 'basematerial', '0')

			# otherwise restore the base material
			else:
				baseMaterial = self._cachedNativeMaterial(MaterialCacheType.BaseMaterial, mid)

			# assign the override for the material based on the options
			uid = unique_id(baseMaterial)

			# look up the advanced system for this material
			advancedMaterial, ignored = advancedState.get(uid, (None, False))

			# if the advanced state says we should ignore this material, then continue processing
			if (ignored):
				obj.material = baseMaterial
				continue

			# use the override material and check to see if we've already processed this material
			overrideMaterial = processed.get(uid)

			# if we have not processed this material yet
			if (not overrideMaterial):
				# check to see if we should use an advanced material option for the override vs. the inputed override
				if (advancedMaterial):
					processMaterial = advancedMaterial.nativePointer()
				else:
					processMaterial = nativeMaterial

				overrideMaterial = matlib.createMaterialOverride(baseMaterial, processMaterial, options=options, advancedState=advancedState)
				processed[uid] = overrideMaterial

			obj.material = overrideMaterial

		return True

	def _setNativeFocus(self, objects):
		"""
			\remarks	sets viewport camera to focus on object
			\param		objects	<list>
			\return		<bool> success
		"""
		# save current selection
		selection = self._nativeSelection()
		# set the objects passed in as the selection
		self._setNativeSelection(objects)
		# focus
		mxs.cross3dHelper.maxZoomExtents()
		# restore previous selection
		self._setNativeSelection(selection)

	def _setNativeSelection(self, selection):
		"""
			\remarks	implements the AbstractScene._setNativeSelection to select the inputed native objects in the scene
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		if isinstance(selection, basestring):
			selection = self._nativeObjects(wildcard=selection)
		if (not selection):
			mxs.clearSelection()
		else:
			# Just make sure that we don't have any none types in
			# the given list, as that will cause a nasty RuntimeError
			# from Max.
			mxs.select([o for o in selection if o])
		return True

	def _setNativeUpdatesEnabled(self, state):
		"""
			\remarks	[virtual] reimplements the AbstractScene._setNativeUpdatesEnabled to enable/disable scene updates
			\sa			setUpdatesEnabled
			\param		state		<bool>
			\return		<bool> success
		"""
		if (state):
			# disable quiet mode
			mxs.setQuietMode(False)

			# enable undo operations
			mxs.theHold.EnableUndo()

			# We're not going to do this anymore.  It appears to cause
			# issues with modifier editing if we flick back and forth
			# between panels without the user's consent when toggling
			# layers in Onion.  Right now that's the only place using
			# the logic in this method, so disabling it is the best
			# course of action. <jbee>
			# reset the command panel state
			# mxs.setCommandPanelTaskMode( self._panelState )
			# self._panelState = None

			# allow panel editing
			# This also appears to cause issues with unrelated modifiers
			# when toggling layers, same as setting the panel task mode.
			# mxs.resumeEditing()

			# enable scene redrawing and refresh the views
			while (mxs.isSceneRedrawDisabled()):
				mxs.enableSceneRedraw()

			mxs.redrawViews()

		else:
			# enable quiet mode
			mxs.setQuietMode(True)

			# disallow panel editing
			# This also appears to cause issues with unrelated modifiers
			# when toggling layers, same as setting the panel task mode.
			# mxs.suspendEditing()

			# disable the scene redrawing
			mxs.disableSceneRedraw()
			mxs.theHold.DisableUndo()

			# We're not going to do this anymore.  It appears to cause
			# issues with modifier editing if we flick back and forth
			# between panels without the user's consent when toggling
			# layers in Onion.  Right now that's the only place using
			# the logic in this method, so disabling it is the best
			# course of action. <jbee>
			# record the command panel state
			# self._panelState = mxs.getCommandPanelTaskMode()
			# mxs.setCommandPanelTaskMode( mxs.pyhelper.namify('create') )

	def _toNativeValue(self, pyValue):
		"""
			\remarks	[virtual] reimplements the AbstractScene._setNativeUpdatesEnabled to convert the inputed value from Qt/Python to whatever value is required for the native application
			\param		pyValue	<variant>
			\return		<variant>
		"""
		from Qt.QtGui import QColor

		# convert the value from a color
		if (isinstance(pyValue, QColor)):
			return mxs.Color(pyValue.red(), pyValue.green(), pyValue.blue())

		# return the standard value
		return AbstractScene._toNativeValue(self, pyValue)

	def _toggleNativeVisibleState(self, nativeObjects=None, options=None):
		"""
			\remarks	implements the AbstractScene.toggleVisibleOptions method to toggle the visible state of the inputed options for the given objects
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\param		options			<cross3d.constants.VisibilityToggleOptions>
			\return		<bool> success
		"""
		from cross3d.studiomax import cachelib
		from cross3d.constants import VisibilityToggleOptions
		from cross3d.studiomax import cachelib

		# toggle all the visibility options by default
		if (options == None):
			options = VisibilityToggleOptions.All

		if (not options):
			return False

		if (nativeObjects == None):
			nativeObjects = mxs.objects

		# store maxscript values
		superclassof = mxs.superClassOf
		classof = mxs.classof
		B2_Main_Light = mxs.B2_Main_Light
		VRaySun = mxs.VraySun
		VRayIES = mxs.VRayIES
		VRayAmbientLight = mxs.VRayAmbientLight
		Light_Portal = mxs.Light_Portal
		OctaneLight = mxs.OctaneLight
		DaylightLight = mxs.Daylightlight
		IESLight = mxs.IESLight
		XRefObject = mxs.XRefObject
		Missing_Light = mxs.Missing_Light
		Light = mxs.Light
		Event = mxs.Event
		FumeFX = mxs.FumeFX
		PF_Source = mxs.PF_Source
		XMeshLoader = mxs.XMeshLoader
		Frost = mxs.Frost
		VRayStereoscopic = mxs.VRayStereoscopic
		Alembic_Mesh_Geometry = mxs.Alembic_Mesh_Geometry
		Alembic_Mesh_Topology = mxs.Alembic_Mesh_Topology

		for obj in nativeObjects:
			state = not obj.ishidden
			msuper = superclassof(obj)
			mcls = classof(obj)

			# Toggle various types of lights.
			if options & VisibilityToggleOptions.ToggleLights:
				if msuper == Light:
					if mcls == B2_Main_Light:
						obj.base_parameters.enabled_on = state
					elif mcls in (VRaySun, VRayIES, VRayAmbientLight):
						obj.enabled = state
					elif mcls == Light_Portal:
						obj.portal_on = state
						obj.renderable = state
					elif mcls == XRefObject:
						obj.actualBaseObject.on = state
						obj.renderable = state
					elif mcls == Missing_Light:
						print 'Warning: Missing Lights found in the Scene'
					elif mcls in (OctaneLight, DaylightLight, IESLight):
						obj.enabled = state
					else:
						obj.renderable = state
						obj.on = state
					continue

			# toggle fx
			if (options & VisibilityToggleOptions.ToggleFX):
				# update an event
				if (mcls == Event):
					if (obj.layer.name != '0'):
						obj.activate(state)
					continue

				# update a fume effect
				elif (mcls == FumeFX):
					obj.renderable = state
					continue

				# update a particle flow source
				elif (mcls == PF_Source):
					obj.enable_particles = state
					obj.baseObject.activateParticles(state)
					continue

			# Toggle point caches.
			if options & VisibilityToggleOptions.TogglePointCaches:
				mods = [m for m in obj.modifiers]
				mxs.cross3dhelper.togglePointCaches(mods, state)

			# Toggle transform caches.
			if options & VisibilityToggleOptions.ToggleTransformCaches:
				mxs.cross3dhelper.toggleTransformCache(obj, state)

			# Toggle XMeshLoaders to save memory and redraw speed.
			if options & VisibilityToggleOptions.ToggleXMeshes:
				if mcls == XMeshLoader:
					obj.enableViewportMesh = state
					obj.keepMeshInMemory = state

			# Toggle Frost viewport mesh calculation.
			if options & VisibilityToggleOptions.ToggleFrost:
				if mcls == Frost or classof(obj.baseObject) == Frost:
					obj.enableViewportMesh = state
					obj.enableRenderMesh = state

			# Toggle VRayStereoscopic helpers.
			if options & VisibilityToggleOptions.ToggleVRayStereoscopics:
				if mcls == VRayStereoscopic:
					obj.enabled = state

			if options & VisibilityToggleOptions.ToggleAlembic:
				geoMods = [m for m in obj.modifiers if mxs.classof(m) == Alembic_Mesh_Geometry]
				topoMods = [m for m in obj.modifiers if mxs.classof(m) == Alembic_Mesh_Topology]
				for mod in (topoMods + geoMods):
					mod.enabled = state

			# EKH 2011: looks like this isn't actually giving speed increases and really slows down layer toggling
#			if ( options & VisibilityToggleOptions.ToggleCaches ):
#				cachelib.toggleCaches( obj, state )

		return True

	def _findNativeCamera(self, name='', uniqueId=0):
		"""
			\remarks	returns the native cameras in the scene. added by douglas
			\return		<variant> nativeCamera
		"""
		camera = mxs.getNodeByName(name)
		if (mxs.isKindOf(camera, mxs.Camera)):
			return camera
		return None

	def _addToNativeSelection(self, selection):
		"""
			\remarks	implements the AbstractScene._addToNativeSelection to select the inputed native objects in the scene. added by douglas
			\param		nativeObjects	<list> [ <Py3dsMax.mxs.Object> nativeObject, .. ]
			\return		<bool> success
		"""
		if isinstance(selection, basestring):
			selection = self._nativeObjects(wildcard=selection)
		mxs.selectMore(selection)

	def importFBX(self, path, showUI=False, **kwargs):

		# Setting up presets.
		presetPaths = self._fbxIOPresetPaths(action='import')
		templatePath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'fbx_import_preset.pytempl'))

		# Setting up the FBX presets.
		self._setupFBXIOPresets(presetPaths, templatePath, **{'user': getpass.getuser()})

		# We always show UI in debug mode.
		showUI = True if cross3d.debugLevel >= cross3d.constants.DebugLevels.Mid else showUI

		# If the preset has been modified since the last export, we make sure to reload ours by showing the UI.
		if showUI or (presetPaths and os.path.getmtime(presetPaths[0]) > self._fbxIOPresetModifiedTime + 100):

			# If the user did not want to see the UI, we prepare some callbacks that will press the enter key for him.
			if not showUI:

				# Creating a method that presses enter.
				def pressEnter():
					win32api.keybd_event(0x0D, 0x0D, 0, 0)
					win32api.keybd_event(0x0D, 0x0D, win32con.KEYEVENTF_KEYUP, 0)

				# There will be a prompt for the FBX options.
				QTimer.singleShot(200, pressEnter)

				# There might be a second prompt if the file needs to be overwritten.
				if os.path.exists(path):
					QTimer.singleShot(400, pressEnter)

			# Exporting showin the UI.
			mxs.importfile(path)

		else:
			# Calling the FBX exporter without GUI.
			mxs.importfile(path, mxs.pyhelper.namify("noPrompt"))

		# Restoring presets.
		self._restoreFBXIOPresets()

		# TODO: Softimage returns a model. Here we return a boolean. Do we want to make imported FBX into models or maybe return a list of objects?
		return True

	def importMocapToBiped(self, path, bipedCtrl):

		# Get the root node of the biped
		if bipedCtrl and 'Rig' in bipedCtrl.name():

			mix = mxs.cross3dhelper.getMixerController(bipedCtrl)
			trackGrp = mxs.cross3dhelper.getMixerTrackGroup(mix, 1)
			track = mxs.cross3dhelper.getMixerTrack(trackGrp, 1)
			mxs.cross3dhelper.appendMixerClip(track, path, False, 0)

			return True

		return False

	def _importNativeModel(self, path, name='', referenced=False, resolution='', load=True, createFile=False):
		"""
			\remarks	implements the AbstractScene._importNativeModel to import and return a native model from an external file. added by douglas.
			\return		[ <Py3dsMax.mxs.Object> ] models
		"""
		if os.path.exists(path):
			model = None
			modelName = name or os.path.splitext(os.path.split(path)[1])[0]
			objectNames = mxs.getMaxFileObjectNames(path, quiet=True)
			mxs.mergeMAXFile(path, mxs.pyhelper.namify('neverReparent'), mxs.pyhelper.namify('useSceneMtlDups'), quiet=True)
			print objectNames
			# Adding name space to objects.
			for name in objectNames:
				obj = self._findNativeObject(name)
				if not obj:
					continue
				if not model and name == 'Model':
					model = obj
					model.name = modelName
				else:
					if name==None:
						name = 'temp01'
					obj.name = '.'.join([modelName, name])

			# Adding name space to layers.
			for layer in self.layers():
				if 'Model.' in layer.name():
					nativePointer = layer.nativePointer()
					nativePointer.setName(nativePointer.name.replace('Model', modelName))

			return model
		raise Exception('Model file does not exist.')

	def _removeNativeModels(self, models):
		"""
			\remarks	implements the AbstractScene._removeNativeModel to remove a native model in the scene. Addded by douglas
			\param		models [ <PySoftimage.xsi.Model>, ... ]
			\return		<bool> success
		"""
		toRemove = []
		layersToRemove = []

		for model in models:

			# Storing the corresponding layers.
			for layer in self.layers():
				if model.name in layer.name():
					layersToRemove.append(layer)

			toRemove += [model]
			toRemove += self._nativeObjects(wildcard='.'.join([model.name.split('.')[0], '*']))

		self._removeNativeObjects(toRemove)

		# Removing the corresponding layers.
		for layer in layersToRemove:
			layer.remove()

		application.refresh()
		return True

	def _isolateNativeObjects(self, nativeObjects):
		selection = self._nativeSelection()
		self._setNativeSelection(nativeObjects)
		if application.version() >= 16:
			if nativeObjects:
				mxs.IsolateSelection.EnterIsolateSelectionMode()
			else:
				mxs.IsolateSelection.ExitIsolateSelectionMode()
		else:
			mxs.macros.run('Tools', 'Isolate_Selection')
		self._setNativeSelection(selection)
		return True

	def _viewNativeObjectTrajectory(self, obj):
		"""
			\remarks 	creates a null that allows the user to view an objects trajectory
			\param 		<scene object>	object to get trajectory of
			\return 	<bool> 			success
		"""
		objType = unicode(mxs.classOf(obj))
		selectionSave = self._nativeSelection()
		self.clearSelection()

		if objType == 'Biped_Object':
			# get the pelvis and attach point
			tPoint = mxs.Point(cross=True, box=False)
			tPoint.name = obj.name.split('.')[0] + '._Trajectory'
			tPoint.wirecolor = mxs.color(0, 230, 250)

			# align the point to the biped obj
			tPoint.transform = obj.transform

			self.setSelection(tPoint.name)
			tPoint.parent = obj

		else:
			self.setSelection(obj.name)

		mxs.cross3dHelper.toggleTrajectories()
		self._setNativeSelection(selectionSave)

	def _unisolate(self):
		"""
			\remarks	Exits the isolation mode if it is enabled and returns if it had to exit.
			\return		<bool>
		"""
		if application.nameAndVersion() == 'Max2014':
			mxs.IsolateSelection.ExitIsolateSelectionMode()
			application.refresh()
			return True
		else:
			if mxs.Iso2lations == True:
				mxs.Iso2Roll.C2Iso.changed(False)
				return True
		return False

	def exportObjectsToOBJ(self, objects, path, **options):
		self.setSelection(objects)
		mxs.exportFile(path, mxs.pyhelper.namify('noPrompt'), selectedOnly=True)

	def _fbxIOPresetPaths(self, action='export'):

		# Building the preset directory path. Somehow 2016 will still export the preset to 2014's folder.
		if application.version() == 18:
			presetPattern = r'C:\Users\{user}\Documents\3dsMax\FBX\3dsMax2014_X64\Presets\{year}.1\{action}\User defined.fbx{action}preset'
		elif application.version() > 14:
			presetPattern = r'C:\Users\{user}\Documents\3dsMax\FBX\3dsMax{year}_X64\Presets\{year}.0.1\{action}\User defined.fbx{action}preset'
		else:
			presetPattern = r'C:\Users\{user}\Documents\3dsmax\FBX\Presets\{year}.1\{action}\User defined.fbx{action}preset'

		# This path is where the preset should be reading from.
		presetPaths = [presetPattern.format(user=getpass.getuser(), year=application.year(), action=action)]

		# In some cases, presets are being written to a different user folder
		# than the currently logged in user. We will overwrite ALL user
		# settings preferences to make sure the settings are applied. They
		# will all be restored afterwards.
		users = os.listdir(r'C:\Users')
		for user in users:
			presetPattern = r'C:\Users\{}\Documents\3dsmax\FBX\*.fbx{}preset'.format(user, action.lower())
			presetPaths += glob.glob(presetPattern)
		return presetPaths

	def _setupFBXIOPresets(self, presetPaths, templatePath, **kwargs):

		# Note on the hack implemented below:
		# -----------------------------------
		# In max, the FBX import/export settings API is broken. To get around
		# this issue, we take advantage of the fact that the FBX plugin saves
		# its settings as a preset file in the user's directory. We have a
		# template of the desired settings file and we overwrite the existing
		# user settings file (making sure to cache the existing preset so that
		# we can restore it afterwards).  After that settings file is written,
		# we have to make sure the FBX plugin GUI opens for the settings to
		# take effect. Because this would would block scripts, we use win32
		# to click "Enter" on any of the GUI's brought up by the FBX plugin.
		# Also, regardless of the frame range set in the export settings,
		# the plugin will use the current animation range, so we have to set
		# and then restore the animation range to the desired range as well.

		preset = ''
		with open(templatePath, 'r') as f:
			template = f.read()

		# Cache the current presets and overwrite them.
		self._orignalFBXpresetPaths = {}
		for path in presetPaths:

			# Read the current presetPaths and cache them to restore later.
			if os.path.isfile(path):
				with open(path, 'r') as f:
					preset = f.read()
					self._orignalFBXpresetPaths[path] = preset

			preset = template.format(**kwargs)

			try:
				# Creating the path to the preset if not existing.
				if not os.path.isdir(os.path.dirname(path)):
					os.makedirs(os.path.dirname(path))

				with open(path, 'w') as f:
					f.write(preset)

			except OSError:
				# Ignore write permission errors, we can't do anything about them right now.
				traceback.print_exc()

	def _restoreFBXIOPresets(self):
		presetPaths = self._orignalFBXPresets.iteritems()
		path = None
		for path, preset in presetPaths:
			try:
				with open(path, 'w') as f:
					f.write(preset)

			except OSError:
				# Ignore write permission errors, we can't do anything about them right now.
				traceback.print_exc()

		# Storing the time of the FBX export preset modification.
		if path:
			self._fbxIOPresetModifiedTime = os.path.getmtime(path)

	def _exportNativeObjectsToFBX(self, nativeObjects, path, frameRange=None, showUI=True, frameRate=None, upVector=UpVector.Y, **kwargs):
		"""
			Exports a given set of objects as FBX.
			:returns bool: Success
		"""

		# Getting the initial state of things.
		initialSelection = self._nativeSelection()
		initialFrameRange = self.animationRange()
		frameRange = initialFrameRange if not frameRange else frameRange

		# Setting frame range and selection.
		self.setAnimationRange(frameRange)
		self._setNativeSelection(nativeObjects)

		# Setting up presets.
		presetPaths = self._fbxIOPresetPaths(action='export')
		templatePath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'fbx_export_preset.pytempl'))

		# Building the template's kwargs.
		kwargs = {}
		kwargs['user'] = getpass.getuser()
		kwargs['start'] = frameRange[0]
		kwargs['end'] = frameRange[1]
		kwargs['upVector'] = UpVector.labelByValue(upVector)

		# Setting up the FBX presets.
		self._setupFBXIOPresets(presetPaths, templatePath, **kwargs)

		# We always show UI in debug mode.
		showUI = True if cross3d.debugLevel >= cross3d.constants.DebugLevels.Mid else showUI

		# If the preset has been modified since the last export, we make sure to reload ours by showing the UI.
		if showUI or (presetPaths and os.path.getmtime(presetPaths[0]) > self._fbxIOPresetModifiedTime + 100):

			# If the user did not want to see the UI, we prepare some callbacks that will press the enter key for him.
			if not showUI:

				# Creating a method that presses enter.
				def pressEnter():
					win32api.keybd_event(0x0D, 0x0D, 0, 0)
					win32api.keybd_event(0x0D, 0x0D, win32con.KEYEVENTF_KEYUP, 0)

				# There will be a prompt for the FBX options.
				QTimer.singleShot(200, pressEnter)

				# There might be a second prompt if the file needs to be overwritten.
				if os.path.exists(path):
					QTimer.singleShot(400, pressEnter)

			# Exporting showin the UI.
			mxs.exportFile(path, selectedOnly=True, using='FBXEXP')

		else:
			# Calling the FBX exporter without GUI.
			mxs.exportFile(path, mxs.pyhelper.namify('noPrompt'), selectedOnly=True, using='FBXEXP')

		# Restoring frame range and selection.
		self.setAnimationRange(initialFrameRange)
		self._setNativeSelection(initialSelection)

		# Restoring presets.
		self._restoreFBXIOPresets()

		return True

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def cacheXmesh(self, path, objList, start, end, worldLock, stack=3, saveVelocity=True, ignoreTopology=True, samples=1, makeMat=False):
		"""
			\remarks	runXmesh cache function
			\param		models [ <SceneModel>, ... ]
			\return		<bool> success
		"""
		import os
		ignoreEmpty = True
		# local ignoreTopology = true
		# local useObjectSpace = true
		# local saveVelocity = true

		fileExt = os.path.basename(path)
		cacheSplit = os.path.splitext(path)
		cacheName = cacheSplit[0]
		saver = mxs.XMeshSaverUtils
		saver.SetSequenceName(path)
		end = end + 1
		#samples = 10
		substep = 1.0 / samples

		# I have to set the display to ticks in-order to access subframe information. This is to get around not having a proper
		# at time function
		mxs.timeDisplayMode = mxs.pyhelper.namify("frameTicks")
		if makeMat:
			matUtils = mxs.XMeshSaver_MaterialUtils
			theMaterial = matUtils.getMaterialFromNodes(objList)

			theMaterial.name = cacheName + "_MultiMaterial"
			matDir = os.path.splitext(path)
			theMatLibPath = matDir[0] + ".mat"
			if theMaterial.numsubs > 1:

				theMatLib = mxs.materialLibrary()
				mxs.append(theMatLib, theMaterial)
				mxs.saveTempMaterialLibrary(theMatLib, theMatLibPath)

		# Beginning cache record.
		saver.SetSceneRenderBegin()
		for i in range(start, end):

			for j in range(0, samples):
				time = float(i) + substep * j
				mxs.sliderTime = time

				if len(objList) > 1:
					saver.SaveMeshesToSequence(objList, True, True, True)

				else:
					saver.SaveMeshToSequence(objList[0], ignoreEmpty, ignoreTopology, worldLock, saveVelocity)
					# saver.SetSceneRenderEnd()

		saver.SetSceneRenderEnd()
		mxs.timeDisplayMode = mxs.pyhelper.namify("frames")
		return True

	def animationRange(self):
		"""
			\remarks	implements AbstractScene.animationRange method to return the current animation start and end frames
			\return		<cross3d.FrameRange>
		"""
		from cross3d import FrameRange
		r = mxs.animationRange
		return FrameRange((r.start, r.end))

	def globalRange(self):
		return self.animationRange()

	def cloneObjects(self, objects, cloneHierarchy=False, cloneType=constants.CloneType.Copy):
		""" Duplicates the provided objects, optionally keeping the heierarchy.
		:param objects: A list of objects to clone
		:param cloneHierarchy: Duplicate parent child structure in clones. Defaults to False
		:param cloneType: Create clones as copy, instance, etc. Defaults to Copy.
		..seealso:: modules `cross3d.constants.CloneType`
		"""
		cloneObjects = mxs.cross3dhelper.cloneObjects([obj.nativePointer() for obj in objects],
                                               expandHierarchy=cloneHierarchy,
                                               cloneType=mxs.pyhelper.namify(constants.CloneType.labelByValue(cloneType)))
		from cross3d import SceneObject
		return [SceneObject(self, obj) for obj in cloneObjects]

	def checkForSave(self):
		"""
			\remarks	implements AbstractScene.checkForSave method to prompt the user to save and continue, returning false on a user cancel
			\return		<bool> success
		"""
		return mxs.checkForSave()

	def cleanMetaData(self):
		root = mxs.rootNode

		# remove undefined environment maps
		data = EnvironmentMapsHolder.find(root)
		if (data):
			currentIndex = data.value('currentIndex')
			oldMaps = list(data.value('environmentMaps', []))

			newMaps = []
			for i, m in enumerate(oldMaps):
				if (m == None and i <= currentIndex):
					currentIndex -= 1
				elif (m):
					newMaps.append(m)

			data.setValue('currentIndex', currentIndex)
			data.setValue('environmentMaps', newMaps)

		# remove undefined layers
		count = mxs.custAttributes.count(root)
		getLayerFromName = mxs.layerManager.getLayerFromName
		get_attr = mxs.custAttributes.get
		rem_attr = mxs.custAttributes.delete
		is_prop = mxs.isproperty

		for i in range(count - 1, -1, -1):
			attr = get_attr(root, i + 1)
			if (str(attr.name).lower() == 'oniondata'):
				layer = None

				# grab the layer by its name
				if (is_prop(attr, 'lnm') and attr.lnm):
					layer = getLayerFromName(attr.lnm)

				# remove the layer reference
				if layer:
					rem_attr(root, i + 1)

	def closeRenderSceneDialog(self):
		"""
			\remarks	implements the AbstractScene.closeRenderSceneDialog to close an open render scene dialog
			\sa			openRenderSceneDialog
			\return		<bool> success
		"""
		mxs.renderscenedialog.close()
		return True

	@classmethod
	def currentFileName(cls):
		"""
			\remarks	implements AbstractScene.currentFileName method to return the current filename for the scene that is active in the application
			\return		<str>
		"""
		return mxs.maxFilePath + mxs.maxFileName

	def deleteSceneState(self, stateName):
		"""
			\reamrks 	deletes a scene state based on the name given
			\param 		<str>	stateName
			\return 	<boo>	Success
		"""
		return mxs.cross3dHelper.deleteSceneState(stateName)

	def exportFile(self, file, using=None, prompt=False, selectedOnly=True):
		"""
			\remarks	implements AbstractScene.exportFile method to export objects from the scene to a file on disk
			\raises		ValueError
			\return		N/A
		"""
		kwargs = {'selectedOnly': selectedOnly}
		if using:
			kwargs['using'] = using
		if prompt:
			result = mxs.exportFile(file, **kwargs)
		else:
			result = mxs.exportFile(file, mxs.pyhelper.namify('noPrompt'), **kwargs)
		if not result:
			raise ValueError('Unable to export to given file path: {file}'.format(file=file))

	def fileName(self):
		"""
			\remarks	implements the AbstractScene.fileName to return the name of the current scene file.
			\sa			filePath
			\return		<str> file name
		"""
		return mxs.maxfilename

	def filePath(self):
		"""
			\remarks	implements the AbstractScene.filePath to return the directory path of the current scene file.
			\sa			fileName
			\return		<str> directory path
		"""
		return mxs.maxfilepath

	def holdCurrentState(self):
		"""
			\remarks	implements AbstractScene.holdCurrentState to protect the current scene as it is to allow for manipulation and provide a restore point
			\sa			restoreHeldState
		"""
		mxs.holdMaxFile()

	def fileType(self):
		"""
			\remarks	implements AbstractScene.fileType to return the main file type for this type of application
			\return		<str>
		"""
		return '.max'

	def fileTypes(self):
		"""
			\remarks	implements AbstractScene.fileTypes to return the associated file types for this type of application
			\return		<list> [ <str>, .. ]
		"""
		return ['Max files (*.max)']

	def getSceneState(self, shotName):
		"""
			\remarks	gets the scene state based on name
			\param 		<string> shotName
			\return		<string> name of scene state
		"""
		if shotName:
			index = mxs.cross3dhelper.findSceneState(shotName)
			if index > 0:
				return mxs.cross3dhelper.getSceneState(index)

		return False

	def isIsolated(self):
		r"""
			\remarks	Returns if the scene is isolated.
			\return		<bool>
		"""
		return mxs.Iso2lations == True

	def isSlaveMode(self):
		"""
			\remarks	[abstract] return whether or not the application is currently being run as a slave
			\return		<bool> state
		"""
		return mxs.getQuietMode()

	def keyInTangentType(self):
		"""
			\remarks	return the current in tangent type of the scene
			\return		<value_wrapper> name
		"""
		return mxs.BezierDefaultParams.inTangentType

	def keyOutTangentType(self):
		"""
			\remarks	return the current out tangent type of the scene
			\return		<value_wrapper> name
		"""
		return mxs.BezierDefaultParams.outTangentType

	def loadFile(self, filename='', confirm=True):
		"""
			\remarks	implements AbstractScene.loadFile to load the inputed filename into the application, returning true on success
			\param		filename	<str>
			\return		<bool> success
		"""
		if (not filename):
			from Qt.QtGui import QFileDialog
			filename = QFileDialog.getOpenFileName(None, 'Load Max File', '', 'Max files (*.max);;All files (*.*)')

		if (filename):
			mxs.loadMaxFile(str(filename), quiet=not confirm)
			return True
		return False

	def metaData(self):
		"""
			\remarks	initializes the SceneMetaData class for this scene instance for retrieving information from the scene
			\return		<SceneMetaData>
		"""
		if (not self._metaData):
			# cleanup existing data
			# self.cleanMetaData()

			data = SceneMetaData.find(mxs.globaltracks)
			if (data):
				# In the event that the version key isn't stored, there's no
				# reason to let that cause issues.  We'll just skip the version
				# check in that instance.  This should be exceedingly rare.
				try:
					version = round(data.value('version'), 2)
					# determine if we need to upgrade
					if (version < SceneMetaData.version):
						# update the data
						print 'update the data', data.value('version'), SceneMetaData.version
				except RuntimeError:
					pass
			else:
				# create the main data
				data = SceneMetaData.createUnique(mxs.globaltracks)

			self._metaData = data

		return self._metaData

	def mergeScene(self, path, **options):
		"""
			\remarks	merges a scene file with the current scene.
			\return		<bool> success
		"""
		objectNames = mxs.getMaxFileObjectNames(path, quiet=True)
		mxs.mergeMAXFile(path)
		objects = []
		for name in objectNames:
			obj = self.findObject(name)
			if obj:
				objects.append(obj)
		return objects

	def openRenderSceneDialog(self):
		"""
			\remarks	implements AbstractScene.openRenderSceneDialog to open a render scene dialog
			\sa			closeRenderSceneDialog
			\return		<bool> success
		"""
		mxs.renderscenedialog.open()
		return True

	def property(self, key, default=None):
		"""
			\remarks	implements AbstractScene.property to return a global scene value
			\param		key			<str> || <QString>
			\param		default		<variant>	default value to return if no value was found
			\return		<variant>
		"""
		value = getattr(mxs, str(key))
		if (not value):
			return default

		return self._fromNativeValue(value)

	def renameObjects(self, objects, names):
		"""
			\remarks	renames the given objects to the corresponding name in the names list
			\param		objects [<SceneObject>, ...], names [<str>, ...]
			\return		<bool> success
		"""
		mxs.blurUtil.setNames([o.nativePointer() for o in objects], names)

	def renderSavesFile(self):
		"""
			\remarks	implements AbstractScene.renderSavesFile to return whether renders are set to save frames to disk
			\sa			getRenderSavesFile
			\return		<bool>
		"""
		return mxs.rendsavefile

	def realizeTimeControllers(self, cachesFrameRate=None):

		# If the frame rate at which the PC and TMC caches have been made is not specified, we use the scene rate.
		cachesFrameRate = float(cachesFrameRate) if cachesFrameRate else self.animationFPS()

		# Handling XMeshes.
		xMeshes = mxs.getClassInstances(mxs.XMeshLoader)
		for xMesh in xMeshes:

			# Getting the FPS of that XMesh.
			fileName = xMesh.renderSequence
			if os.path.exists(fileName):

				# Getting the FPS at which the XMesh was generated.
				from blur3d.lib.xmeshhandler import XMESHHandler
				xMeshFrameRate = XMESHHandler(fileName).fps()

				# Setting up the playback curve.
				timeScriptController = mxs.Float_Script()
				timeScriptController.script = '{} / frameRate * F'.format(xMeshFrameRate)
				xMesh.enablePlaybackGraph = True
				mxs.setPropertyController(xMesh, "playbackGraphTime", timeScriptController)

		# Creating the and RayFireCaches, PCs, and TMCs instanciated controllers.

		# Handling PCs and TMCs.
		nativeCaches = mxs.getClassInstances(mxs.Point_Cache) + mxs.getClassInstances(mxs.Transform_Cache)
		for nativeCache in nativeCaches:

			# This optimizes the playback greatly.
			if mxs.classOf(nativeCache) == mxs.Point_Cache:
				nativeCache.sampleRate = self.animationFPS() / float(cachesFrameRate)

			# Some info like the first and last frame of the point cache must unfortunately come from parsing the file.
			fileName = nativeCache.filename if mxs.classOf(nativeCache) == mxs.Point_Cache else nativeCache.CacheFile
			if os.path.exists(fileName):

				# Parsing the cache file. We need to extract the start frame.
				if mxs.classof(nativeCache) == mxs.Point_Cache:
					from blur3d.lib.pclib import PointCacheInfo
					cacheInfo = PointCacheInfo.read(fileName, header_only=True)
				elif mxs.classof(nativeCache) == mxs.Transform_Cache:
					from blur3d.lib.tmclib import TMCInfo
					cacheInfo = TMCInfo.read(fileName, header_only=True)

				# Setting the playback to curve.
				timeScriptController = mxs.Float_Script()
				timeScriptController.script = '{} / frameRate * F - {}'.format(cachesFrameRate, cacheInfo.start_frame)
				nativeCache.playbackType = 3
				mxs.setPropertyController(nativeCache, "playbackFrame", timeScriptController)

		# Handling RayFire caches.
		rayFireCaches = mxs.getClassInstances(mxs.RF_Cache)

		# We can instance this.
		timeScriptController = mxs.Float_Script()
		timeScriptController.script = '{} / frameRate * F'.format(cachesFrameRate)

		for rayFireCache in rayFireCaches:

			# Setting the playback curve.
			rayFireCache.playUseGraph = True
			mxs.setPropertyController(rayFireCache, "playFrame", timeScriptController)

	def resetTimeControllers(self, include='', exclude=''):

		# Resetting Alembics to normal playback by instantiating the same expression.
		alembicControllers = mxs.getClassInstances(mxs.Alembic_Float_Controller)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Xform)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Mesh_Geometry)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Mesh_Normals)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Mesh_Topology)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Mesh_UVW)

		# Looping through controllers.
		for alembicController in alembicControllers:

			# Figuring if the name of the object depending on that modifier meets the exclude and include criterias.
			dependents = mxs.refs.dependents(alembicController)
			for dependent in dependents:
				if mxs.isProperty(dependent, 'name'):
					name = dependent.name

					# TODO: That check is a little lite.
					if re.findall(include, name) and not (re.findall(exclude, name) and exclude):
						scriptController = mxs.Float_Script()
						scriptController.script = 'S'
						mxs.setPropertyController(alembicController, 'time', scriptController)

		# Resetting PCs and TMCs to default playback.
		nativeCaches = mxs.getClassInstances(mxs.Point_Cache) + mxs.getClassInstances(mxs.Transform_Cache)
		for nativeCache in nativeCaches:

			# Figuring if the name of the object depending on that modifier meets the exclude and include criterias.
			dependents = mxs.refs.dependents(nativeCache)
			for dependent in dependents:
				if mxs.isProperty(dependent, 'name'):
					name = dependent.name

					# TODO: That check is a little lite.
					if re.findall(include, name) and not (re.findall(exclude, name) and exclude) and mxs.classOf(self._findNativeObject(name)) != mxs.FumeFX:
						if mxs.classOf(nativeCache) == mxs.Point_Cache:
							nativeCache.sampleRate = 1.0
						nativeCache.playbackType = 0
						mxs.setPropertyController(nativeCache, "playbackFrame", mxs.bezier_float())

		# Resetting XMeshes to default playback.
		xMeshes = mxs.getClassInstances(mxs.XMeshLoader)
		for xMesh in xMeshes:

			# Figuring if the name of the object depending on that modifier meets the exclude and include criterias.
			dependents = mxs.refs.dependents(xMesh)

			for dependent in dependents:
				if mxs.isProperty(dependent, 'name'):
					name = dependent.name

					# TODO: That check is a little lite.
					if re.findall(include, name) and not (re.findall(exclude, name) and exclude):
						xMesh.enablePlaybackGraph = False
						mxs.setPropertyController(xMesh, "playbackGraphTime", mxs.bezier_float())

		# Resetting XMeshes to default playback.
		rayFireCaches = mxs.getClassInstances(mxs.RF_Cache)
		for rayFireCache in rayFireCaches:

			# Figuring if the name of the object depending on that modifier meets the exclude and include criterias.
			dependents = mxs.refs.dependents(rayFireCache)
			for dependent in dependents:
				if mxs.isProperty(dependent, 'name'):
					name = dependent.name

					# TODO: That check is a little lite.
					if re.findall(include, name) and not (re.findall(exclude, name) and exclude):
						rayFireCache.playUseGraph = False
						mxs.setPropertyController(rayFireCache, "playFrame", mxs.bezier_float())

		# Resetting Fumes.
		fumes = mxs.getClassInstances(mxs.FumeFX)
		for fume in fumes:

			# Figuring if the name of the object depending on that modifier meets the exclude and include criterias.
			dependents = mxs.refs.dependents(fume)
			for dependent in dependents:
				if mxs.isProperty(dependent, 'name'):
					name = dependent.name

					# TODO: That check is a little lite.
					if re.findall(include, name) and not (re.findall(exclude, name) and exclude):
						mxs.setPropertyController(fume, 'TimeValue', mxs.bezier_float())
						mxs.setPropertyController(fume, 'TimeScaleFactor', mxs.bezier_float())
						fume.TimeScaleFactor = 1.0
						mxs.setPropertyController(fume, 'timescale', mxs.bezier_float())
						fume.timescale = 1.0

		return True

	def restoreSceneState(self, stateName, parts):
		return mxs.cross3dHelper.restoreSceneState(stateName, parts)

	def saveSceneState(self, stateName, parts):
		return mxs.cross3dhelper.captureSceneState(stateName, parts)

	def _applyNativeTimeController(self, nativeController, cachesFrameRate=None, include='', exclude='', bake=False, rnd=0.0):

 		# If the frame rate at which the PC and TMC caches have been made is not specified, we use the scene rate.
		cachesFrameRate = float(cachesFrameRate) if cachesFrameRate else self.animationFPS()

		# Loading time on alembics by instantiating a single controller.
		alembicControllers = mxs.getClassInstances(mxs.Alembic_Float_Controller)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Xform)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Mesh_Geometry)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Mesh_Normals)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Mesh_Topology)
		alembicControllers += mxs.getClassInstances(mxs.Alembic_Mesh_UVW)

		for alembicController in alembicControllers:

			# Figuring if the name of the object depending on that modifier meets the exclude and include criterias.
			dependents = mxs.refs.dependents(alembicController)
			for dependent in dependents:
				if mxs.isProperty(dependent, 'name'):
					name = dependent.name

					# TODO: That check is a little lite.
					if re.findall(include, name) and not (re.findall(exclude, name) and exclude):
						mxs.setPropertyController(alembicController, 'Time', nativeController)

		# Since the TMC and PC time controllers will take the form of a script that references the provided time controller.
		# We need to make sure the provided controller is not "floating" otherwise we use a pointer the one we have instanciated on alembics.
		if not mxs.refs.dependents(nativeController):
			nativeController = mxs.getPropertyController(alembicController, "Time")

		# In the case where there is no alembic controller around, we cannot reference a "floating" controller and therefore have to bake.
		if not mxs.refs.dependents(nativeController):
			bake = True

		# Getting the range of the native controller in case we need to bake.
		if bake:
			from cross3d import SceneAnimationController
			controller = SceneAnimationController(self, nativeController)

			# The FCurve range is not made from floats.
			bakeRange = FrameRange(controller.fCurve().range())
			if not bakeRange:
				bake = False

		# Add target takes a lot of time, so we are prepping this controller on the forehand.
		timeScriptControllerBase = mxs.Float_Script()
		timeScriptControllerBase.addtarget('Time', nativeController)

		# TODO: Stop supporting PCs and TMCs, they suck, we need to move on.
		nativeCaches = mxs.getClassInstances(mxs.Point_Cache) + mxs.getClassInstances(mxs.Transform_Cache)
		for nativeCache in nativeCaches:

			# Figuring if the name of the object depending on that modifier meets the exclude and include criterias.
			dependents = mxs.refs.dependents(nativeCache)
			for dependent in dependents:
				if mxs.isProperty(dependent, 'name'):
					name = dependent.name

					# TODO: That check is a little lite.
					if re.findall(include, name) and not (re.findall(exclude, name) and exclude) and mxs.classOf(self._findNativeObject(name)) != mxs.FumeFX:

						# This optimized greatly the playback.
						if mxs.classOf(nativeCache) == mxs.Point_Cache:
							nativeCache.sampleRate = self.animationFPS() / float(cachesFrameRate)

						# Some info like the first and last frame of the point cache must unfortunately come from parsing the file.
						fileName = nativeCache.filename if mxs.classOf(nativeCache) == mxs.Point_Cache else nativeCache.CacheFile
						if os.path.exists(fileName):

							# Parsing the cache file. We need to extract the start frame.
							if mxs.classof(nativeCache) == mxs.Point_Cache:
								from blur3d.lib.pclib import PointCacheInfo
								cacheInfo = PointCacheInfo.read(fileName, header_only=True)
							elif mxs.classof(nativeCache) == mxs.Transform_Cache:
								from blur3d.lib.tmclib import TMCInfo
								cacheInfo = TMCInfo.read(fileName, header_only=True)

							# Setting up the start frame.
							# nativeCache.recordStart = cacheInfo.start_frame

							# Setting the playback to curve.
							nativeCache.playbackType = 3

							# Creating the time script controller.
							timeScriptController = mxs.copy(timeScriptControllerBase)
							timeScriptController.script = 'Time * %f - %i' % (cachesFrameRate, cacheInfo.start_frame)

							# Baking the controller requested.
							if bake:
								from cross3d import SceneAnimationController
								wrappedController = SceneAnimationController(self, timeScriptController)
								wrappedController.bake(rng=bakeRange, extrapolation=ExtrapolationType.Linear)
								timeScriptController = wrappedController.nativePointer()

							# Setting the playback controller.
							mxs.setPropertyController(nativeCache, "playbackFrame", timeScriptController)

		# Handling XMesh caches.
		xMeshes = mxs.getClassInstances(mxs.XMeshLoader)
		for xMesh in xMeshes:

			# Getting the FPS of that XMesh.
			fileName = xMesh.renderSequence
			if os.path.exists(fileName):

				# Getting the FPS at which the XMesh was generated.
				from blur3d.lib.xmeshhandler import XMESHHandler
				xMeshFrameRate = XMESHHandler(fileName).fps()

				# Creating the XMesh and RayFire and Fume instanciated time script controller.
				timeScriptController = mxs.copy(timeScriptControllerBase)
				timeScriptController.script = 'Time * %f' % xMeshFrameRate

				# Baking the controller requested.
				if bake:
					from cross3d import SceneAnimationController
					wrappedController = SceneAnimationController(self, timeScriptController)
					wrappedController.bake(rng=bakeRange, extrapolation=ExtrapolationType.Linear)
					timeScriptController = wrappedController.nativePointer()

				# Figuring if the name of the object depending on that modifier meets the exclude and include criterias.
				dependents = mxs.refs.dependents(xMesh)

				for dependent in dependents:
					if mxs.isProperty(dependent, 'name'):
						name = dependent.name

						# TODO: That check is a little lite.
						if re.findall(include, name) and not (re.findall(exclude, name) and exclude):

							# Setting the playback to curve.
							xMesh.enablePlaybackGraph = True

							# Setting the playback controller.
							mxs.setPropertyController(xMesh, "playbackGraphTime", timeScriptController)

		# Handling the other cache formats.
		rayFireCaches = mxs.getClassInstances(mxs.RF_Cache)
		fumes = mxs.getClassInstances(mxs.FumeFX)
		thinkings = mxs.getClassInstances(mxs.Thinking)
		if rayFireCaches or fumes or thinkings:

			# Creating the and RayFire, Fume and Thinking instanciated time script controller.
			# TODO: The frame rate should be detected for each individual cache.
			timeScriptController = mxs.copy(timeScriptControllerBase)
			timeScriptController.script = 'Time * frameRate'

			# Baking the controller requested.
			if bake:
				from cross3d import SceneAnimationController
				wrappedController = SceneAnimationController(self, timeScriptController)
				wrappedController.bake(rng=bakeRange, extrapolation=ExtrapolationType.Linear)
				timeScriptController = wrappedController.nativePointer()

			# Handling RayFire caches.
			for rayFireCache in rayFireCaches:

				# Figuring if the name of the object depending on that modifier meets the exclude and include criterias.
				dependents = mxs.refs.dependents(rayFireCache)
				for dependent in dependents:
					if mxs.isProperty(dependent, 'name'):
						name = dependent.name

						# TODO: That check is a little lite.
						if re.findall(include, name) and not (re.findall(exclude, name) and exclude):

							# Setting the playback to curve.
							rayFireCache.playUseGraph = True

							# Setting the playback controller.
							mxs.setPropertyController(rayFireCache, "playFrame", timeScriptController)

			# We are only creating a speed curve if fumes or thinking are present.
			if fumes or thinkings:

				# Creating speed controller for Fume caches.
				from cross3d import SceneAnimationController
				wrappedController = SceneAnimationController(self, nativeController)
				speedScriptController = wrappedController.derivatedController()

				# Baking the controller requested.
				if bake:
					speedScriptController.bake(rng=bakeRange, extrapolation=ExtrapolationType.Linear)

				# Getting the native speed controller.
				speedScriptController = speedScriptController.nativePointer()

				# Handling fumes.
				for fume in fumes:

					# Figuring if the name of the object depending on that modifier meets the exclude and include criterias.
					dependents = mxs.refs.dependents(fume)
					for dependent in dependents:
						if mxs.isProperty(dependent, 'name'):
							name = dependent.name

							# TODO: That check is a little lite.
							if re.findall(include, name) and not (re.findall(exclude, name) and exclude):

								# Setting the playback controller.
								mxs.setPropertyController(fume, "TimeValue", timeScriptController)

								# We are now generating a script that computes the derivative of the time curve for the speed curve.
								mxs.setPropertyController(fume, "TimeScaleFactor", speedScriptController)

				# Handling Thinking Particles objects.
				for thinking in thinkings:

					# For thinking we do not care for include and exclude since the user can simply unsubscribe by not using the pre-defined properties.
					self._setThinkingPropertyController(thinking, "TimeCurve", timeScriptController)
					self._setThinkingPropertyController(thinking, "SpeedCurve", speedScriptController)

		mxs.redrawViews()
		return True

	def _setThinkingPropertyController(self, thinking, prop, controller):
		def setControllerRecursively(operator, prop, controller):
			if operator:
				if mxs.hasProperty(operator, 'Value') and operator.getName() == prop:
					mxs.setPropertyController(operator, mxs.pyHelper.namify('Value'), controller)
				elif mxs.hasProperty(operator, 'Operators'):
					for op in operator.Operators:
						setControllerRecursively(op, prop, controller)

		# Running the local recursive function on all dynamic sets.
		for dynamicSet in thinking.MasterDynamic.DynamicSets:
			setControllerRecursively(dynamicSet, prop, controller)
		return True

	def rendererType(self):
		nativeRenderer = mxs.renderers.current
		if mxs.classOf(nativeRenderer) == mxs.Default_Scanline_Renderer:
			return RendererType.Scanline
		elif mxs.classOf(nativeRenderer) == mxs.Quicksilver_Hardware_Renderer:
			return RendererType.Quicksilver
		elif mxs.classOf(nativeRenderer) == mxs.V_Ray_Adv_3_25_01:
			return RendererType.VRay
		elif mxs.classOf(nativeRenderer) == mxs.mental_ray_renderer:
			return RendererType.MentalRay
		return 0

	def renderSize(self):
		"""
			\remarks	implements AbstractScene.renderSize method to return the current output width and height for renders
			\return		<QSize>
		"""
		from Qt.QtCore import QSize
		return QSize(mxs.renderWidth, mxs.renderHeight)

	def reset(self, silent=False):
		"""
			\remarks	implements AbstractScene.reset to reset this scene for all the data and in the application
			\return		<bool> success
		"""
		if silent:
			mxs.resetMaxFile(mxs.pyhelper.namify('noPrompt'))
		else:
			mxs.resetMaxFile()
		return True

	def restoreHeldState(self):
		"""
			\remarks	implements AbstractScene.restoreHeldState to restore a held state after processing code
			\sa			holdCurrentState
			\return		<bool> success
		"""
		mxs.fetchMaxFile()

		# flush the maxscript memory that was used during the hold state
		mxs.gc()  # first time marks items ready for removal
		mxs.gc()  # second time removes items that are ready for removal

		return True

	def select(self):
		"""
			\remarks	implements AbstractScene.select to launch Max's "selectByName" dialog and then select the user's choice.
			\return		<list> objects
		"""
		selection = mxs.selectByName()
		mxs.select(selection)
		application.refresh()
		return self.selection()

	def saveFileAs(self, filename=''):
		"""
			\remarks	implements AbstractScene.saveFileAs to save the current scene to the inputed name specified.  If no name is supplied, then the user should be prompted to pick a filename
			\param		filename 	<str>
			\return		<bool> success
		"""
		if (not filename):
			from Qt.QtGui import QFileDialog
			filename = QFileDialog.getSaveFileName(None, 'Save Max File', '', 'Max files (*.max);;All files (*.*)')

		if (filename):
			mxs.saveMaxFile(str(filename))
			return True
		return False

	def saveSelected(self, path, **options):
		"""
			\remarks implements the saveSelected feature in 3dsMax
		"""
		selectedNodes = self._nativeSelection()
		mxs.saveNodes(selectedNodes, path)
		return True

	def saveCopy(self, path):
		"""
			\remarks	implements AbstractScene.saveCopy to save a copy of the current scene
			\param		filename 	<str>
			\return		<bool> success
		"""
		mxs.saveMaxFile(path, useNewFile=False)
		return True

	def setAnimationFPS(self, fps, changeType=constants.FPSChangeType.Seconds, callback=None):
		""" Updates the scene's fps to the provided value and scales existing keys as specified.
		
		If you have any code that you need to run after changing the FPS and plan to use it in 
		Max you will need to pass that code into the callback argument.

		Although any float can be provided the only supported FPS supported by Max are:
		1,2,3,4,5,6,8,10,12,15,16,20,24,25,30,32,40,48,50,60,64,75,80,96,100,120,150,160,192,200,240,300,300,320,400,480,600,800,1200,1600,2400,4800

		This can be expressed in Python using "sorted([2**a * 3**b * 5**c for a in range(7) for b in range(2) for c in range(3)])".
		Thank you Tyler Fox.

		Args:
			fps(float): The FPS value to set.
		    changeType(enum): <constants.FPSChangeType> Defaults to constants.FPSChangeType.Frames
		:param callback: <funciton> Code called after the fps is changed.

		Returns:
			(bool): Wheter the FPS was set.
		"""

		# No need to change it if the frameRate is already correct
		if mxs.frameRate != fps:
			if changeType == constants.FPSChangeType.Frames:
				from cross3d.studiomax.rescaletime import RescaleTime
				from cross3d import FrameRange
				# If we dont save it as a class variable it will go out of scope and all of the
				# QTimers will not be called.
				self._rescaleTime = RescaleTime()

				def finishFrameRate(checkRate):
					# If the current frame range doesn't match the value we passed into RescaleTime
					# a error has occurred and we dont want to change the fps
					errorCheck = checkRate == self.animationRange().end()
					if errorCheck:
						mxs.frameRate = round(fps)
					self.setAnimationRange(animRange)
					self.setCurrentFrame(currFrame)
#					if not errorCheck:
#						from cross3d import Exceptions
#						raise Exceptions.FPSChangeFailed('Changing the FPS appears to have failed. Your FPS has not been changed.')
					if callback:
						callback()
				# because RescaleTime.scaleTime requires the use of QTimers we need to listen for the signal
				# before finishing the conversion
				self._rescaleTime.scaleTimeFinished.connect(finishFrameRate)
				animRange = self.animationRange()
				currFrame = self.currentFrame()
				self.setAnimationRange(FrameRange((0, 1000000)))
				self._rescaleTime.scaleTime(round(1000000 * mxs.frameRate / float(fps)))
			else:
				mxs.frameRate = round(fps)
				if callback:
					callback()
			return True
		if callback:
			callback()
		return False

	def setAnimationRange(self, animationRange, globalRange=None):
		"""
			\remarks	implements AbstractScene.setAnimationRange method to set the current start and end frame for animation
			\param		animationRange	<tuple> ( <int> start, <int> end )
			\return		<bool> success
		"""
		start, end = animationRange
		mxs.animationRange = mxs.interval(start, end)
		return True

	def setKeyInTangentType(self, tangentType):
		"""
			\remarks	implements AbstractScene.setKeyInTangentType method to set the in tangent type for the scene
			\param		tangentType <str|name>
			\raises		ValueError
			\return		N/A
		"""
		# Make sure we have a name.  This should allow anything that stringifies
		# properly to be given, as well.
		tangentType = mxs.pyhelper.namify(str(tangentType))
		if not mxs.BezierDefaultParams.setProperty('inTangentType', tangentType):
			raise ValueError('Given tangent type is invalid: {tt}'.format(tt=str(tangentType)))

	def setKeyOutTangentType(self, tangentType):
		"""
			\remarks	implements AbstractScene.setKeyOutTangentType method to set the out tangent type for the scene
			\param		tangentType <str|name>
			\raises		ValueError
			\return		N/A
		"""
		tangentType = mxs.pyhelper.namify(str(tangentType))
		if not mxs.BezierDefaultParams.setProperty('outTangentType', tangentType):
			raise ValueError('Given tangent type is invalid: {tt}'.format(tt=str(tangentType)))

	def setRenderOutputPath(self, outputPath):
		"""
			\remarks	set the render output path for the scene
			\param		outputPath	<str>
			\return		<bool> success
		"""
		mxs.rendOutputFilename = outputPath
		return True

	def setRenderSavesFile(self, state):
		"""
			\remarks	implements AbstractScene.setRenderSavesFile to tell renders to save frames to disk
			\sa			renderSavesFile
			\param		state	<bool>
			\return		<bool> success
		"""
		mxs.rendsavefile = state
		return True

	def setRenderSize(self, size):
		"""
			\remarks	implements AbstractScene.setRenderSize method to set the current output width and height for renders for this scene
			\param		size	<QSize>
			\return		<bool> success
		"""
		mxs.renderWidth = size.width()
		mxs.renderHeight = size.height()
		if mxs.renderSceneDialog.isOpen():
			mxs.renderSceneDialog.update()

	def faceFromMouseClick(self):
		"""Summary
			finds the geometry and face clicked by the user in the viewport
		Returns:
		    TYPE: <tuple> Collision Object and Face Index of Collision
		"""
		p = mxs.pickPoint(snap=mxs.pyhelper.namify('3D'))
		if p == None or p == mxs.pyhelper.namify('rightClick'): #user right clicked
		    return False

		ray = mxs.mapScreenToWorldRay(mxs.mouse.pos)

		if not ray:
			return False

		sampledObjects = []
		for obj in self.objects():
			if not obj.isHidden() and mxs.superclassOf(obj) == mxs.GeometryClass and mxs.classOf(obj) != mxs.Biped_Object:
				sampledObjects.append(obj)

		shortestDistance = -1
		hitObjects = []
		for obj in sampledObjects:
		    result = mxs.intersectRayEx(obj, ray)
		    if result:
		        faceIndex = result[1]
		        faceCenter = mxs.meshop.getFaceCenter(obj, faceIndex)
		        camPos = ray.pos
		        distance = math.sqrt((camPos.x - faceCenter.x)**2 + (camPos.y - faceCenter.y)**2 + (camPos.z - faceCenter.z)**2)
		        if shortestDistance < 0 or shortestDistance > distance:
		            hitObjects.append([obj, faceIndex])
		            shortestDistance = distance

		if hitObjects:
			return hitObjects.pop()

		return False
	def setRenderFrameRange(self, frameRange):
		"""
			\remarks	set the render frame range of the scene
			\param		size	<cross3d.FrameRange>
			\return		<bool> success
		"""
		# not the ideal way to deal with all the options but I am in the rush
		mxs.rendTimeType = 3
		mxs.rendStart = frameRange[0]
		mxs.rendEnd = frameRange[1]
		return True

	def setRenderPixelAspect(self, pixelAspect):
		"""
			\remarks	set the render pixel aspect of the scene
			\param		pixelAspect	<int>
			\return		<bool> success
		"""
		mxs.renderPixelAspect = pixelAspect
		return True

	def setSilentMode(self, switch):
		mxs.setSilentMode(switch)

	def silentMode(self):
		return mxs.silentMode()

	def renderPixelAspect(self,):
		"""
			\remarks	returns the render pixel aspect of the scene
			\return		<int> pixelAspect
		"""
		return mxs.renderPixelAspect

	def renderOutputPath(self):
		"""
			\remarks	return the render output file path for the scene
			\return		<str>
		"""
		return mxs.rendOutputFilename

	def setRenderMissingFramesOnly(self, renderMissingFramesOnly):
		"""
			\remarks	sets if the renderer is rendering missing frames only.
			\param		renderMissingFramesOnly	<bool>
			\return		<bool> success
		"""
		mxs.skipRenderedFrames = renderMissingFramesOnly
		return True

	def renderMissingFramesOnly(self):
		"""
			\remarks	gets if the renderer is rendering missing frames only.
			\return		<bool> renderMissingFramesOnly
		"""
		return mxs.skipRenderedFrames

	def setLayerGroups(self, layerGroups):
		"""
			\remarks	reimplements the AbstractScene.setLayerGroups method to set the scene layer groups to the inputed list
			\param		layerGroups		<list> [ <cross3d.SceneLayerGroup> layerGroup, .. ]
			\return		<bool> success
		"""
		groupNames = []
		groupStates = []

		for layerGroup in layerGroups:
			groupNames.append(str(layerGroup.groupName()))
			groupStates.append(layerGroup.isOpen())

		data = self.metaData()
		data.setValue('layerGroupNames', groupNames)
		data.setValue('layerGroupStates', groupStates)

		return True

	def setProperty(self, key, value):
		"""
			\remarks	implements AbstractScene.setProperty to set the global scene property to the inputed value
			\param		key			<str> || <QString>
			\param		value		<variant>
			\return		<bool>
		"""
		return setattr(mxs, str(key), self._toNativeValue(value))

	def setRotation(self, objects, axes, relative=False):
		"""
		Rotates the provided objects in the scene
		:param objects: Rotate these objects
		:param axes: A list with a length of 3 floats representing x, y, z
		:param relative: Apply the rotation as relative or absolute. Absolute by default.
		"""
		# Compensate for the axes order
		axes = (axes[2], axes[0], axes[1])
		if relative:
			mxs.rotate([obj.nativePointer() for obj in objects], mxs.eulerangles(*axes))
		else:
			# Max makes this difficult
			for obj in objects:
				nobj = obj.nativePointer()
				oldPos = nobj.pos
				oldScale = nobj.scale
				nobj.transform = mxs.matrix3(1)
				nobj.rotation = mxs.eulerangles(*axes)
				nobj.scale = oldScale
				nobj.pos = oldPos
		return True

	def setTimeControlPlay(self, switch, fromStart=False):
		if switch:
			if fromStart:
				mxs.sliderTime = mxs.animationRange.start
				mxs.playAnimation()
			else:
				mxs.playAnimation()
		else:
			mxs.stopAnimation()
		return True

	def setTimeControlLoop(self, isLooping):
		"""
			\remarks	sets whether the timeline is looping or not.
			\param		isLooping <bool>
			\return		<bool>
		"""
		mxs.timeConfiguration.playbackLoop = isLooping
		return True

	def isTimeControlLoop(self):
		"""
			\remarks	gets whether the timeline is looping or not.
			\return		<bool>
		"""
		return mxs.timeConfiguration.playbackLoop

	@classmethod
	def animationFPS(cls):
		"""
			\remarks	gets the current scene's fps.
			\return		<float>
		"""
		return float(mxs.frameRate)

	def currentFrame(self):
		"""
			\remarks	gets the current scene's frame.
			\return		<float>
		"""
		return int(mxs.currentTime)

	def setCurrentFrame(self, frame):
		"""
			\remarks	sets the current scene's frame.
			\param 		frame <int>
			\return		<float>
		"""
		mxs.sliderTime = frame
		return True

	def clearSelection(self):
		"""
			\remarks	clears the scene's selection.
			\return		<bool>
		"""
		mxs.clearSelection()
		return True

	def undo(self):
		"""
			\remarks	undos the last action.
			\return		<bool>
		"""
		mxs.execute('max undo')
		return True

	def userProps(self):
		"""Returns the FileProps object associated with this file
		:return; :class:`cross3d.FileProps`
		"""
		from cross3d import FileProps
		return FileProps()

	def animationMixers(self):
		"""Finds all mixers present in the current MAX scene.

		Returns:
					list: A list of Mixer instances for each MxMixer in the
						current MAX Scene.
		"""
		# Since Mixer is a Class in MAXScript, and not a MAXClass, we're not
		# able to use getClassInstances to retrieve Mixers in the scene.
		# Instead, we'll iterate over objects in the scene, and test to see if
		# they have a controller with a Mixer attached.
		from cross3d import Mixer
		mixers = []
		for obj in mxs.objects:
			if hasattr(obj, 'controller') and hasattr(obj.controller, 'mixer'):
				mixers.append(Mixer(obj.controller.mixer))
		return mixers

# register the symbol
cross3d.registerSymbol('Scene', StudiomaxScene)
