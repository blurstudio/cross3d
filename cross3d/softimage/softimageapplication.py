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

import os

from blur3d.api.abstract.abstractapplication import AbstractApplication
from PySoftimage import xsi, constants
from blur3d import api

dispatch = None

class SoftimageApplication(AbstractApplication):
	# Only process these functions when we actually care about them. This is required because xsi doesnt generate individual signals for objects
	# it generates a single event and requires the scripter to figure out if they need to do anything with the event.
	objectCallbacks = set(['objectRenamed', 'objectUnHide', 'objectHide', 'objectUnfreeze', 'objectFreeze', 'objectParented'])
	_objectsConnectedCount = 0
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
		""" Only process valueChanged signals if we actually care about one of its many signals. """
		if signal in self.objectCallbacks:
			if self._objectsConnectedCount == 0:
				xsi.Blur3d_enableValueChanged(True)
			self._objectsConnectedCount += 1
		return
	
	def disconnect(self):
		"""
			\remarks	disconnect application specific callbacks to <blur3d.api.Dispatch>. This will be called when <blur3d.api.Dispatch> is deleted,
						disconnect is called when the last <blur3d.api.Dispatch> signal is disconnected.
		"""
		xsi.UnloadPlugin(os.path.abspath(__file__ + '/../blur3dplugin.py'))
	
	def disconnectCallback(self, signal):
		""" Only process valueChanged signals if we actually care about one of its many signals. """
		if signal in self.objectCallbacks:
			self._objectsConnectedCount -= 1
			if self._objectsConnectedCount < 1:
				xsi.Blur3d_enableValueChanged(False)
		return
	
	def preDeleteObject(self, *args):
		"""
			\remarks	XSI does not emit pre and post signals, so just emit the delete signal
		"""
		if args:
			dispatch.objectDeleted.emit(args[0])
			
	def version(self, major=True):
		"""
			\remarks	Returns the version major of XSI.
		"""
		version = xsi.Version()
		return int(version.split('.')[0]) if major else version
		
	def name( self ):
		return "Softimage"
		
	def exportAlembic(self, filename, **kwargs):
		from blur3d.api import Scene
		scene = Scene()
		
		job = {'filename': filename}
		job.update(**kwargs)
		
		objects = kwargs.get('objects', scene.selection())
		job["objects"] = ",".join([obj.name() for obj in objects])
	
		job['in'] = kwargs.get('in', scene.animationRange()[0])
		job['out'] = kwargs.get('out', scene.animationRange()[1])
		
		jobString = ";".join( [ "=".join([k,str(v)]) for k, v in job.iteritems()] )
		print jobString 
		return xsi.alembic_export(jobString)
	
	def importAlembic(self, filename, **kwargs):
		job = {'filename': filename}
		job.update(**kwargs)
		return xsi.alembic_import_jobs(";".join( [ "=".join([k,str(v)]) for k, v in job.iteritems()] ))
	
	def installDir(self):
		""" Returns the path to the application's install directory
		
		:return: path string
		:rtyp: str
		"""
		return xsi.InstallationPath(constants.siFactoryPath)
	
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
		"11.1.57.0" : "XSI2013_SP1",
		'default' : "XSI2013"}
		
		if versionDic.has_key(version):
			jobType = versionDic[str(version)]
		else:
			jobType = versionDic['default']
		#print("debug =" + jobType)
		return jobType
		
	def refresh( self ):
		if not self._blockRefresh:
			xsi.SceneRefresh()
			xsi.Refresh()
			return True
		return False
	
	def log( self, message ):
		xsi.LogMessage( message )
		
		
# register the symbol
api.registerSymbol( 'Application', SoftimageApplication)

# Creating a single instance of Application for all code to use.
api.registerSymbol( 'application', SoftimageApplication())