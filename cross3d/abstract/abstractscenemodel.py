##
#	\namespace	blur3d.api.abstract.abstractscenemodel
#
#	\remarks	The AbstractSceneModel class provides the base foundation for the 3d Object framework for the blur3d system
#				This class will provide a generic overview structure for all manipulations of 3d models
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/05/10
#

from blur3d import abstractmethod
from blur3d.api import SceneObject
from blur3d.constants import ObjectType

#------------------------------------------------------------------------------------------------------------------------

class AbstractSceneModel( SceneObject ):
	_objectType = ObjectType.Model

	#--------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#--------------------------------------------------------------------------------------------------------------------
		
	def objects( self, wildcard = '', type = '' ):
		return self.children( recursive = True, wildcard = wildcard, type = type )
	
#------------------------------------------------------------------------------------------------------------------------

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneModel', AbstractSceneModel, ifNotFound = True )