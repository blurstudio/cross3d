##
#	\namespace	blur3d.api.abstract.studiomaxapplication
#
#	\remarks	The StudiomaxApplication class will define all operations for application interaction. It is a singleton class, so calling blur3d.api.Application() will
#				always return the same instance of Application. One of its main functions is connecting application callbacks to blur3d.api.Dispatch.
#				
#				The StudiomaxApplication is a QObject instance and any changes to the scene data can be controlled by connecting to the signals defined here.
#
#				When subclassing the AbstractScene, methods tagged as @abstractmethod will be required to be overwritten.  Methods tagged with [virtual]
#				are flagged such that additional operations could be required based on the needs of the method.  All @abstractmethod methods MUST be implemented
#				in a subclass.
#	
#	\author		Mikeh@blur.com
#	\author		Blur Studio
#	\date		06/07/11
#

from blur3d.api.abstract.abstractapplication import AbstractApplication
#from blur3d.api.dispatch import Dispatch
from PySoftimage import xsi
import os
dispatch = None

class SoftimageApplication(AbstractApplication):
	def connect(self):
		"""
			\remarks	connect application specific callbacks to <blur3d.api.Dispatch>, dispatch will convert the native object to a blur3d.api object
						and emit a signal.
						connect is called when the first <blur3d.api.Dispatch> signal is connected.
			\return		<bool>	was the connection successfull
		"""
		global dispatch
		import blur3d.api
		dispatch = blur3d.api.dispatch
		if super(SoftimageApplication, self).connect():
			if xsi.LoadPlugin(os.path.abspath(__file__ + '/../blur3dplugin.py')):
				return True
		return False
	
	def connectCallback(self, signal):
		""" Override to prevent a warning in high debug. If a plugin can be designed to handle dynamicly connecting and disconnecting callbacks this is not useable """
		return
	
	def disconnect(self):
		"""
			\remarks	disconnect application specific callbacks to <blur3d.api.Dispatch>. This will be called when <blur3d.api.Dispatch> is deleted,
						disconnect is called when the last <blur3d.api.Dispatch> signal is disconnected.
		"""
		xsi.UnloadPlugin(os.path.abspath(__file__ + '/../blur3dplugin.py'))
	
	def disconnectCallback(self, signal):
		""" Override to prevent a warning in high debug. If a plugin can be designed to handle dynamicly connecting and disconnecting callbacks this is not useable """
		return
	
	def preDeleteObject(self, *args):
		"""
			\remarks	XSI does not emit pre and post signals, so just emit the delete signal
		"""
		if args:
			dispatch.objectDeleted.emit(args[0])
			
	def version( self ):
		"""
			\remarks	Returns the version major of XSI.
		"""
		version = xsi.Version()
		return int( version.split( '.' )[0] )
		
	def name( self ):
		return "Softimage"
		
	def nameAndVersion( self ):
		"""
			\remarks	returns the name and version format needed for Assburner added by John Kosnik
			\return		<str> unique name
		"""
		version =xsi.version()
		versionDic = {
		"10.1.46.0" : "XSI2012",
		"8.0.249.0" : "XSI2010",
		"11.0.525.0" : "XSI2013",
		'default' : "XSI2013"}
		
		if versionDic.has_key(version):
			jobType = versionDic[str(version)]
		else:
			jobType = versionDic['default']
		#print("debug =" + jobType)
		return jobType
		
	def refresh( self ):
		xsi.SceneRefresh()
		xsi.Refresh()
		return True
	
	def log( self, message ):
		xsi.LogMessage( message )
		
# register the symbol
from blur3d import api
api.registerSymbol( 'Application', SoftimageApplication)