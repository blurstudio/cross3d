##
#   :namespace  cross3d.softimage.blur3dplugin
#
#	\remarks	Defines the plugin methods needed for the softimage session using the cross3d package
#	
#	\author		beta
#	\author		Blur Studio
#	\date		04/12/10
#

#-------------------------------------------------------------------------------------------------------------
# define python plugin information

from win32com.client 	import constants
from PyQt4.QtCore		import Qt
import cross3d
from cross3d import dispatch
dispatchRename = cross3d.dispatch.dispatchRename
dispatchObject = cross3d.dispatch.dispatchObject
dispatchSignal = cross3d.dispatch.dispatch
#import inspect
#-------------------------------------------------------------------------------------------------------------

_signalsEnabled = True
_enableValueChanged = False

#-------------------------------------------------------------------------------------------------------------

#def XsiApplication_fileExportRequested_OnEvent( ctxt ):
#	_signalsEnabled = False
#	print 'state change', inspect.stack()[0][3], _signalsEnabled
	
#def XsiApplication_fileExportFinished_OnEvent( ctxt ):
#	_signalsEnabled = True
#	print 'state change', inspect.stack()[0][3], _signalsEnabled
	
def XsiApplication_fileImportRequested_OnEvent( ctxt ):
	_signalsEnabled = False
	#print 'state change', inspect.stack()[0][3], _signalsEnabled
	dispatchSignal('sceneImportRequested')
	
def XsiApplication_fileImportFinished_OnEvent( ctxt ):
	_signalsEnabled = True
	#print 'state change', inspect.stack()[0][3], _signalsEnabled
	dispatchSignal('sceneImportFinished')
	
def XsiApplication_objectAdded_OnEvent( ctxt ):
	try:
		for object in ctxt.GetAttribute('Objects'):
			dispatchObject('objectCreated', object)
	except TypeError:
		cross3d.logger.debug("Unable to process objectCreated Event because it did not return a list.")
	
def XsiApplication_objectRemoved_OnEvent( ctxt ):
	for name in ctxt.GetAttribute('ObjectNames'):
		dispatch.preDelete(name)
	
#def XsiApplication_projectChanged_OnEvent( ctxt ):
#	pass
	
#def XsiApplication_refModelSaved_OnEvent( ctxt ):
#	pass
	
def XsiApplication_refModelLoadRequested_OnEvent( ctxt ):
	_signalsEnabled = False
	#print 'state change', inspect.stack()[0][3], _signalsEnabled
	# May need to define a pre refrence loading signal
	dispatchSignal('sceneImportRequested')
	
def XsiApplication_refModelLoadFinished_OnEvent( ctxt ):
	_signalsEnabled = True
	#print 'state change', inspect.stack()[0][3], _signalsEnabled
	# May need to define a post refrence loading signal
	dispatchSignal('sceneImportFinished')
	
def XsiApplication_renderFrameRequested_OnEvent( ctxt ):
	#dispatch.renderFrameRequested.emit( int( ctxt.GetAttribute( 'RenderType' ) ), str( ctxt.GetAttribute( 'FileName' ) ), int( ctxt.GetAttribute( 'Frame' ) ), int( ctxt.GetAttribute( 'Sequence' ) ), int( ctxt.GetAttribute( 'RenderField' ) ) )
	pass
	
def XsiApplication_renderFrameFinished_OnEvent( ctxt ):
	#dispatch.renderFrameFinished.emit( int( ctxt.GetAttribute( 'RenderType' ) ), str( ctxt.GetAttribute( 'FileName' ) ), int( ctxt.GetAttribute( 'Frame' ) ), int( ctxt.GetAttribute( 'Sequence' ) ), int( ctxt.GetAttribute( 'RenderField' ) ) )
	pass
	
def XsiApplication_sceneClosed_OnEvent( ctxt ):
	dispatch.sceneClosed.emit()
	
def XsiApplication_sceneNewRequested_OnEvent( ctxt ):
	_signalsEnabled = False
	#print 'state change', inspect.stack()[0][3], _signalsEnabled
	dispatchSignal('sceneNewRequested')
	
def XsiApplication_sceneNewFinished_OnEvent( ctxt ):
	_signalsEnabled = True
	#print 'state change', inspect.stack()[0][3], _signalsEnabled
	dispatchSignal('sceneNewFinished')
	
