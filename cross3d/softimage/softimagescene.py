##
#	\namespace	blur3d.classes.softimage.softimagescene
#
#	\remarks	The scene class implementation for a Softimage scene
#	
#	\author		beta@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from PySoftimage 								import xsi
from blur3d.classes.abstract.abstractscene		import AbstractScene

class SoftimageScene( AbstractScene ):
	def nativeRoot( self ):
		return xsi.ActiveSceneRoot
	
	def nativeObjects( self ):
		"""
			\remarks	[virtual] returns all the objects in the scene to the user
			\return		<list> [ <blur3d.objects.SceneObject>, .. ]
		"""
		return xsi.ActiveSceneRoot.FindChildren()
		
	def currentFileName( self ):
		return str( xsi.ActiveProject.ActiveScene.Filename.Value )
	
	def fileTypes( self ):
		return [ 'Softimage files (*.scn)' ]
	
	def loadFile( self, filename ):
		xsi.OpenScene( str( filename ), True )
	
	def saveFile( self ):
		xsi.SaveScene()
	
	def saveFileAs( self, filename ):
		xsi.SaveSceneAs( str( filename ) )
	
	def setSelection( self, nodes ):
		nativeObjsNames = [ node.nativeObject().FullName for node in nodes ]
		xsi.Selection.SetAsText( ",".join(nativeObjsNames) )
		return True
	
	def softwareId( self ):
		import PySoftimage
		
		# output the software id
		import win32com.client
		utils = win32com.client.Dispatch( 'XSI.Utils' )
		output = '%s_x32'
		
		if ( utils.Is64BitOS() ):
			output = '%s_x64'
			
		return output % str(PySoftimage.version())