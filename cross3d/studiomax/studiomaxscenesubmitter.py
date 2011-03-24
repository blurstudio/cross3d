##
#	\namespace	blur3d.api.studiomax.studiomaxscenesubmitter
#
#	\remarks	[desc::commented]
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/18/11
#

from Py3dsMax 										import mxs
from blur3d.api.abstract.abstractscenesubmitter		import AbstractSceneSubmitter

REMOTE_RENDER_SUBMIT = """
def runScript( frame ):
	from blur3d.api import SceneSubmitter, Scene
	import os.path
	
	# the scriptArchiveRoot variable will be set for a job on load
	relpath = os.path.normpath(mxs.scriptArchiveRoot)
	
	# load the submitter from xml
	submitter = SceneSubmitter.loadXml( Scene.instance(), '%s/submitter.xml' % relpath )
	
	# load a particular render element before processing
	relements = submitter.renderElements()
	if ( 0 < frame and frame <= len(reelements) ):
		submitter.setCurrentRenderElement( '%s/%s' % (relpath,os.path.basename(relements[frame-1]) ) # frames are 1 based
	
	# turn off the remote submission & render element flags since now we are processing those locally here
	submitter.setSubmitFlag( SubmitFlags.RemoteSubmit, False )
	submitter.setRenderElements( [] )
	
	# run the submission
	return submitter.submit()
"""

class StudiomaxSceneSubmitter( AbstractSceneSubmitter ):
	# define class level submission scripts
	RemoteRenderScript = REMOTE_RENDER_SUBMIT
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												private methods
	#------------------------------------------------------------------------------------------------------------------------
	def _prepareRenderSubmit( self ):
		"""
			\remarks	prepares the scene for a render submission
			\return		<bool> success
		"""
		AbstractSceneSubmitter._prepareRenderSubmit( self )
		
		# check to see if the fileName has already been generated
		if ( self.fileName() ):
			return True
		
		import os
		jobMaxFile 	= os.path.normpath('c:/temp/maxhold.mx')
		jobStatFile = os.path.normpath('c:/temp/maxhold.txt')
		
		# create max hold file
		success = mxs.saveMaxFile( jobMaxFile, clearNeedSaveFlag = False, useNewFile = False, quiet = True )
		self.setFileName( jobMaxFile )
		
		# create job stat file
		if ( os.path.exists(jobStatFile) ):
			os.remove(jobStatFile)

#		st 	= mxs.timeStamp()
#		f 	= open( jobStatFile, 'w' )
#		f2  = open( 'c:/temp/maxhold.bak', 'r' )
#		f.write( f2.read() )
#		f2.close()
#		f.close()
		