def XsiApplication_sceneOpenRequested_OnEvent( ctxt ):
	_signalsEnabled = False
	#print 'state change', inspect.stack()[0][3], _signalsEnabled
	dispatchSignal('sceneOpenRequested', ctxt.GetAttribute('FileName'))
	
def XsiApplication_sceneOpenFinished_OnEvent( ctxt ):
	_signalsEnabled = True
	#print 'state change', inspect.stack()[0][3], _signalsEnabled
	dispatchSignal('sceneOpenFinished', ctxt.GetAttribute('FileName'))
	
def XsiApplication_sceneSaveRequested_OnEvent( ctxt ):
	_signalsEnabled = False
	#print 'state change', inspect.stack()[0][3], _signalsEnabled
	dispatchSignal('sceneSaveRequested', ctxt.GetAttribute('FileName'))
	
def XsiApplication_sceneSaveFinished_OnEvent( ctxt ):
	_signalsEnabled = True
	#print 'state change', inspect.stack()[0][3], _signalsEnabled
	dispatchSignal('sceneSaveFinished', ctxt.GetAttribute('FileName'))
	
def XsiApplication_sceneSaveAsRequested_OnEvent( ctxt ):
	_signalsEnabled = False
	#print 'state change', inspect.stack()[0][3], _signalsEnabled
	dispatchSignal('sceneSaveRequested', ctxt.GetAttribute('FileName'))
	
def XsiApplication_sceneSaveAsFinished_OnEvent( ctxt ):
	_signalsEnabled = True
	#print 'state change', inspect.stack()[0][3], _signalsEnabled
	dispatchSignal('sceneSaveFinished', ctxt.GetAttribute('FileName'))
	
def XsiApplication_selectionChanged_OnEvent( ctxt ):
	# Send different signals based on this
	# int( ctxt.GetAttribute( 'ChangeType' )
	_signalsEnabled = True
	dispatch.selectionChanged.emit()
	
#def XsiApplication_sequenceRenderRequested_OnEvent( ctxt ):
#	dispatch.sequenceRenderRequested.emit( int( ctxt.GetAttribute( 'RenderType' ) ), str( ctxt.GetAttribute( 'FileName' ) ), int( ctxt.GetAttribute( 'Frame' ) ), int( ctxt.GetAttribute( 'Sequence' ) ), int( ctxt.GetAttribute( 'RenderField' ) ) )
#	
#def XsiApplication_sequenceRenderFinished_OnEvent( ctxt ):
#	dispatch.sequenceRenderFinished.emit( int( ctxt.GetAttribute( 'RenderType' ) ), str( ctxt.GetAttribute( 'FileName' ) ), int( ctxt.GetAttribute( 'Frame' ) ), int( ctxt.GetAttribute( 'Sequence' ) ), int( ctxt.GetAttribute( 'RenderField' ) ) )
	
#def XsiApplication_timeChanged_OnEvent( ctxt ):
#	#dispatch.currentFrameChanged.emit( int( ctxt.GetAttribute( 'Frame' ) ) )
#	pass
	
def XsiApplication_valueChanged_OnEvent( ctxt ):
	if _signalsEnabled and _enableValueChanged:
		GetAttribute = ctxt.GetAttribute
		object = GetAttribute( 'Object' ).parent
		fullname = GetAttribute( 'fullName' )
		previousValue = GetAttribute( 'PreviousValue' )
#		print 'Emiting changed signal', inspect.stack()[0][3]
#		dispatch.eventCalled.emit('ValueChanged', [object, fullname, previousValue])
		end = fullname.endswith
		if end('.Name'):
			dispatchRename('objectRenamed', previousValue, object(), object)
		elif end('.visibility.viewvis'):
			value = object.Parameters('viewvis').Value
			if object.Parameters('rendvis').Value == value:
				if value:
					dispatchObject('objectUnHide', object.parent)
				else:
					dispatchObject('objectHide', object.parent)
		elif end('.visibility.rendvis'):
			value = object.Parameters('rendvis').Value
			if object.Parameters('viewvis').Value == value:
				if value:
					dispatchObject('objectUnHide', object.parent)
				else:
					dispatchObject('objectHide', object.parent)
		elif end('.visibility.selectability'):
			if object.Parameters('selectability').Value:
				dispatchObject('objectUnfreeze', object.parent)
			else:
				dispatchObject('objectFreeze', object.parent)
		elif end('.kine.global'):
			dispatchObject('objectParented', object.parent)
#		else:
#			print 'Unknown signal', fullname, previousValue, object

