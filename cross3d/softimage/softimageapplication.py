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
						connect should only be called after blur3d has been initalized.
		"""
		global dispatch
		import blur3d.api
		dispatch = blur3d.api.dispatch
		super(SoftimageApplication, self).connect()
		xsi.LoadPlugin(os.path.abspath(__file__ + '/../blur3dplugin.py'))
	
	def disconnect(self):
		xsi.UnloadPlugin(os.path.abspath(__file__ + '/../blur3dplugin.py'))
	
#	def connect(self):
#		global Dispatch, DispatchProcess
#		from blur3d.api.classes import Dispatch
#		from blur3d.api.classes.dispatchprocess import DispatchProcess
#		Dispatch().setProcess(DispatchProcess())
#	
#	def disconnect(self):
#		thread = Dispatch.process()
#		thread.quit()
#		thread.wait()
	
#	def valueChanged(self, objectAttr, fullname, previousValue):
#		"""
#			\remarks	Responsible for decoding xsi's generic valueChanged callback for object changes into blur3d.api.Dispatch's callbacks
#		"""
#		import blur3d.api
#		object = objectAttr.parent
#		if fullname.endswith('.Name'):
#			print "The Name has changed, Old: %s, New: %s" % (previousValue, object())
#			blur3d.api.dispatch.dispatchRename(previousValue, object(), object)
#		elif fullname.endswith('.visibility.viewvis') or fullname.endswith('.visibility.rendvis'):
#			print 'View visibility changed'
#		elif fullname.endswith('.visibility.selectability'):
#			print 'The object was frozen/unfrozen'
	
	def preDeleteObject(self, *args):
		"""
			\remarks	XSI does not emit pre and post signals, so just emit the delete signal
		"""
		if args:
			dispatch.objectDeleted.emit(args[0])
	
# register the symbol
from blur3d import api
api.registerSymbol( 'Application', SoftimageApplication)