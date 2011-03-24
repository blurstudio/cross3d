##
#	\namespace	blur3d.api.abstract.abstractscenesubmitter
#
#	\remarks	The AbstractSceneSubmitter class defines the way a scene will interact with the render farm when submitting jobs
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/18/11
#

from blur3d.api import SceneWrapper

RENDER_PROGRESS_SECTIONS 	= [ 'Validating Scene', 'Pre-Processing Scene', 'Post-Processing Scene' ]
SCRIPT_PROGRESS_SECTIONS	= [ 'Preparing Script', 'Archiving Files' ]
SUBMIT_PROGRESS_SECTIONS	= [ 'Preparing to Submit', 'Submitted to Farm', 'Waiting for Response' ]

class AbstractSceneSubmitter( SceneWrapper ):
	__cache = []
	
	# define submission scripts
	RemoteRenderScript = ''				# needs to be redefined in a subclass
	
	def __init__( self, scene, submitType ):
		"""
			\remarks	the submitter class does not take a native wrapper since it techincally will live outside of the scene
						heirarchy and simply work onto the scene itself.  We will provide the nativePointer for this wrapper manually
			\param		scene			<blur3d.api.Scene>
			\param		submitType		<blur3d.constants.SubmitType>		submit type to be created
		"""
		# initialize the SceneWrapper base class
		SceneWrapper.__init__( self, scene, None )
		
		# initialize the default job settings based on the scene
		element					= scene.currentElement()
		filename				= scene.currentFileName()
		
		self._submitType			= submitType
		
		import os.path, blur.Stone, socket
		if ( filename ):
			self._jobName			= '.'.join(os.path.basename( filename ).split('.')[:-1])
			self._fileOriginal		= os.path.normpath( filename )
		else:
			self._jobName			= ''
			self._fileOriginal		= ''
			
		self._fileName			= ''
		self._jobSubName			= ''
		self._jobType				= ''
		self._projectName			= element.project().name()
		self._username				= blur.Stone.getUserName()
		self._hostname				= socket.gethostname()
		
		from blur3d.constants import NotifyType
		self._notifyOnError			= NotifyType.Email
		self._notifyOnComplete		= 0
		
		self._hostNames				= []
		self._serviceNames			= []
		self._priority				= 50
		self._frameList				= ''
		
		self._packetType			= 'sequential'
		self._packetSize			= 0
		self._autoPacketSize		= True
		
		self._deleteJobOnComplete	= False
		self._prioritizeOuterFrames	= False
		
		self._useFrameNth			= False
		self._frameNth				= 0
		self._invertFrameNth		= False
		
		self._useMaxTaskTime		= False
		self._maxTaskTime			= 90 * 60	# seconds, default is 90 minutes * 60 seconds/minute
		
		self._customArgs			= {}
		
		# initialize non-job submitter settings
		from blur3d.constants import SubmitFlags, ProxyType
		
		self._submitFlags			= SubmitFlags.Default
		self._proxyType				= ProxyType.Disabled
		self._proxyFPS				= 30.0
		self._renderElements		= []
		self._cameras				= []
		
		# THE FOLLOWING ARGUMENTS DO NOT NEED TO BE SAVED WITH XML DEFINITIONS, THEY ARE DEFINED ON THE FLY PROGRAMMATICALLY
		# define the argument normalization system
		self._argBooleans		= self.customArgBooleans()
		self._argMapping		= self.customArgMapping()
		self._additionalFiles	= []							# used when creating a package for submission
		self._progress			= None
		
		# set the submit type
		self.setSubmitType(submitType)
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def _buildArgs( self ):
		# initialize the custom arguments based on normalization and boolean definitions
		output = {}
		for key, value in self._customArgs.items():
			okey = self._argMapping.get(str(key),str(key))
			
			# by default, booleans need to be converted to integers for the submitter
			if ( type(value) == bool and not key in self._argBooleans ):
				output[okey] = int(value)
			else:
				output[okey] = value
		
		# create the standard args
		if ( self._jobSubName ):
			output['job']				= '%s_%s' % (self._jobName,self._jobSubName)
		else:
			output['job']				= self._jobName
			
		output['jobType']				= self._jobType
		output['fileOriginal']			= self._fileOriginal
		output['fileName']				= self._fileName
		output['user']					= self._username
		output['host']					= self._hostname
		output['projectName']			= self._projectName
		output['hosts']					= ','.join( self._hostNames )
		output['services']				= ','.join( self._serviceNames )
		output['priority']				= self._priority
		output['frameList']				= self._frameList
		output['packetType']			= self._packetType
		output['deleteOnComplete']		= int(self._deleteJobOnComplete)
		output['prioritizeOuterFrames']	= int(self._prioritizeOuterFrames)
		
		# create notification preferences
		if ( self._username ):
			u = self._username
			n = ''
			
			from blur3d.constants import NotifyType
			
			# define the complete notifications
			if ( self._notifyOnComplete & NotifyType.Jabber ):
				n += 'j'
			if ( self._notifyOnComplete & NotifyType.Email ):
				n += 'e'
				
			if ( n ):
				output['notifyOnComplete'] = '%s:%s' % (u,n)
			
			# define the error notifications
			if ( self._notifyOnError & NotifyType.Jabber ):
				n += 'j'
			if ( self._notifyOnError & NotifyType.Email ):
				n += 'e'
			
			if ( n ):
				output['notifyOnError'] = '%s:%s' % (u,n)
		
		# create the nth frame preferences
		if ( self._useFrameNth ):
			output['frameNth']		= self._frameNth
			output['frameFill']		= int(self._invertFrameNth)
		
		# create the max task time preferences
		if ( self._useMaxTaskTime ):
			output['maxtasktime']	= self._maxTaskTime
		
		# create the packet size preferences
		if ( not self._autoPacketSize ):
			output['packetSize']	= self._packetSize
		
		return dict( [ (key,str(value)) for key, value in output.items() ] )
		
	def _cache( self ):
		"""
			\remarks	the blur.Stone Submitter must remain in memory throughout the submission process to be successful, so when it
						completes this will add the pointer from the cache
		"""
		if ( not self in AbstractSceneSubmitter.__cache ):
			AbstractSceneSubmitter.__cache.append(self)
			
			if ( self._nativePointer ):
				# uncache the submitter when the submission completes
				self._nativePointer.submitSuccess.connect(	self._uncache )
				self._nativePointer.submitError.connect(	self._uncache )
		
	def _prepareRenderSubmit( self ):
		"""
			\remarks	[virtual] provide any processing that needs to occur for a render submission, by default, this method does nothing
			\return		<bool> success
		"""
		return True
	
	def _prepareRemoteSubmit( self ):
		"""
			\remarks	[virtual] provide any processing that needs to occur for a remote render submission
			\return		<bool> success
		"""
		# collect the render elements and all associated files with the render elements
		import glob, os.path
		
		# create the xml definition file for this submitter
		self.saveXml( 'c:/temp/submitter.xml' )
		self._additionalFiles.append( 'c:/temp/submitter.xml' )
		
		return True
		
	def _submit( self ):
		"""
			\remarks	private method for actually performing the submission and caching
			\warning	this method should ONLY be called internally from this class
		"""
		scene = self.scene()
		
		# initialize the submission system
		import blur.Stone
		from blur.absubmit import Submitter
		self._nativePointer = Submitter(scene)
		
		# create the submitter connections
		self._nativePointer.submitSuccess.connect( 	scene.emitSubmitSuccess )
		self._nativePointer.submitError.connect(	scene.emitSubmitError )
		
		# collect all of the arguments that will be supplied for submission
		scene.emitProgressUpdated( SUBMIT_PROGRESS_SECTIONS[0], 100 )
		self._nativePointer.applyArgs( self._buildArgs() )
		scene.emitProgressUpdated( SUBMIT_PROGRESS_SECTIONS[1], 100 )
		self._nativePointer.submit()
		
		from blurdev import debug
		if ( debug.isDebugLevel( debug.DebugLevel.Mid ) ):
			self._nativePointer.waitForFinished()
		else:
			self._cache()
			
	def _submitRender( self ):
		"""
			\remarks	submit the data for this submitter to the farm as a render job
			\sa			submit
			\return		<bool> success
		"""
		from blur3d.constants import SubmitFlags
		
		scene = self.scene()
		
		# record render submission information
		if ( not self._prepareRenderSubmit() ):
			scene.emitProgressErrored( RENDER_PROGRESS_SECTIONS[0], 'The submission data was not able to be saved properly.' )
			return False
		
		# make sure we have a valid output path specified
		outputpath = self.customArg('outputPath')
		if ( not outputpath ):
			scene.emitProgressErrored( RENDER_PROGRESS_SECTIONS[0], 'There is no output path specified for this Render submission' )
			return False
		
		scene.emitProgressUpdated( RENDER_PROGRESS_SECTIONS[0], 100 )
		
		# delete old frames if necessary
		if ( self.hasSubmitFlag( SubmitFlags.DeleteOldFrames ) ):
			self.deleteOldFrames( outputpath )
		
		scene.emitProgressUpdated( RENDER_PROGRESS_SECTIONS[1], 100 )
		
		# submit the job
		self._submit()
		
		# record the info file if necessary
		if ( self.hasSubmitFlag( SubmitFlags.WriteInfoFile ) ):
			self.writeInfoFile( outputpath )
		
		scene.emitProgressUpdated( RENDER_PROGRESS_SECTIONS[2], 100 )
				
		return True
	
	def _submitRemoteRender( self ):
		"""
			\remarks	creates a script job for a remote render submission based on this submitter
			\sa			submit
			\return		<bool> success
		"""
		from blur3d.constants import SubmitFlags, SubmitType
		
		scene = self.scene()
		tempscriptfile	= 'c:/temp/script.py'
		
		# make sure this instance has a remote render script defined
		if ( not self.RemoteRenderScript ):
			scene.emitProgressErrored( SCRIPT_PROGRESS_SECTIONS[0], 'There is no remote render script defined.' )
			return False
		
		# remove the old archive
		import os
		try:
			if ( os.path.exists(tempscriptfile) ):
				os.remove(tempscriptfile)
		except:
			scene.emitProgressErrored( SCRIPT_PROGRESS_SECTIONS[0], 'Could not remove the temporary render script files.' )
			return False
		
		# create the remote submission information
		submitter = self.scene().createSubmitter(SubmitType.Script)
		
		# save the script to a custom location
		f = open( tempscriptfile, 'w' )
		f.write( self.RemoteRenderScript )
		f.close()
		
		# create the script with the remote render script
		submitter.setCustomArg( 'script', tempscriptfile )
		
		# collect the additional files for the script submission
		filenames = []
		for filename in self.renderElements():
			filenames += [ filename ] + glob.glob( os.path.splitext(filename)[0] + '*.*' )
			
		submitter.setAdditionalFiles( filenames )
		
		if ( not submitter._prepareRemoteSubmit() ):
			return False
		
		# calculate the number of frames for the submission script as the number of render elements that need to be loaded
		num_elements = len(self.renderElements())
		if ( num_elements > 1 ):
			submitter.setFrameList( '1-%i' % num_elements )
			
			# if we are deleting hidden geometry, force the packet size to 1
			if ( self.hasSubmitFlag( SubmitFlags.DeleteHiddenGeometry ) ):
				submitter.setPacketSize( 1 )
			
			# otherwise, set the packet size as the length of the elements
			else:
				submitter.setPacketSize( num_elements )
		
		submitter.submit()
		
	def _submitScript( self ):
		"""
			\remarks	submits the data from this scene submitter to the farm as a script job
			\sa			submit
			\return		<bool> success
		"""
		import os.path
		
		script = self.customArg( 'script' )
		if ( not script ):
			return False
		
		scene = self.scene()
		
		# create the submission package
		if ( self._additionalFiles ):
			temparchivefile = 'c:/temp/archive.zip'
			try:
				if ( os.path.exists(temparchivefile) ):
					os.remove(temparchivefile)
			except:
				scene.emitProgressErrored( SCRIPT_PROGRESS_SECTIONS[0], 'Could not remove the temporary archive location.' )
				return False
			
			scene.emitProgressUpdated( SCRIPT_PROGRESS_SECTIONS[1], 100 )
				
			from blurdev import zipper
			print 'zipping', ([script] + self._additionalFiles)
			if ( not zipper.packageFiles( [script] + self._additionalFiles, temparchivefile ) ):
				scene.emitProgressErrored( SCRIPT_PROGRESS_SECTIONS[1], 'Could not package the files together' )
				return False
			
			self.setFileName( temparchivefile )
		
		scene.emitProgressUpdated( SCRIPT_PROGRESS_SECTIONS[1], 100 )
		
		# submit the script job
		return self._submit()
		
	def _uncache( self ):
		"""
			\remarks	the blur.Stone Submitter must remain in memory throughout the submission process to be successful, so when it
						completes this will remove the pointer from the cache
		"""
		# clear the submitter from memory
		scene			= self._scene
		nativeSubmitter = self._nativePointer
		
		if ( nativeSubmitter ):
			# disconnect from the scene
			nativeSubmitter.submitError.disconnect( 	scene.emitSubmitError )
			nativeSubmitter.submitSuccess.disconnect( 	scene.emitSubmitSuccess )
			nativeSubmitter.submitSuccess.disconnect(	self.submitSucceeded )
			nativeSubmitter.submitError.disconnect(		self.submitErrored )
			
			# clear the submitter from Qt's memory
			nativeSubmitter.setParent(None)
			nativeSubmitter.deleteLater()
		
		# remove the submitter
		self._nativePointer = None
		
		# remove the submitter from the cache
		if ( self in AbstractSceneSubmitter.__cache ):
			AbstractSceneSubmitter.__cache.remove(self)
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def additionalFiles( self ):
		"""
			\remarks	return the list of additional files that will be packaged together when creating a package for submission
			\return		<list> [ <str> filename, .. ]
		"""
		
	
	def autoPacketSize( self ):
		"""
			\remarks	return whether or not this submission should automatically determine the packet size
			\return		<bool>
		"""
		return self._autoPacketSize
	
	def cameras( self ):
		"""
			\remarks	return the list of cameras that should be used when processing this submission.  if there are cameras associated
						with the submission, then it will need to create multiple job submissions, one per camera, for the farm
			\warning	this property is only used during processing, and is not actually a property on a farm job
			\return		<list> [ <blur3d.api.SceneCamera>, .. ]
		"""
		return self._cameras
	
	def customArgs( self ):
		"""
			\remarks	return custom arguments that will be set based on the application and job type that we are going to be using
			\return		<dict> { <str> key: <variant> value, .. }
			\appendix	
						SubmitType.Render Args:
						
							deformMotionBlur		force2Sided				outputPath
							outputHeight			outputWidth				pass	
							renderer				renderAtmospherics		renderDisplacements			
							renderHidden			renderEffects			renderSuperBlack					
							useColorCheck			useDither256			useDither
							useFieldRender			useMotionBlur			useVideoPost
						
						SubmitType.Script Args:
							
							requiresUi				runPythonScript			run64Bit
							script					silent
		"""
		return self._customArgs
	
	def customArg( self, key, default = None ):
		"""
			\remarks	return the custom argument's value for the inputed key
			\param		key			<str>
			\param		default		<variant>	return value if the key is not set
			\return		<variant> value
		"""
		return self._customArgs.get(str(key),default)
	
	def customArgBooleans( self ):
		"""
			\remarks	[virtual] defines which keys from the customArgs dictionary should be preserved as booleans and not converted
						to integers when the submission arguments get generated
			\return		<list> [ <str>, .. ]
		"""
		return []
	
	def customArgMapping( self ):
		"""
			\remarks	[virtual] create a mapping between the abstracted custom arg keys that are used with the blur3d system to the
						application/job specific settings that are needed.  Not all arguements need to be converted, as any argument that
						is not found will simply be ignored.  See the customArgs method for a list of the abstract argument names to be used
						when developing
			\sa			customArgs
			\return		<dict> { <str> blur3dArg: <str> jobArg, .. }
		"""
		return {}
	
	def defaultJobType( self ):
		"""
			\remarks	[virtual] return the default job type for this submitter instance based on the abstract submitType inputed.
			\param		submitType		<blur3d.constants.SubmitType>
			\return		<str>
		"""
		return ''
	
	def deleteOldFrames( self, path ):
		"""
			\remarks	removes the frames at the inputed path
			\param		path	<str>
			\return		<bool> success
		"""
		import os, glob
		path = str(path).strip()
		if ( not path ):
			return False
		
		fpath = os.path.split(path)[0]
		if ( not os.path.exists(fpath) ):
			return False
			
		# ignore these file types when removing files
		ignore 	= ('.txt','.log',)
		
		import glob, os
		usespool	= False
		files 		= glob.glob( os.path.split(path)[0] + '/*.*' )
		
		for file in files:
			if ( os.path.splitext(file)[1] in ignore ):
				continue
			try:
				os.remove(file)
			except:
				usespool = True
		
		# if we were unable to remove some of the files, use the backend spooler to force removal
		if ( usespool ):
			from blur3d import spool
			fname = os.path.split( path )[0] + '/*' + os.path.splitext( path )[1]
			spool.removeFiles( fname )
		
		return True
	
	def deleteJobOnComplete( self ):
		"""
			\remarks	return whether or not the job should be deleted from the farm automatically when it finishes
			\return		<bool>
		"""
		return self._deleteJobOnComplete
	
	def fileOriginal( self ):
		"""
			\remarks	return the original file name for this submitter.  this property represents the source file that was used to
						submit the job to the farm, not necessarily the actual file that was submitted as often times there will be a
						temp file saved before submission
			\return		<str>
		"""
		return self._fileOriginal
	
	def frameList( self ):
		"""
			\remarks	return the frame list that will be used to determine the number of sub-tasks and/or frames that need to be processed
						when the job submits to the farm
			\warning	this property cannot be left blank or the submission will fail
			\return		<str>
		"""
		return self._frameList
	
	def fileName( self ):
		"""
			\remarks	return the name of the actual file being submitted to the farm.  If there is any temp saving that occurs during
						the submission process, this is the value that will point to the actual file being copied for use in the submit
			\warning	this parameter must be set or the job will not submit properly
		"""
		return self._fileName
	
	def frameNth( self ):
		"""
			\remarks	return the number of frames that should be alternated when using the frameNth option on a job
			\sa			invertFrameNth, useFrameNth
			\return		<int>
		"""
		return self._frameNth
	
	def hasSubmitFlag( self, flag ):
		"""
			\remarks	return whether or not the inputed submission flag is currently set for this submitter
			\param		flag		<blur3d.constants.SubmitFlag>
			\return		<bool>
		"""
		return (self._submitFlags & flag) != 0
	
	def hostname( self ):
		"""
			\remarks	return the hostname that is associated with this submission
			\return		<str>
		"""
		return self._hostname
	
	def hostNames( self ):
		"""
			\remarks	return the list of host names that this submitter will send the job to.  if a blank list is used, then it will not
						specify any particular hosts on submission
			\return		<list> [ <str>, .. ]
		"""
		return self._hostNames
	
	def hosts( self ):
		"""
			\remarks	return the list of host records that this submitter will send the job to.  if a blank list is used, then it will
						not specify any particular hosts on submission.  This method is a wrapper on top of the
						hostNames method to look up actual database records based on the set host names list for this instance
			\return		<list> [ <trax.api.data.Host>, .. ]
		"""
		if ( not self._hostNames ):
			return []
			
		from blurdev import debug
		try:
			import trax.api
		except:
			debug.debugObject( self.services, 'trax package is not installed.' )
			return []
			
		return trax.api.data.Host.select( 'name IN (%s)' % ','.join( [ "'%s'" % hostname for hostname in self._hostNames ] ) )
	
	def invertFrameNth( self ):
		"""
			\remarks	return whether or not the Nth frame value should be rendering the Nth frames (when False), or the
						frames BETWEEN the Nth frames (when True)
			\sa			frameNth, useFrameNth
			\return		<bool>
		"""
		return self._invertFrameNth
	
	def jobName( self ):
		"""
			\remarks	return the name that will be used for the farm job when it is created
			\sa			jobSubName
			\return		<str>
		"""
		return self._jobName
	
	def jobSubName( self ):
		"""
			\remarks	return sub-job names for this farm job that will be created.  If this is set, then the name of the job will be
						[JobName]_[JobSubName], otherwise it will be [JobName]
			\sa			jobName
			\return		<str>
		"""
		return self._jobSubName
	
	def jobType( self ):	
		"""
			\remarks	return the job type that is associated with this submitter, this can be automatically set by using the
						setSubmitType method, and is done on initialization of the class.  You can override the default submiType's
						jobType with the setJobType method
			\sa			submitType, setSubmitType
			\return		<str>
		"""
		return self._jobType
	
	def maxTaskTime( self ):
		"""
			\remarks	return the number of seconds an individual frame should be allowed to process on the farm before triggering an error.
			\warning	this value will only be utilized if you have useMaxTaskTime set to True
			\return		<int> seconds
		"""
		return self._maxTaskTime
	
	def notifyOnComplete( self ):
		"""
			\remarks	return the prefrences set for the notify on complete option from the submission
			\return		<blur3d.constants.NotifyType>
		"""
		return self._notifyOnComplete
	
	def notifyOnError( self ):
		"""
			\remarks	return the preferences set for the notify on error option from the submission
			\return		<blur3d.constants.NotifyType>
		"""
		return self._notifyOnError
	
	def packetSize( self ):
		"""
			\remarks	return the packet size that will be used if the autoPacketSize is turned off for submission
			\return		<int>
		"""
		return self._packetSize
	
	def packetType( self ):
		"""
			\remarks	return the packet type that will be used for this submission
			\return		<str>	('sequential' || 'random')
		"""
		return self._packetType
	
	def proxyFPS( self ):
		"""
			\remarks	return the frames-per-second value that will be used for the proxy job that will be created from this submission
						if the CreateProxyJob flag is set in the submitFlags() for this submission.  If that flag is not set, then this 
						method will not be used
			\sa			submitFlags, proxyType
			\warning	this property is only used during processing, and is not actually a property on a farm job
			\return		<float>
		"""
		return self._proxyFPS
	
	def proxyType( self ):
		"""
			\remarks	return the current proxy setting for the submission.  If this property is set and the CreateProxyJob submit flag is set,
						then a second job will be created and submitted to take the result from the frames output and use it to create a proxy
						job
			\warning	this property is only used during processing, and is not actually a property on a farm job
			\return		<blur3d.constants.ProxyType>
		"""
		return self._proxyType
	
	def prioritizeOuterFrames( self ):
		"""
			\remarks	return whether or not the submission job will process the first and last frames of the job before processing the other
						frames
			\return		<bool>
		"""
		return self._prioritizeOuterFrames
	
	def projectName( self ):
		"""
			\remarks	return the name of a project that this submission will be associated with
			\return		<str>
		"""
		return self._projectName
	
	def priority( self ):
		"""
			\remarks	return the job priority that will be given to this submission
			\return		<int> priority
		"""
		return self._priority
	
	def recordXml( self, xml ):
		"""
			\remarks	define a way to record this controller to xml
			\param		xml		<blurdev.XML.XMLElement>
			\return		<bool> success
		"""
		xml.setAttribute( 'type', 					self.submitType() )
		xml.setProperty( 'jobName', 				self._jobName )
		xml.setProperty( 'fileOriginal',		 	self._fileOriginal )
		xml.setProperty( 'fileName',				self._fileName )
		xml.setProperty( 'jobSubName',				self._jobSubName )
		xml.setProperty( 'projectName',				self._projectName )
		xml.setProperty( 'username',				self._username )
		xml.setProperty( 'hostname',				self._hostname )
		xml.setProperty( 'frameList',				self._frameList )
		xml.setProperty( 'packetType',				self._packetType )
		xml.setProperty( 'hostnames',				';'.join(self._hostNames) )
		xml.setProperty( 'services',				';'.join(self._serviceNames) )
		xml.setProperty( 'renderElements',			';'.join(self._renderElements) )
		xml.setProperty( 'cameras',					';'.join(self._cameras) )
		xml.setProperty( 'autoPacketSize',			self._autoPacketSize )
		xml.setProperty( 'deleteJobOnComplete',		self._deleteJobOnComplete )
		xml.setProperty( 'prioritizeOuterFrames',	self._prioritizeOuterFrames )
		xml.setProperty( 'useFrameNth',				self._useFrameNth )
		xml.setProperty( 'invertFrameNth',			self._invertFrameNth )
		xml.setProperty( 'useMaxTaskTime',			self._useMaxTaskTime )
		xml.setProperty( 'maxTaskTime',				self._maxTaskTime )
		xml.setProperty( 'frameNth',				self._frameNth )
		xml.setProperty( 'packetSize',				self._packetSize )
		xml.setProperty( 'priority',				self._priority )
		xml.setProperty( 'notifyOnError',			self._notifyOnError )
		xml.setProperty( 'notifyOnComplete',		self._notifyOnComplete )
		xml.setProperty( 'submitFlags',				self._submitFlags )
		xml.setProperty( 'proxyType',				self._proxyType )
		xml.setProperty( 'proxyFPS',				self._proxyFPS )
		
		xml.recordProperty( 'customArgs', self._customArgs )
	
	def renderElements( self ):
		"""
			\remarks	return the list of render elements that this submission should load before submitting.  when there are elements provided, then
						there will be multiple jobs created, one per element and submitted to the farm individually
			\warning	this property is only used during processing, and is not actually a property on a farm job
			\warning	this is considered legacy support - # EKH 03/21/11
			\return		<list> [ <str> filename, .. ]
		"""
		return self._renderElements
	
	def reset( self ):
		"""
			\remarks	[virtual] this method will be called to reset the arguments for this submission to their default mode
		"""
		self._customArgs.clear()
		
		# reset scripting args
		from blur3d.constants import SubmitType
		if ( self.submitType() == SubmitType.Script ):
			self.setCustomArg( 'runPythonScript', 	True )
			self.setCustomArg( 'run64Bit', 			False )
			self.setCustomArg( 'silent',			True )
			self.setCustomArg( 'script',			'' )
			self.setFrameList( '1' )
	
	def saveXml( self, filename ):
		"""
			\remarks	saves out an XML description of this submitter to the inputed filename
			\param		filename	<str>
			\return		<bool> success
		"""
		from blurdev.XML import XMLDocument
		doc = XMLDocument()
		node = doc.addNode( 'submitter' )
		self.recordXml(node)
		return doc.save(filename)
	
	def services( self ):
		"""
			\remarks	return a list of the service records that will be used by this submission by looking up the database records using
						the service names set on this instance
			\sa			serviceNames, setServices, setServiceNames
			\return		<list> [ <trax.api.data.Service>, .. ]
		"""
		if ( not self._serviceNames ):
			return []
		
		from blurdev import debug
		try:
			import trax.api
		except:
			debug.debugObject( self.services, 'trax package is not installed.' )
			return []
		
		return list(trax.api.data.Service.select( 'service IN (%s)' % ( ','.join( [ "'%s'" % servicename for servicename in self._serviceNames ] ) ) ))
	
	def serviceNames( self ):
		"""
			\remarks	return a list of the service names that are linked to this submission instance
			\sa			services, setServices, setServiceNames
			\return		<list> [ <str>, .. ]
		"""
		return self._serviceNames
	
	def setAdditionalFiles( self, filenames ):
		"""
			\remarks	set the list of additional filenames that will be used when packaging this job for submission
			\param		filenames	<list> [ <str> filename, .. ]
		"""
		self._additionalFiles = filenames
			
	def setAutoPacketSize( self, state = True ):
		"""
			\remarks	set whether or not this submitter should automatically determine the packet size when submitting
			\param		state	<bool>
		"""
		self._autoPacketSize = state
	
	def setCameras( self, cameras ):
		"""
			\remarks	set the cameras that will need to be processed for this submitter, allowing for mult-shot processing from a single
						submission job
			\param		cameras		<list> [ <blur3d.api.SceneCamera>, .. ]
		"""
		self._cameras = cameras
	
	def setCurrentRenderElement( self, renderElement ):
		"""
			\remarks	[abstract] set the current render element in the scene to the inputed element
			\warning	this is considered legacy support - # EKH 03/21/11
			\param		renderElement	<str> filename
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError

		return False
	
	def setCustomArg( self, key, value ):
		"""
			\remarks	set the custom argument's value to the inputed key
			\param		key		<str>
			\param		value	<variant>
		"""
		self._customArgs[str(key)] = value
	
	def setCustomArgs( self, args ):
		"""
			\remarks	set the whole custom argument dictionary to the inputed args
			\param		args	<dict> { <str> key: <variant> value, .. }
		"""
		self._customArgs = args
	
	def setDeleteJobOnComplete( self, state = True ):
		"""
			\remarks	set whether or not to delete this job from the farm automatically when it completes
			\param		state	<bool>
		"""
		self._deleteJobOnComplete = state
	
	def setFileOriginal( self, filename ):
		"""
			\remarks	sets the source filename for this job submission
			\sa			fileOriginal
			\param		filename	<str>
		"""
		self._fileOriginal = filename
	
	def setFileName( self, filename ):
		"""
			\remarks	set the filename that will be used when submitting to the farm
			\param		filename	<str>
		"""
		self._filename = filename
	
	def setFrameList( self, frameList ):
		"""
			\remarks	set the list of frames to be processed for this submission
			\param		frameList	<str>
		"""
		self._frameList = frameList
	
	def setFrameNth( self, frameNth ):
		"""
			\remarks	set the number of frames that should be alternated when using the frame Nth submission option
			\param		frameNth	<int>
		"""
		self._frameNth = frameNth
	
	def setHostname( self, hostname ):
		"""
			\remarks	set the hostname for this submission instance
			\param		hostname	<str> hostname
		"""
		return self._hostname
	
	def setHostNames( self, hostnames ):
		"""
			\remarks	set the host names list that will be used on submission to the inputed list of host names
			\sa			hosts, hostNames, setHosts
			\param		hostnames	<list> [ <str>, .. ]
		"""
		self._hostNames = [ str(hostname) for hostname in hostnames ]
	
	def setHosts( self, hosts ):
		"""
			\remarks	set the host list that will be used on submission to the inputed list of hosts.  This method is a wrapper on top of the
						setHostNames method
			\sa			hosts, hostNames, setHostNames
			\param		hosts	<list> [ <trax.api.data.Host>, .. ]
		"""
		self._hostNames = [str(host.name()) for host in hosts]
	
	def setInvertFrameNth( self, state = True ):
		"""
			\remarks	set whether or not the Nth frame value should be rendering the Nth frames (when False), or the
						frames BETWEEN the Nth frames (when True)
			\param		state	<bool>
		"""
		self._invertFrameNth = state
	
	def setJobName( self, text ):
		"""
			\remarks	set the job name that will be used for the farm job when it is created to the inputed text
			\param		text	<str>
		"""
		self._jobName = text
	
	def setJobSubName( self, text ):
		"""
			\remarks	set the job sub-name that will be used when building the farm job's name
			\sa			jobSubName, jobName
			\param		text	<str>
		"""
		self._jobSubName = text
	
	def setJobType( self, jobType ):
		"""
			\remarks	set the job type for this submitter to the inputed jobType record.  When this property is set, it will automatically call the
						reset method to setup the default arguments that are going to be used on a per job/submit type basis
			\sa			reset
			\param		jobType		<str>
		"""
		self._jobType = jobType
		self.reset()
	
	def setMaxTaskTime( self, maxTaskTime ):
		"""
			\remarks	sets the maximum task time to be used for a single frame to process when the job is running
			\sa			useMaxTaskTime
			\param		maxTaskTime		<int>	seconds
		"""
		self._maxTaskTime = maxTaskTime
	
	def setNotifyOnComplete( self, notifyType ):
		"""
			\remarks	set the completion notification preferences for this submission to the inputed type
			\param		notifyType	<blur3d.constants.NotifyType>
		"""
		self._notifyOnComplete = notifyType
	
	def setNotifyOnError( self, notifyType ):
		"""
			\remarks	set the error notification preferences for this submission to the inputed type
			\param		notifyType	<blur3d.constants.NotifyType>
		"""
		self._notifyOnError = notifyType
	
	def setPacketSize( self, packetSize ):
		"""
			\remarks	set the packet size that will be used if the autoPacketSize is turned off
			\sa			autoPacketSize, setAutoPacketSize
			\param		packetSize	<int>
		"""
		self._packetSize = packetSize
	
	def setPacketType( self, packetType ):
		"""
			\remarks	set the packet type that will be used for this submission
			\param		packetType	<str> ('sequential' || 'random')
		"""
		self._packetType = packetType
	
	def setPriority( self, priority ):
		"""
			\remarks	set the priority for the job to have when it is submitted
			\param		priority	<int>
		"""
		return self._priority
	
	def setPrioritizeOuterFrames( self, state = True ):
		"""
			\remarks	set whether or not the job should prioritize processing of the first and last frames before the inner frames
			\param		state	<bool>
		"""
		self._prioritizeOuterFrames = state
	
	def setProjectName( self, projectName ):
		"""
			\remarks	set the name of the project this submission should be associated with
			\param		projectName		<str>
		"""
		self._projectName = projectName
	
	def setProxyFPS( self, fps ):
		"""
			\remarks	set the frames-per-second value for the proxy job that will be created if the CreateProxyJob flag is set in the SubmitFlags
			\param		fps		<float>
		"""
		self._proxyFPS = fps
	
	def setProxyType( self, proxyType ):
		"""
			\remarks	set the proxy type to the inputed type.  if the ProxyType.Disabled value is supplied, then the SubmitFlags.CreateProxyJob
						will automatically be removed from the submission flags, otherwise, it will be added to the submission flags for this submit
			\param		proxyType	<blur3d.constants.ProxyType>
		"""
		self._proxyType = proxyType
		
		from blur3d.constants import ProxyType, SubmitFlags
		self.setSubmitFlag( SubmitFlags.CreateProxyJob, proxyType != ProxyType.Disabled )
	
	def setRenderElements( self, renderElements ):
		"""
			\remarks	set the render elements that will be processed and then submitted to the farm
			\warning	this is considered legacy support - # EKH 03/21/11
			\param		renderElements	<list> [ <str> filename, .. ]
		"""
		self._renderElements = renderElements
	
	def setServices( self, services ):
		"""
			\remarks	set the service list that will be used on submission to the inputed list of services.  This method is a wrapper
						on top of the setServiceNames method
			\sa			services, serviceNames, setServiceNames
			\param		services	<list> [ <trax.api.data.Service>, .. ]
		"""
		self._serviceNames = [ str(service.service()) for service in services ]
	
	def setServiceNames( self, servicenames ):
		"""
			\remarks	set the service name list that will be used on submission to the inputed list of service names
			\sa			services, serviceNames, setServices
			\param		servicenames	<list> [ <str> , .. ]
		"""
		self._serviceNames = [ str(servicename) for servicename in services ]
	
	def setSubmitFlag( self, flag, state = True ):
		"""
			\remarks	set the inputed submit flag to the given state
			\sa			submitFlags
			\param		flag			<blur3d.constants.SubmitFlag>
		"""
		# set the flag as active
		if ( state ):
			self._submitFlags |= flag
		
		# set the flag as inactive
		elif ( self._submitFlags & flag ):
			self._submitFlags ^= flag
	
	def setSubmitFlags( self, flags ):
		"""
			\remarks	set the submit flags for this submission to the inputed flags
			\param		flags	<blur3d.constants.SubmitFlag>
		"""
		self._submitFlags = flags
			
	def setSubmitType( self, submitType ):
		"""
			\remarks	set the generic submit type for this submitter to the inputed submitType.  This will call the setJobType method with the
						result of the defaultJobType() call to abstractly set the default job types per submit type
			\param		submitType		<blur3d.constants.SubmitType>
		"""
		self._submitType = submitType
		
		# initialize the job type and services
		jobtype = self.defaultJobType()
		
		self.setJobType( jobtype )
	
		# try to use trax to determine default services
		try:
			import trax.api
		except:
			self.setServices( [] )
			return
		
		service = trax.api.data.JobType.recordByName(jobtype).service()
		if ( service.isRecord() ):
			self.setServices( [ service ] )
	
	def setUseFrameNth( self, state = True ):
		"""
			\remarks	set whether or not the job is setup to moderate through the frames with a variable number
			\sa			frameNth, invertFrameNth
			\param		state	<bool>
		"""
		self._useFrameNth = state
	
	def setUseMaxTaskTime( self, state = True ):
		"""
			\remarks	set whether or not the max task time should be used for this submission.
			\param		state	<bool>
		"""
		self._useMaxTaskTime = state
	
	def setUsername( self, username ):
		"""
			\remarks	set the username for the user that is associated with this submission
			\param		username	<str>
		"""
		self._username = username
	
	def setupProgress( self, progress ):
		"""
			\remarks	setup the inputed multiprogress dialog for the different submission sections we'll be using
			\param		progress	<blurdev.gui.dialogs.multiprogressdialog.MultiProgressDialog>
		"""
		if ( self._progress ):
			return False
			
		from blur3d.constants import SubmitType, SubmitFlags
		
		sections = []
		
		# include the render submission settings
		if ( self.submitType() == SubmitType.Render ):
			if ( self.hasSubmitFlag( SubmitFlags.RemoteSubmit ) ):
				sections += SCRIPT_PROGRESS_SECTIONS
			else:
				sections += RENDER_PROGRESS_SECTIONS
		
		# include the script progress sections
		elif ( self.submitType() == SubmitType.Script ):
			sectiosn += SCRIPT_PROGRESS_SECTIONS
		
		sections += SUBMIT_PROGRESS_SECTIONS
		
		# add the sections
		for section in sections:
			progress.addSection( section )
		
		# create the connections
		scene = self.scene()
		scene.progressUpdated.connect( 	progress.sectionUpdated )
		scene.progressErrored.connect( 	progress.sectionErrored )
		scene.submitError.connect( 		progress.complete )
		scene.submitSuccess.connect(	progress.complete )
	
	def submit( self ):
		"""
			\remarks	processes all of the data stored in this instance and then submits the job to the farm.  While this method will
						return a bool 'success' value, it will only get so far as processing and actually submitting to the backend system.
						to get full responses from the backend system, you need to connect slots to the submitSucceeded and submitErrored signals
						from this submitter's scene
			\sa			submitRender, submitScript
			\return		<bool> success
		"""
		from blur3d.constants import SubmitType, SubmitFlags
		
		# make sure we have a valid job name and job type at least for this submission (required for all jobs)
		if ( not (self.jobName() and self.jobType()) ):
			scene.emitProgressErrored( 'Preparing to Submit', 'No job name and/or job type has been provided for submission.' )
			return False
		
		# submit a render job
		if ( self.submitType() == SubmitType.Render ):
			# create a remote submission
			if ( self.hasSubmitFlag( SubmitFlags.RemoteSubmit ) ):
				return self._submitRemoteRender()
			
			# create an element submission
			elif ( self.renderElements() ):
				return self._submitRenderElements()
			
			# otherwise, perform a standard render element submission
			else:
				return self._submitRender()
		
		# submit a script job
		elif ( self.submitType() == SubmitType.Script ):
			return self._submitScript()
	
	def submitFlags( self ):
		"""
			\remarks	return the submit flags that are currently set for this submission
			\warning	this property is only used during processing, and is not actually a property on a farm job
			\return		<blur3d.constants.SubmitFlag>
		"""
		return self._submitFlags
	
	def submitType( self ):
		"""
			\remarks	return the submit type for this submitter
			\return		<blur3d.constants.SubmitType>
		"""
		return self._submitType
	
	def useMaxTaskTime( self ):
		"""
			\remarks	return whether or not the max task time should be used for this submission.
			\sa			maxTaskTime
			\return		<bool>
		"""
		return self._useMaxTaskTime
	
	def useFrameNth( self ):
		"""
			\remarks	return whether or not the ability to mod through frames is enabled for this job submission
			\return		<bool>
		"""
		return self._useFrameNth
	
	def username( self ):
		"""
			\remarks	return the username that is going to be created with this submitter
			\warning	this property is set to the logged in user by default
			\return		<str>
		"""
		return self._username
	
	def writeInfoFile( self, path ):
		"""
			\remarks	records the submission information to the inputed path
			\param		path	<str>
			\return		<bool>
		"""
		import os.path
		path = os.path.split( str(path) )[0]
		if ( path and os.path.exists(path) ):
			from PyQt4.QtCore import QDateTime
			fname = path + '/Render History Info.txt'
	
			# create the data for the file
			lines = [ '\n\n--------------------------------------------------------------------' ]
			lines.append( 'time:		%s' % QDateTime.currentDateTime().toString( 'M/d/yyyy h:mm:ss AP' ) )
			lines.append( 'from:		%s' % self.hostname() )
			lines.append( 'by:		%s' % self.username() )
			lines.append( 'max file:	%s' % self.fileOriginal() )
			lines.append( 'frames:		%s' % self.frameList() )
			lines.append( 'camera:		%s' % self.customArg( 'camera', '' ) )
			lines.append( 'net job name:	%s' % self.jobName() )
			lines.append( '--------------------------------------------------------------------' )
				
			# append to the existing file
			f = open( fname, 'a' )
			f.write( '\n'.join( lines ) )
			f.close()
		else:
			print '%s does not exist, cannot write history file' % path
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												static/class methods
	#------------------------------------------------------------------------------------------------------------------------
	@classmethod
	def fromXml( cls, scene, xml ):
		"""
			\remarks	implements AbstractSceneWrapper.fromXml method to create a new wrapper instance from the inputed xml data
			\param		scene	<blur3d.api.Scene>
			\param		xml		<blurdev.XML.XMLElement>
			\return		<blur3d.api.SceneSubmitter> || None
		"""
		if ( xml.nodeName != 'submitter' ):
			return None
			
		from blur3d.api 		import SceneSubmitter
		from blur3d.constants 	import SubmitType
		
		submitter = SceneSubmitter( scene, int(xml.attribute('type',0)) )
		
		# restore settings
		submitter._jobName 				= xml.findProperty('jobName')
		submitter._fileOriginal			= xml.findProperty('fileOriginal')
		submitter._fileName				= xml.findProperty('fileName')
		submitter._jobSubName			= xml.findProperty('jobSubName')
		submitter._projectName			= xml.findProperty('projectName')
		submitter._username				= xml.findProperty('username')
		submitter._hostname				= xml.findProperty('hostname')
		submitter._frameList			= xml.findProperty('frameList')
		submitter._packetType			= xml.findProperty('packetType')
		submitter._hostNames			= xml.findProperty('hostnames').split(';')
		submitter._serviceNames			= xml.findProperty('services').split(';')
		submitter._renderElements		= xml.findProperty('renderElements').split(';')
		submitter._cameras				= xml.findProperty('cameras').split(';')
		
		submitter._autoPacketSize			= xml.findProperty('autoPacketSize') != 'False'
		submitter._deleteJobOnComplete		= xml.findProperty('deleteJobOnComplete') == 'True'
		submitter._prioritizeOuterFrames	= xml.findProperty('prioritizeOuterFrames') == 'True'
		submitter._useFrameNth				= xml.findProperty('useFrameNth') == 'True'
		submitter._invertFrameNth			= xml.findProperty('invertFrameNth') == 'True'
		submitter._useMaxTaskTime			= xml.findProperty('useMaxTaskTime') == 'True'
		
		submitter._maxTaskTime			= int(xml.findProperty('maxTaskTime',90*60))
		submitter._frameNth				= int(xml.findProperty('frameNth',0))
		submitter._packetSize			= int(xml.findProperty('packetSize',0))
		submitter._priority				= int(xml.findProperty('priority',50))
		submitter._notifyOnError		= int(xml.findProperty('notifyOnError',0))
		submitter._notifyOnComplete		= int(xml.findProperty('notifyOnComplete',0))
		submitter._submitFlags			= int(xml.findProperty('submitFlags',0))
		submitter._proxyType			= int(xml.findProperty('proxyType',0))
		submitter._proxyFPS				= float(xml.findProperty('proxyFPS',0.0))
		
		submitter._customArgs			= xml.restoreProperty( 'customArgs' )
		
		return submitter
	
	@classmethod
	def loadXml( cls, scene, filename ):
		"""
			\remarks	loads the submitter from the xml file for the inputed scene
			\param		scene		<blur3d.api.Scene>
			\param		filename	<str>
			\return		<blur3d.api.SceneSubmitter> || None
		"""
		from blurdev.XML import XMLDocument
		doc = XMLDocument()
		if ( doc.load(filename) ):
			return cls.fromXml( scene, doc.root() )
		return None
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneSubmitter', AbstractSceneSubmitter, ifNotFound = True )
