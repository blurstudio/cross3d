##
#   :namespace  cross3d.maya.mayaapplication
#
#   :remarks    The MayaApplication class will define all operations for application interaction. This class should never be initalized on its own.
#				You should access it by cross3d.application. One of its main functions is connecting application callbacks to cross3d.Dispatch.
#				
#				The MayaApplication is a QObject instance and any changes to the scene data can be controlled by connecting to the signals defined here.
#   
#   :author     mikeh
#   :author     Blur Studio
#   :date       09/10/14
#

import re
import maya.cmds as cmds
from maya.OpenMaya import MSceneMessage, MMessage, MModelMessage, MEventMessage

import cross3d
from cross3d.abstract.abstractapplication import AbstractApplication

class MayaApplication(AbstractApplication):
	_callbackMap = {}
	def __init__(self):
		super(MayaApplication, self).__init__()
		# Scene can not be imported at this point, the class has not been defined.
		self._scene = None
	
	def _wildcardToRegex(self, wildcard):
		""" Convert a * syntax wildcard string into a parsable regular expression
		"""
		if wildcard:
			# Maya doesn't support our current naming convetions, so convert hyphens to underscores
			wildcard = wildcard.replace('-', '_')
			# Maya uses pipes as seperators, so escape them so they are not treated as or's
			expression = re.sub(r'(?<!\\)\|', r'\|', wildcard)
			# This will replace any "*" into ".+" therefore converting basic star based wildcards into a regular expression.
			expression = re.sub(r'(?<!\\)\*', r'.*', expression)
			if not expression[-1] == '$':
				expression += '$'
		else:
			# No wildcard provided, match everything
			expression = '.*'
		return expression
	
	def _fileNameCallback(self, clientData):
		# Ensure the scene object is created.
		if self._scene == None:
			self._scene = cross3d.Scene()
		cross3d.dispatch.dispatch(clientData, self._scene.currentFileName())
	
	def _selectionChanged(self, clientData):
		import __main__
		__main__.shit = clientData
		print 'selectionChanged', clientData

	def animationClipExtension(self):
		return self.sceneFileExtension()
		
	def connectCallback(self, signal):
		"""
		Connects a single callback. This allows cross3d to only have to
		respond to callbacks that tools actually need, instead of all 
		callbacks.  Called the first time a signal is connected to 
		this callback.
		"""
		msg = None
		funct = cross3d.dispatch.dispatch
		addCallback = MSceneMessage.addCallback
		if signal == 'sceneNewRequested':
			msg = MSceneMessage.kBeforeNew
		elif signal == 'sceneNewFinished':
			msg = MSceneMessage.kAfterNew
		elif signal == 'sceneMergeRequested':
			msg = MSceneMessage.kBeforeImport
		elif signal == 'sceneMergeFinished':
			msg = MSceneMessage.kAfterImport
		elif signal == 'sceneOpenRequested':
			msg = MSceneMessage.kBeforeOpen
		elif signal == 'sceneOpenFinished':
			msg = MSceneMessage.kAfterOpen
			funct = self._fileNameCallback
		elif signal == 'sceneSaveRequested':
			msg = MSceneMessage.kBeforeSave
		elif signal == 'sceneSaveFinished':
			msg = MSceneMessage.kAfterSave
			funct = self._fileNameCallback
		elif signal == 'selectionChanged':
			msg = MModelMessage.kActiveListModified
			addCallback = MModelMessage.addCallback
#		elif signal == 'objectRenamed':
#			# TODO: Make this work
#			msg = 'NameChanged'
#			addCallback = MEventMessage.addEventCallback
		if msg != None:
			if signal in self._callbackMap:
				raise cross3d.Exceptions.SignalAlreadyConnected('This signal is already connected. The new connection was not made.')
			else:
#				print 'connectCallback', signal
				self._callbackMap[signal] = addCallback(msg, funct, signal)
	
	def disconnectCallback(self, signal):
		"""
		Disconnect a single callback when it is no longer used. Called 
		when the last signal for this callback is disconnected.
		"""
		if signal in self._callbackMap:
			callback = self._callbackMap.pop(signal)
#			print 'disconnectCallback', signal
			MMessage.removeCallback(callback)

	def disconnect(self):
		"""
		Disconnect application specific callbacks to <cross3d.Dispatch>. This will be called 
		when <cross3d.Dispatch> is deleted, disconnect is called when the last 
		<cross3d.Dispatch> signal is disconnected.
		"""
		# iterate over keys because disconnectCallback pops the signals it disconnects
		for signal in self._callbackMap.keys():
			self.disconnectCallback(signal)
	
	def allowedCharacters(self):
		return 'A-Za-z0-9_'
		
	def name(self):
		return "Maya"

	def nameSpaceSeparator(self):
		return ':'

	def refresh(self):
		if not self._blockRefresh:
			# Ensure the scene object is created.
			if self._scene == None:
				self._scene = cross3d.Scene()
			self._scene.viewport().nativePointer().refresh(True, True)
			return True
		return False

	def sceneFileExtension(self):
		return 'ma'

	def modelFileExtension(sefl):
		return 'ma'
		
	def version(self):
		v = cmds.about(version=True).replace(' x64', '')
		return int(v)
	
	def year(self):
		return self.version()


# register the symbol
cross3d.registerSymbol('Application', MayaApplication)

# Creating a single instance of Application for all code to use.
cross3d.registerSymbol('application', MayaApplication())