#-------------------------------------------------------------------------------------------------------------
# Get the enabled state for ValueChanged
def Cross3d_valueChangedEnabled_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = True
	return True
	
def Cross3d_valueChangedEnabled_Execute():
	return _enableValueChanged

# set the enabled state for ValueChanged
def Cross3d_enableValueChanged_Init( ctxt ):
	oCmd = ctxt.Source
	oCmd.Description = ""
	oCmd.ReturnValue = True
	
	oArgs = oCmd.Arguments
	oArgs.Add("state",constants.siArgumentInput)
	
	return True
	
def Cross3d_enableValueChanged_Execute(state):
	global _enableValueChanged
	_enableValueChanged = state
	return True

#-------------------------------------------------------------------------------------------------------------

def XSILoadPlugin( reg ):
	reg.author 	= 'Blur Studio'
	reg.name 	= 'cross3d'
	reg.email	= 'beta@blur.com'
	reg.url		= 'www.blur.com'
	reg.major	= 1
	reg.minor	= 0
	
	# Register signals
#	reg.RegisterEvent( 'XsiApplication_fileExportRequested',		constants.siOnBeginFileExport )
#	reg.RegisterEvent( 'XsiApplication_fileExportFinished',			constants.siOnEndFileExport )
	reg.RegisterEvent( 'XsiApplication_fileImportRequested',		constants.siOnBeginFileImport )
	reg.RegisterEvent( 'XsiApplication_fileImportFinished',			constants.siOnEndFileImport )
	reg.RegisterEvent( 'XsiApplication_objectAdded',				constants.siOnObjectAdded )
	reg.RegisterEvent( 'XsiApplication_objectRemoved',				constants.siOnObjectRemoved )
#	reg.RegisterEvent( 'XsiApplication_projectChanged',				constants.siOnChangeProject )
#	reg.RegisterEvent( 'XsiApplication_refModelSaved',				constants.siOnRefModelModSave )
	reg.RegisterEvent( 'XsiApplication_refModelLoadRequested',		constants.siOnBeginRefModelModLoad )
	reg.RegisterEvent( 'XsiApplication_refModelLoadFinished',		constants.siOnEndRefModelModLoad )
	reg.RegisterEvent( 'XsiApplication_renderFrameRequested',		constants.siOnBeginFrame )
	reg.RegisterEvent( 'XsiApplication_renderFrameFinished',		constants.siOnEndFrame )
	reg.RegisterEvent( 'XsiApplication_sceneClosed',				constants.siOnCloseScene )
	reg.RegisterEvent( 'XsiApplication_sceneNewRequested',			constants.siOnBeginNewScene )
	reg.RegisterEvent( 'XsiApplication_sceneNewFinished',			constants.siOnEndNewScene )
	reg.RegisterEvent( 'XsiApplication_sceneOpenRequested',			constants.siOnBeginSceneOpen )
	reg.RegisterEvent( 'XsiApplication_sceneOpenFinished',			constants.siOnEndSceneOpen )
	reg.RegisterEvent( 'XsiApplication_sceneSaveRequested',			constants.siOnBeginSceneSave2 )
	reg.RegisterEvent( 'XsiApplication_sceneSaveFinished',			constants.siOnEndSceneSave2 )
	reg.RegisterEvent( 'XsiApplication_sceneSaveAsRequested',		constants.siOnBeginSceneSaveAs )
	reg.RegisterEvent( 'XsiApplication_sceneSaveAsFinished',		constants.siOnEndSceneSaveAs )
	reg.RegisterEvent( 'XsiApplication_selectionChanged',			constants.siOnSelectionChange )
#	reg.RegisterEvent( 'XsiApplication_sequenceRenderRequested',	constants.siOnBeginSequence )
#	reg.RegisterEvent( 'XsiApplication_sequenceRenderFinished',		constants.siOnEndSequence )
#	reg.RegisterEvent( 'XsiApplication_timeChanged',				constants.siOnTimeChange )
#	reg.RegisterEvent( 'XsiApplication_valueChanged',				constants.siOnValueChange )

	# Note:  dataChanged slows down xsi
	
	reg.RegisterCommand("Cross3d_enableValueChanged", "Cross3d_enableValueChanged")
	reg.RegisterCommand("Cross3d_valueChangedEnabled", "Cross3d_valueChangedEnabled")
	
	return True

def XSIUnloadPlugin( reg ):
	pass