#		self.setStats( self.scene().stats().summary() )
		
		return True
	
	def _prepareRemoteSubmit( self ):
		"""
			\remarks	[virtual] provide any processing that needs to occur for a remote render submission
			\return		<bool> success
		"""
		AbstractSceneSubmitter._prepareRemoteSubmit( self )
		
		import os
		jobMaxFile 	= os.path.normpath('c:/temp/maxhold.mx')
		jobStatFile = os.path.normpath('c:/temp/maxhold.txt')
		
		# create max hold file
		success = mxs.saveMaxFile( jobMaxFile, clearNeedSaveFlag = False, useNewFile = False, quiet = True )
		if ( not jobMaxFile in self._additionalFiles ):
			self._additionalFiles.append( jobMaxFile )
		
		# create job stat file
		if ( os.path.exists(jobStatFile) ):
			os.remove(jobStatFile)
		
		return True
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def defaultJobType( self ):
		"""
			\remarks	implements AbstractScene.defaultJobType method to return the default job type based on the current application
			\return		<str>
		"""
		from blur3d.constants import SubmitType
		submitType = self.submitType()
		
		# look up the default render submit job type
		if ( submitType == SubmitType.Render ):
			mversion 	= mxs.maxVersion()[0]/1000
			if ( mversion > 10 ):
				mversion = 2009 + (mversion-11)		# shifted to years at version 11
			return 'Max%i' % mversion
		
		# look up the default script submit job type
		elif ( submitType == SubmitType.Script ):
			return 'MaxScript'
		
		return AbstractSceneSubmitter.defaultJobType( self, submitType )
	
	def customArgMapping( self ):
		"""
			\remarks	[virtual] create a mapping between the abstracted custom arg keys that are used with the blur3d system to the
						application/job specific settings that are needed.  Not all arguements need to be converted, as any argument that
						is not found will simply be ignored.  See the customArgs method for a list of the abstract argument names to be used
						when developing
			\sa			customArgs
			\return		<dict> { <str> blur3dArg: <str> jobArg, .. }
		"""
		mapping = AbstractSceneSubmitter.customArgMapping( self )
		
		# map to abstract Render settings
		mapping[ 'outputWidth' ] 			= 'flag_w'
		mapping[ 'outputHeight' ] 			= 'flag_h'
		mapping[ 'useColorCheck' ]			= 'flag_xv'
		mapping[ 'force2Sided' ]			= 'flag_x2'
		mapping[ 'renderAtmospherics' ]		= 'flag_xa'
		mapping[ 'renderEffects' ]			= 'flag_xe'
		mapping[ 'renderSuperBlack' ]		= 'flag_xk'
		mapping[ 'renderDisplacements' ]	= 'flag_xd'
		mapping[ 'renderHidden' ]			= 'flag_xh'
		mapping[ 'useFields' ]				= 'flag_xf'
		mapping[ 'useDither' ]				= 'flag_xc'
		mapping[ 'useDither256' ]			= 'flag_xp'
		mapping[ 'useVideoPost' ]			= 'flag_v'
		
		# map to abstract Script settings
		mapping[ 'run64Bit' ]				= 'runMax64'
		
		return mapping
			
	def reset( self ):
		"""
			\remarks	overloads the AbstractSceneSubmitter method to reset the arguments for this submission to their default mode based
						on the submit type for this submitter
		"""
		AbstractSceneSubmitter.reset( self )
		
		import os.path
		from blur3d.constants import SubmitType
		
		submitType = self.submitType()
		
		# initialize the render arguments
		if ( submitType == SubmitType.Render ):
			
			# initialize render custom args
			self.setCustomArg( 'outputPath', 			os.path.normpath( mxs.rendOutputFilename ) )
			self.setCustomArg( 'outputWidth',			mxs.renderWidth )
			self.setCustomArg( 'outputHeight',			mxs.renderHeight )
			self.setCustomArg( 'force2Sided',			mxs.rendForce2Side )
			self.setCustomArg( 'renderAtmospherics',	not mxs.rendAtmosphere )
			self.setCustomArg( 'renderEffects',			not mxs.rendEffects )
			self.setCustomArg( 'renderSuperBlack',		mxs.rendSuperBlack )
			self.setCustomArg( 'renderDisplacements',	not mxs.rendDisplacements )
			self.setCustomArg( 'renderHidden',			mxs.rendHidden )
			self.setCustomArg( 'useColorCheck',			mxs.rendColorCheck )
			self.setCustomArg( 'useFields',				mxs.rendFieldRender )
			self.setCustomArg( 'useDither',				mxs.rendDitherTrue )
			self.setCustomArg( 'useDither256',			mxs.rendDither256 )
			self.setCustomArg( 'useVideoPost',			False )
			
			# setup the default frame list
			rtype = mxs.rendTimeType
			if ( rtype == 1 ):
				self.setFrameList( '%i' % int(mxs.slidertime.frame) )
			elif ( rtype == 2 ):
				self.setFrameList( '%s-%s' % (int(mxs.animationRange.start),int(mxs.animationRange.end)) )
			elif ( rtype == 3 ):
				self.setFrameList( '%s-%s' % (int(mxs.rendStart.frame),int(mxs.rendEnd.frame)) )
			elif ( rtype == 4 ):
				self.setFrameList( mxs.rendPickupFrames )
			
			# set the current camera
			camera = mxs.viewport.getCamera()
			if ( camera ):
				self.setCustomArg( 'camera', camera.name )
			else:
				self.setCustomArg( 'camera', '' )
		
		return True
	
	def setCurrentRenderElement( self, renderElement ):
		"""
			\remarks 	implements the AbstractSceneSubmitter.setCurrentRenderElement method to load the inputed render element as active in the scene
						before submission
			\warning	this is considered legacy support - # EKH 03/21/11
			\param		renderElement	<str>
			\return		<bool> success
		"""
		# load the old render element library
		blurRE = mxs._blurRE
		if ( not blurRE ):
			mxs._blurLibrary.load( 'blurRenderElements' )
		
		if ( blurRE ):
			success = str(blurRE.loadRenderElement( renderElement, executeScript = True, showPrompts = False )).lower() == 'true'
		else:
			success = False
			print 'ERROR: could not load the blurRenderElements library in Maxscript'
		
		# set the job sub name
		if ( success ):
			self.setJobSubName( os.path.basename(renderElement).split( '.' )[0].replace( ' ', '_' ) )
		
		return success
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneSubmitter', StudiomaxSceneSubmitter )