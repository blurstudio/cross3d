##
#	\namespace	blur3d.api.abstract.abstractscenestats
#
#	\remarks	The AbstractSceneStats class provides an interface to collecting stats on a scene instance
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blur3d		import abstractmethod
from blur3d.api import SceneWrapper

class AbstractSceneStats( SceneWrapper ):
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def summary( self ):
		"""
			\remarks	return a stat summary for the scene
			\return		<str>
		"""
		return ''
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneStats', AbstractSceneStats, ifNotFound = True )
