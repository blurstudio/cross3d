##
#	\namespace	cross3d.abstract.motionbuilderapplication
#
#	\remarks	The StudiomaxApplication class will define all operations for application interaction. It is a singleton class, so calling cross3d.Application() will
#				always return the same instance of Application. One of its main functions is connecting application callbacks to cross3d.Dispatch.
#				
#				The StudiomaxApplication is a QObject instance and any changes to the scene data can be controlled by connecting to the signals defined here.
#
#				When subclassing the AbstractScene, methods tagged as @abstractmethod will be required to be overwritten.  Methods tagged with [virtual]
#				are flagged such that additional operations could be required based on the needs of the method.  All @abstractmethod methods MUST be implemented
#				in a subclass.
#	
#	\author		Mikeh
#	\author		Blur Studio
#	\date		06/07/11
#

#------------------------------------------------------------------------------------------------------------------------

import sys
import os
import pyfbsdk as mob

import cross3d
from cross3d.abstract.abstractapplication import AbstractApplication

#------------------------------------------------------------------------------------------------------------------------

dispatch = None

class MotionBuilderApplication(AbstractApplication):
	def __init__(self):
		self._fbapp = mob.FBApplication()
		super(MotionBuilderApplication, self).__init__()
	
	def _mobCallback(self, caller, event):
		# Note: if a error is raised in this function, it will disconnect the callback from motion builder.
		eType = event.Type
		eName = mob.FBEventName
		if eType == eName.kFBEventFileNew:
			cross3d.dispatch.dispatch('sceneNewRequested')
		elif eType == eName.kFBEventFileNewCompleted:
			cross3d.dispatch.dispatch('sceneNewFinished')
		elif eType == eName.kFBEventFileMerge:
			cross3d.dispatch.dispatch('sceneMergeRequested')
		elif eType == eName.kFBEventFileOpen:
			cross3d.dispatch.dispatch('sceneOpenRequested', 'Unknown')
		elif eType == eName.kFBEventFileOpenCompleted:
			cross3d.dispatch.dispatch('sceneOpenFinished', 'Unknown')
		elif eType == eName.kFBEventFileSave:
			cross3d.dispatch.dispatch('sceneSaveRequested', 'Unknown')
		elif eType == eName.kFBEventFileSaveCompleted:
			cross3d.dispatch.dispatch('sceneSaveFinished', 'Unknown')
	
	def connectCallback(self, signal):
		"""
		Connects a single callback. This allows cross3d to only have to
		respond to callbacks that tools actually need, instead of all 
		callbacks.  Called the first time a signal is connected to 
		this callback.
		"""
		if signal == 'sceneNewRequested':
			self._fbapp.OnFileNew.Add(self._mobCallback)
		elif signal == 'sceneNewFinished':
			self._fbapp.OnFileNewCompleted.Add(self._mobCallback)
		elif signal == 'sceneMergeRequested':
			self._fbapp.OnFileMerge.Add(self._mobCallback)
		elif signal == 'sceneOpenRequested':
			self._fbapp.OnFileOpen.Add(self._mobCallback)
		elif signal == 'sceneOpenFinished':
			self._fbapp.OnFileOpenCompleted.Add(self._mobCallback)
		elif signal == 'sceneSaveRequested':
			self._fbapp.OnFileSave.Add(self._mobCallback)
		elif signal == 'sceneSaveFinished':
			self._fbapp.OnFileSaveCompleted.Add(self._mobCallback)
	
	def disconnectCallback(self, signal):
		"""
		Disconnect a single callback when it is no longer used. Called 
		when the last signal for this callback is disconnected.
		"""
		if signal == 'sceneNewRequested':
			self._fbapp.OnFileNew.Remove(self._mobCallback)
		elif signal == 'sceneNewFinished':
			self._fbapp.OnFileNewCompleted.Remove(self._mobCallback)
		elif signal == 'sceneMergeRequested':
			self._fbapp.OnFileMerge.Remove(self._mobCallback)
		elif signal == 'sceneOpenRequested':
			self._fbapp.OnFileOpen.Remove(self._mobCallback)
		elif signal == 'sceneOpenFinished':
			self._fbapp.OnFileOpenCompleted.Remove(self._mobCallback)
		elif signal == 'sceneSaveRequested':
			self._fbapp.OnFileSave.Remove(self._mobCallback)
		elif signal == 'sceneSaveFinished':
			self._fbapp.OnFileSaveCompleted.Remove(self._mobCallback)

	def disconnect(self):
		"""
		Disconnect application specific callbacks to <cross3d.Dispatch>. This will be called 
		when <cross3d.Dispatch> is deleted, disconnect is called when the last 
		<cross3d.Dispatch> signal is disconnected.
		"""
		self.disconnectCallback('sceneNewRequested')
		self.disconnectCallback('sceneNewFinished')
		self.disconnectCallback('sceneMergeRequested')
		self.disconnectCallback('sceneOpenRequested')
		self.disconnectCallback('sceneOpenFinished')
		self.disconnectCallback('sceneSaveRequested')
		self.disconnectCallback('sceneSaveFinished')
		return

	def name( self ):
		return "MotionBuilder"
	
	def version(self):
		path = mob.__file__
		if '2012' in path:
			return 2012
		elif '2013' in path:
			return 2013
		elif '2014' in path:
			return 2014
		else:
			return 2015
	
	def year(self):
		return self.version()

# register the symbol
cross3d.registerSymbol('Application', MotionBuilderApplication)

# Creating a single instance of Application for all code to use.
cross3d.registerSymbol('application', MotionBuilderApplication())
