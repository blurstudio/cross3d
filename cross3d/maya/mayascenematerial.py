##
#	\namespace	blur3d.api.maya.mayascenematerial
#
#	\remarks	The Maya implementation of SceneMaterial.
#	
#	\author		jbee@blur.com
#	\author		Blur Studio
#	\date		01/2015
#

import re
import os.path
import contextlib
import maya.cmds as cmds
from blur3d.api.abstract.abstractscenematerial import AbstractSceneMaterial
from blur3d.constants import MaterialPropertyMap

# =============================================================================
# CLASSES
# =============================================================================

class MayaSceneMaterial(AbstractSceneMaterial):
	def _nativeObjects(self):
		"""The native objects using this material."""
		@contextlib.contextmanager
		def restoreSelection(scn):
			objects = scn.selection()
			yield
			scn.setSelection(objects)
		boundObjects = []
		with restoreSelection(self._scene):
			# Hypershade can be used to select the objects that are
			# using the given shader.  This can then be grabbed as
			# native objects by selection, after which we return the
			# selection to what the user previously had.
			cmds.hyperShade(objects=self.name()) or []
			boundObjects.extend(self._scene._nativeObjects(True))
		return boundObjects

	def __iter__(self):
		mapSets = dict()
		cons = cmds.listConnections(
			self.name() + '.surfaceShader',
		) or []
		for con in cons:
			maps = cmds.listConnections(
				con,
				plugs=True,
				type='file',
			) or []
			for mapSpec in maps:
				(name, plug) = re.split(r'[.]', mapSpec)
				mapPath = os.path.normpath(cmds.getAttr(name + '.fileTextureName'))
				if mapPath and MaterialPropertyMap.hasKey(plug):
					mapSets[MaterialPropertyMap.valueByLabel(plug)] = mapPath
				else:
					mapSets[plug] = mapPath
		yield ('name', self.name())
		yield ('maps', mapSets)
		yield ('objects', [o.name() for o in self.objects()])
	
from blur3d import api
api.registerSymbol('SceneMaterial', MayaSceneMaterial)

