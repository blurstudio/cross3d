##
#	\namespace	cross3d.abstract.abstractscenesubmitter
#
#	\remarks	The AbstractSceneSubmitter class defines the way a scene will interact with the render farm when submitting jobs
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/18/11
#

import cross3d
from cross3d import SceneWrapper, abstractmethod


class AbstractSceneSubmitter(SceneWrapper):
	"""
	The SceneSubmitter class defines the way a scene will interact 
	with the render farm when submitting jobs
	"""
	__cache = []

	# define progress sections
	RENDER_PROGRESS_SECTIONS = ['Validating Scene', 'Pre-Processing Scene', 'Post-Processing Scene']
	SCRIPT_PROGRESS_SECTIONS = ['Preparing Script', 'Archiving Files']
	SUBMIT_PROGRESS_SECTIONS = ['Preparing to Submit', 'Submitted to Farm', 'Waiting for Response']


	# define submission scripts
	RemoteRenderScript = ''				# needs to be redefined in a subclass

	def __init__(self, scene, submitType):
		"""
		The submitter class does not take a native wrapper since it 
		techincally will live outside of the scene heirarchy and simply work 
		onto the scene itself.  We will provide the nativePointer for this 
		wrapper manually
		
		:param scene: :class:`cross3d.Scene`
		:param submitType: :data:`cross3d.constants.SubmitType`

		"""
		# initialize the SceneWrapper base class
		SceneWrapper.__init__(self, scene, None)

		# TODO: This class should not be using trax records, remove this or move it.
		from blur3d.pipe.cinematic.api import Scene
		# initialize the default job settings based on the scene
		element = scene.element()
		filename = scene.currentFileName()

		self._submitType = submitType

		import os.path, blur.Stone, socket
		if (filename):
			self._jobName = '.'.join(os.path.basename(filename).split('.')[:-1])
			self._fileOriginal = os.path.normpath(filename)
		else:
			self._jobName = ''
			self._fileOriginal = ''

		self._fileName = ''
		self._jobSubName = ''
		self._jobType = ''
		self._projectName = element.project().name()
		self._username = blur.Stone.getUserName()
		self._hostname = socket.gethostname()

		from cross3d.constants import NotifyType
		self._notifyOnError = NotifyType.Email
		self._notifyOnComplete = 0

		self._hostNames = []
		self._serviceNames = []
		self._priority = 50
		self._frameList = ''

		self._packetType = 'sequential'
		self._packetSize = 0
		self._autoPacketSize = True

		self._deleteJobOnComplete = False
		self._prioritizeOuterFrames = False

		self._useFrameNth = False
		self._frameNth = 0
		self._invertFrameNth = False

		self._useMaxTaskTime = False
		self._maxTaskTime = 90 * 60	# seconds, default is 90 minutes * 60 seconds/minute

		self._customArgs = {}

		# initialize non-job submitter settings
		from cross3d.constants import SubmitFlags, ProxyType

		self._submitFlags = SubmitFlags.Default
		self._proxyType = ProxyType.Disabled
		self._proxyFPS = 30.0
		self._renderElements = []
		self._cameras = []

		# THE FOLLOWING ARGUMENTS DO NOT NEED TO BE SAVED WITH XML DEFINITIONS, THEY ARE DEFINED ON THE FLY PROGRAMMATICALLY
		# define the argument normalization system
		self._argBooleans = self.customArgBooleans()
		self._argMapping = self.customArgMapping()
		self._additionalFiles = []							# used when creating a package for submission
		self._progress = None

		# set the submit type
		self.setSubmitType(submitType)

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	def _buildArgs(self):
		# initialize the custom arguments based on normalization and boolean definitions
		output = {}
		for key, value in self._customArgs.items():
			okey = self._argMapping.get(str(key), str(key))

			# by default, booleans need to be converted to integers for the submitter
			if (type(value) == bool and not key in self._argBooleans):
				output[okey] = int(value)
			else:
				output[okey] = value

		# create the standard args
		if (self._jobSubName):
			output['job'] = '%s_%s' % (self._jobName, self._jobSubName)
		else:
			output['job'] = self._jobName

		output['jobType'] = self._jobType
		output['fileOriginal'] = self._fileOriginal
		output['fileName'] = self._fileName
		output['user'] = self._username
		output['host'] = self._hostname
		output['projectName'] = self._projectName
		output['hostList'] = ','.join(self._hostNames)
		output['services'] = ','.join(self._serviceNames)
		output['priority'] = self._priority
		output['frameList'] = self._frameList
		output['packetType'] = self._packetType
		output['deleteOnComplete'] = int(self._deleteJobOnComplete)
		output['prioritizeOuterFrames'] = int(self._prioritizeOuterFrames)

		# create notification preferences
		if (self._username):
			u = self._username
			n = ''

			from cross3d.constants import NotifyType

			# define the complete notifications
			if (self._notifyOnComplete & NotifyType.Jabber):
				n += 'j'
			if (self._notifyOnComplete & NotifyType.Email):
				n += 'e'

			if (n):
				output['notifyOnComplete'] = '%s:%s' % (u, n)

			# define the error notifications
			if (self._notifyOnError & NotifyType.Jabber):
				n += 'j'
			if (self._notifyOnError & NotifyType.Email):
				n += 'e'

			if (n):
				output['notifyOnError'] = '%s:%s' % (u, n)

		# create the nth frame preferences
		if (self._useFrameNth):
			output['frameNth']		 = self._frameNth
			output['frameFill']		 = int(self._invertFrameNth)

		# create the max task time preferences
		if (self._useMaxTaskTime):
			output['maxtasktime']	 = self._maxTaskTime

		# create the packet size preferences
		if (not self._autoPacketSize):
			output['packetSize']	 = self._packetSize

		return dict([(key, str(value)) for key, value in output.items()])

	def _cache(self):
		"""
		The blur.Stone Submitter must remain in memory throughout the 
		submission process to be successful, so when it completes this 
		will add the pointer from the cache
		
		"""
		if (not self in AbstractSceneSubmitter.__cache):
			AbstractSceneSubmitter.__cache.append(self)

			if (self._nativePointer):
				# uncache the submitter when the submission completes
				self._nativePointer.submitSuccess.connect(self._uncache)
				self._nativePointer.submitError.connect(self._uncache)

	@abstractmethod
	def _prepareRenderSubmit(self):
		"""
		Provide any processing that needs to occur for a render submission, 
		by default, this method does nothing

		"""
		return True

	def _submit(self):
		"""
		Private method for actually performing the submission and caching
		
		.. warning::

		   This method should ONLY be called internally from this class
		   
		"""
		scene = self.scene()

		# initialize the submission system
		import blur.Stone
		from blur.absubmit import Submitter
		self._nativePointer = Submitter(scene)

		# create the submitter connections
		self._nativePointer.submitSuccess.connect(scene.emitSubmitSuccess)
		self._nativePointer.submitError.connect(scene.emitSubmitError)

		# collect all of the arguments that will be supplied for submission
		scene.emitProgressUpdated(self.SUBMIT_PROGRESS_SECTIONS[0], 100)
		self._nativePointer.applyArgs(self._buildArgs())
		scene.emitProgressUpdated(self.SUBMIT_PROGRESS_SECTIONS[1], 100)
		self._nativePointer.submit()

		if cross3d.debugLevel:
			self.saveXml('c:/temp/submission_settings.xml')

		if cross3d.debugLevel >= cross3d.constants.DebugLevels.Mid:
			self._nativePointer.waitForFinished()
		else:
			self._cache()

		return True

	def _submitRender(self):
		"""Submit the data for this submitter to the farm as a render job

		"""
		from cross3d.constants import SubmitFlags

		scene = self.scene()

		# record render submission information
		if (not self._prepareRenderSubmit()):
			scene.emitProgressErrored(self.RENDER_PROGRESS_SECTIONS[0], 'The submission data was not able to be saved properly.')
			return False

		# make sure we have a valid output path specified
		outputpath = self.customArg('outputPath')
		if (not outputpath):
			scene.emitProgressErrored(self.RENDER_PROGRESS_SECTIONS[0], 'There is no output path specified for this Render submission')
			return False

		scene.emitProgressUpdated(self.RENDER_PROGRESS_SECTIONS[0], 100)

		# delete old frames if necessary
		if (self.hasSubmitFlag(SubmitFlags.DeleteOldFrames)):
			self.deleteOldFrames(outputpath)

		scene.emitProgressUpdated(self.RENDER_PROGRESS_SECTIONS[1], 100)

		# submit the job
		self._submit()

		# record the info file if necessary
		if (self.hasSubmitFlag(SubmitFlags.WriteInfoFile)):
			self.writeInfoFile(outputpath)

		scene.emitProgressUpdated(self.RENDER_PROGRESS_SECTIONS[2], 100)

		return True

	def _submitRemoteRender(self):
		"""
		Creates a script job for a remote render submission based on
		this submitter

		"""
		from cross3d.constants import SubmitFlags, SubmitType

		scene = self.scene()

		# make sure this instance has a remote render script defined
		if (not self.RemoteRenderScript):
			scene.emitProgressErrored(self.SCRIPT_PROGRESS_SECTIONS[0], 'There is no remote render script defined.')
			return False

		# create the remote submission information
		submitter = self.scene().createSubmitter(SubmitType.Script)
		submitter.setCustomArg('code', self.RemoteRenderScript)

		# collect the additional files for the script submission
		filenames = []
		for filename in self.renderElements():
			filenames += [filename] + glob.glob(os.path.splitext(filename)[0] + '*.*')

		# create the xml definition file for this submitter
		submitterfile = 'c:/temp/submitter.xml'
		self.saveXml(submitterfile)
		filenames.append(submitterfile)

		submitter.setAdditionalFiles(filenames)

		# calculate the number of frames for the submission script as the number of render elements that need to be loaded
		num_elements = len(self.renderElements())
		if (num_elements > 1):
			submitter.setFrameList('1-%i' % num_elements)

			# if we are deleting hidden geometry, force the packet size to 1
			if (self.hasSubmitFlag(SubmitFlags.DeleteHiddenGeometry)):
				submitter.setPacketSize(1)

			# otherwise, set the packet size as the length of the elements
			else:
				submitter.setPacketSize(num_elements)

		return submitter.submit()

	def _submitScript(self):
		"""
		Submits the data from this scene submitter to the farm as a script job

		"""
		import os
		scene = self.scene()
		scriptFile = self.fileName()

		# use the script file for submission
		if (not os.path.exists(scriptFile)):
			scene.emitProgressErrored(self.SCRIPT_PROGRESS_SECTIONS[0], 'The script file (%s) does not exist for submission' % scriptFile)
			return False

		# create the submission package
		if (self._additionalFiles):
			temparchivefile = 'c:/temp/archive.zip'

			try:
				if (os.path.exists(temparchivefile)):
					os.remove(temparchivefile)
			except:
				scene.emitProgressErrored(self.SCRIPT_PROGRESS_SECTIONS[0], 'Could not remove the temporary archive location.')
				return False

			scene.emitProgressUpdated(self.SCRIPT_PROGRESS_SECTIONS[1], 100)

			from cross3d.migrate import zipper
			if (not zipper.packageFiles([scriptFile] + self._additionalFiles, temparchivefile)):
				scene.emitProgressErrored(self.SCRIPT_PROGRESS_SECTIONS[1], 'Could not package the files together')
				return False
			else:
				self.setFileName(temparchivefile)

		scene.emitProgressUpdated(self.SCRIPT_PROGRESS_SECTIONS[1], 100)

		# submit the script job
		return self._submit()

	def _uncache(self):
		"""
		The blur.Stone Submitter must remain in memory throughout the 
		submission process to be successful, so when it completes this 
		will remove the pointer from the cache
		
		"""
		# clear the submitter from memory
		scene			 = self._scene
		nativeSubmitter = self._nativePointer

		if (nativeSubmitter):
			# disconnect from the scene
			nativeSubmitter.submitError.disconnect(scene.emitSubmitError)
			nativeSubmitter.submitSuccess.disconnect(scene.emitSubmitSuccess)

			# clear the submitter from Qt's memory
			nativeSubmitter.setParent(None)
			nativeSubmitter.deleteLater()

		# remove the submitter
		self._nativePointer = None

		# remove the submitter from the cache
		if (self in AbstractSceneSubmitter.__cache):
			AbstractSceneSubmitter.__cache.remove(self)

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def additionalFiles(self):
		"""
		Return the list of additional files that will be packaged together 
		when creating a package for submission
		
		:return: list of filepaths
			
		"""


	def autoPacketSize(self):
		"""
		Return whether or not this submission should automatically 
		determine the packet size
		
		:return: bool

		"""
		return self._autoPacketSize

	def cameras(self):
		"""
		Return the list of cameras that should be used when processing this 
		submission.  if there are cameras associated with the submission, 
		then it will need to create multiple job submissions, one per 
		camera, for the farm
		
		.. warning::
		
		   This property is only used during processing, and is not actually 
		   a property on a farm job
		   
		:return: list of :class:`cross3d.SceneCamera` objects
		
		"""
		return self._cameras

	def customArgs(self):
		"""
		Return custom arguments that will be set based on the application 
		and job type that we are going to be using

		SubmitType.Render Args::
		
			deformMotionBlur		force2Sided				outputPath
			outputHeight			outputWidth				pass	
			renderer				renderAtmospherics		renderDisplacements			
			renderHidden			renderEffects			renderSuperBlack					
			useColorCheck			useDither256			useDither
			useFieldRender			useMotionBlur			useVideoPost
		
		SubmitType.Script Args::
			
			code					requiresUi				runPythonScript			
			run64Bit				script					silent
							
		:return: dict of key, value args
		
		"""
		return self._customArgs

	def customArg(self, key, default=None):
		"""
		Return the custom argument's value for the inputed key

		"""
		return self._customArgs.get(str(key), default)

	def customArgBooleans(self):
		"""
		Defines which keys from the customArgs dictionary should be 
		preserved as booleans and not converted to integers when the 
		submission arguments get generated
		
		:return: a list of strings
			
		"""
		return []

	def customArgMapping(self):
		"""
		Create a mapping between the abstracted custom arg keys that are 
		used with the cross3d system to the application/job specific 
		settings that are needed.  Not all arguements need to be converted, 
		as any argument that is not found will simply be ignored.  See 
		the customArgs method for a list of the abstract argument names to 
		be used when developing
		
		:return: <dict> { <str> blur3dArg: <str> jobArg, .. }

		"""
		return {}

	@abstractmethod
	def defaultJobType(self):
		"""
		Return the default job type for this submitter instance based on 
		the abstract submitType inputed.
		
		:param submitType: :class:`cross3d.constants.SubmitType1

		"""
		return ''

	def deleteOldFrames(self, path):
		"""Removes the frames at the inputed path

		"""
		import os, glob
		path = str(path).strip()
		if (not path):
			return False

		fpath = os.path.split(path)[0]
		if (not os.path.exists(fpath)):
			return False

		# ignore these file types when removing files
		ignore 	 = ('.txt', '.log',)

		import glob, os
		usespool	 = False
		files 		 = glob.glob(os.path.split(path)[0] + '/*.*')

		for file in files:
			if (os.path.splitext(file)[1] in ignore):
				continue
			try:
				os.remove(file)
			except:
				usespool = True

		# if we were unable to remove some of the files, use the backend spooler to force removal
		if (usespool):
			from trax.api import spool
			fname = os.path.split(path)[0] + '/*' + os.path.splitext(path)[1]
			spool.removeFiles(fname)

		return True

	def deleteJobOnComplete(self):
		"""Return whether or not the job should be deleted from the farm 
		automatically when it finishes

		"""
		return self._deleteJobOnComplete

	def fileOriginal(self):
		"""
		Return the original file name for this submitter.  This property 
		represents the source file that was used to submit the job to the 
		farm, not necessarily the actual file that was submitted as often 
		times there will be a temp file saved before submission

		"""
		return self._fileOriginal

	def frameList(self):
		"""
		Return the frame list that will be used to determine the number of 
		sub-tasks and/or frames that need to be processed when the job 
		submits to the farm
		
		.. warning::
		
		   This property cannot be left blank or the submission will fail

		"""
		return self._frameList

	def fileName(self):
		"""
		Return the name of the actual file being submitted to the farm.  
		If there is any temp saving that occurs during the submission process, 
		this is the value that will point to the actual file being copied for 
		use in the submit
		
		.. warning::
		
		   This parameter must be set or the job will not submit properly
		   
		"""
		return self._fileName

	def frameNth(self):
		"""
		Return the number of frames that should be alternated when using 
		the frameNth option on a job

		"""
		return self._frameNth

	def hasSubmitFlag(self, flag):
		"""
		Return whether or not the inputed submission flag is currently set 
		for this submitter
		
		:param flag: :data:`cross3d.constants.SubmitFlag`

		"""
		return (self._submitFlags & flag) != 0

	def hostname(self):
		"""
		Return the hostname that is associated with this submission

		"""
		return self._hostname

	def hostNames(self):
		"""
		Return the list of host names that this submitter will send the 
		job to.  if a blank list is used, then it will not specify any 
		particular hosts on submission
		
		:return: a list of strings
		
		"""
		return self._hostNames

	def hosts(self):
		"""
		Return the list of host records that this submitter will send the +
		job to.  if a blank list is used, then it will not specify any 
		particular hosts on submission.  This method is a wrapper on top of 
		the hostNames method to look up actual database records based on 
		the set host names list for this instance
		
		:return: list of :class:`trax.api.data.Host` objects
			
		"""
		if (not self._hostNames):
			return []

		try:
			import trax.api
		except:
			cross3d.logger.debug('trax package is not installed.')
			return []

		return trax.api.data.Host.select('name IN (%s)' % ','.join(["'%s'" % hostname for hostname in self._hostNames]))

	def invertFrameNth(self):
		"""
		Return whether or not the Nth frame value should be rendering +
		the Nth frames (when False), or the frames BETWEEN the Nth 
		frames (when True)

		"""
		return self._invertFrameNth

	def jobName(self):
		"""
		Return the name that will be used for the farm job when it is created

		"""
		return self._jobName

	def jobSubName(self):
		"""
		Return sub-job names for this farm job that will be created.  If 
		this is set, then the name of the job will be [JobName]_[JobSubName], 
		otherwise it will be [JobName]

		"""
		return self._jobSubName

	def jobType(self):
		"""
		Return the job type that is associated with this submitter, this 
		can be automatically set by using the setSubmitType method, and is 
		done on initialization of the class.  You can override the default 
		submiType's jobType with the setJobType method

		"""
		return self._jobType

	def maxTaskTime(self):
		"""
		Return the number of seconds an individual frame should be 
		allowed to process on the farm before triggering an error.
		
		.. warning::
		
		   This value will only be utilized if you have useMaxTaskTime set 
		   to True

		:return: seconds
		:rtype: int

		"""
		return self._maxTaskTime

	def notifyOnComplete(self):
		"""
		Return the prefrences set for the notify on complete option from 
		the submission
		
		:return: :data:`cross3d.constants.NotifyType`
		
		"""
		return self._notifyOnComplete

	def notifyOnError(self):
		"""
		Return the preferences set for the notify on error option from 
		the submission
		
		:return: :data:`cross3d.constants.NotifyType`
		
		"""
		return self._notifyOnError

	def packetSize(self):
		"""
		Return the packet size that will be used if the autoPacketSize is 
		turned off for submission
		
		:rtype: int
		
		"""
		return self._packetSize

	def packetType(self):
		"""
		Return the packet type that will be used for this submission
		
		:return: "sequential" or "random"
		:rtype: str
			
		"""
		return self._packetType

	def proxyFPS(self):
		"""
		Return the frames-per-second value that will be used for the proxy 
		job that will be created from this submission if the CreateProxyJob 
		flag is set in the submitFlags() for this submission.  If that 
		flag is not set, then this method will not be used
		
		.. warning::
		
		   this property is only used during processing, and is not actually 
		   a property on a farm job
		   
		:return: float
		
		"""
		return self._proxyFPS

	def proxyType(self):
		"""
		Return the current proxy setting for the submission.  If this 
		property is set and the CreateProxyJob submit flag is set, then a 
		second job will be created and submitted to take the result from 
		the frames output and use it to create a proxy job
		
		.. warning::
		
		   This property is only used during processing, and is not 
		   actually a property on a farm job
		   
		:return: :data:`cross3d.constants.ProxyType`
		
		"""
		return self._proxyType

	def prioritizeOuterFrames(self):
		"""
		Return whether or not the submission job will process the first and 
		last frames of the job before processing the other frames

		"""
		return self._prioritizeOuterFrames

	def projectName(self):
		"""
		Return the name of a project that this submission will be 
		associated with

		"""
		return self._projectName

	def priority(self):
		"""
		Return the job priority that will be given to this submission
		
		:return: int
		
		"""
		return self._priority

	def recordXml(self, xml):
		"""
		Define a way to record this controller to xml
		
		:param xml: :class:`cross3d.migrate.XMLElement`

		"""
		xml.setAttribute('type', 					self.submitType())
		xml.setProperty('jobName', 				self._jobName)
		xml.setProperty('fileOriginal', 		 	self._fileOriginal)
		xml.setProperty('fileName', 				self._fileName)
		xml.setProperty('jobSubName', 				self._jobSubName)
		xml.setProperty('projectName', 				self._projectName)
		xml.setProperty('username', 				self._username)
		xml.setProperty('hostname', 				self._hostname)
		xml.setProperty('frameList', 				self._frameList)
		xml.setProperty('packetType', 				self._packetType)
		xml.setProperty('hostList', 				';'.join(self._hostNames))
		xml.setProperty('services', 				';'.join(self._serviceNames))
		xml.setProperty('renderElements', 			';'.join(self._renderElements))
		xml.setProperty('cameras', 					';'.join(self._cameras))
		xml.setProperty('autoPacketSize', 			self._autoPacketSize)
		xml.setProperty('deleteJobOnComplete', 		self._deleteJobOnComplete)
		xml.setProperty('prioritizeOuterFrames', 	self._prioritizeOuterFrames)
		xml.setProperty('useFrameNth', 				self._useFrameNth)
		xml.setProperty('invertFrameNth', 			self._invertFrameNth)
		xml.setProperty('useMaxTaskTime', 			self._useMaxTaskTime)
		xml.setProperty('maxTaskTime', 				self._maxTaskTime)
		xml.setProperty('frameNth', 				self._frameNth)
		xml.setProperty('packetSize', 				self._packetSize)
		xml.setProperty('priority', 				self._priority)
		xml.setProperty('notifyOnError', 			self._notifyOnError)
		xml.setProperty('notifyOnComplete', 		self._notifyOnComplete)
		xml.setProperty('submitFlags', 				self._submitFlags)
		xml.setProperty('proxyType', 				self._proxyType)
		xml.setProperty('proxyFPS', 				self._proxyFPS)

		xml.recordProperty('customArgs', self._customArgs)

	def renderElements(self):
		"""
		Return the list of render elements that this submission should load 
		before submitting.  when there are elements provided, then there 
		will be multiple jobs created, one per element and submitted to 
		the farm individually
		
		.. warning::
		
		   This property is only used during processing, and is not actually 
		   a property on a farm job
		   
		   This is considered legacy support
		   
		:return: a list of filenames

		"""
		return self._renderElements

	def reset(self):
		"""
		This method will be called to reset the arguments for this 
		submission to their default mode
		
		"""
		self._customArgs.clear()

		# reset scripting args
		from cross3d.constants import SubmitType
		if (self.submitType() == SubmitType.Script):
			self.setCustomArg('runPythonScript', 	True)
			self.setCustomArg('run64Bit', 			False)
			self.setCustomArg('silent', 			True)
			self.setCustomArg('script', 			'')
			self.setFrameList('1')
			self.setPriority(10)

			# temp for testing - # EKH 03/25/11
			self.setHostNames(['sentinel039'])

	def saveXml(self, filename):
		"""
		Saves out an XML description of this submitter to the inputed filename

		"""
		doc = cross3d.migrate.XMLDocument()
		node = doc.addNode('submitter')
		self.recordXml(node)
		return doc.save(filename)

	def services(self):
		"""
		Return a list of the service records that will be used by this 
		submission by looking up the database records using the service 
		names set on this instance
		
		:return: a list of :class:`trax.api.data.Service` records

		"""
		if (not self._serviceNames):
			return []

		try:
			import trax.api
		except:
			cross3d.logger.debug('trax package is not installed.')
			return []

		return list(trax.api.data.Service.select('service IN (%s)' % (','.join(["'%s'" % servicename for servicename in self._serviceNames]))))

	def serviceNames(self):
		"""
		Return a list of the service names that are linked to this 
		submission instance
		
		:return: a list of strings
		
		"""
		return self._serviceNames

	def setAdditionalFiles(self, filenames):
		"""
		Set the list of additional filenames that will be used when 
		packaging this job for submission
		
		:param filenames: a list of filepaths
		
		"""
		self._additionalFiles = filenames

	def setAutoPacketSize(self, state=True):
		"""
		Set whether or not this submitter should automatically determine 
		the packet size when submitting
		
		"""
		self._autoPacketSize = state

	def setCameras(self, cameras):
		"""
		Set the cameras that will need to be processed for this 
		submitter, allowing for mult-shot processing from a single 
		submission job
		
		:param cameras: a list of :class:`cross3d.SceneCamera` objects
		
		"""
		self._cameras = cameras

	@abstractmethod
	def setCurrentRenderElement(self, renderElement):
		"""
		Set the current render element in the scene to the inputed element

		.. warning::
		
		   This is considered legacy support - # EKH 03/21/11

		"""
		return False

	def setCustomArg(self, key, value):
		"""
		Set the custom argument's value to the inputed key

		"""
		self._customArgs[str(key)] = value

	def setCustomArgs(self, args):
		"""
		Set the whole custom argument dictionary to the inputed args
		
		:param args: <dict> { <str> key: <variant> value, .. }

		"""
		self._customArgs = args

	def setDeleteJobOnComplete(self, state=True):
		"""
		Set whether or not to delete this job from the farm 
		automatically when it completes

		"""
		self._deleteJobOnComplete = state

	def setFileOriginal(self, filename):
		"""
		Sets the source filename for this job submission

		"""
		self._fileOriginal = filename

	def setFileName(self, filename):
		"""
		Set the filename that will be used when submitting to the farm

		"""
		self._fileName = filename

	def setFrameList(self, frameList):
		"""
		Set the list of frames to be processed for this submission

		"""
		self._frameList = frameList

	def setFrameNth(self, frameNth):
		"""
		Set the number of frames that should be alternated when using the 
		frame Nth submission option
S
		"""
		self._frameNth = frameNth

	def setHostname(self, hostname):
		"""
		Set the hostname for this submission instance

		"""
		return self._hostname

	def setHostNames(self, hostnames):
		"""
		Set the host names list that will be used on submission to the 
		inputed list of host names

		"""
		self._hostNames = [str(hostname) for hostname in hostnames]

	def setHosts(self, hosts):
		"""
		Set the host list that will be used on submission to the inputed 
		list of hosts.  This method is a wrapper on top of the 
		setHostNames method
		
		:param hosts: a list of :class:`trax.api.data.Host` records

		"""
		self._hostNames = [str(host.name()) for host in hosts]

	def setInvertFrameNth(self, state=True):
		"""
		Set whether or not the Nth frame value should be rendering the 
		Nth frames (when False), or the frames BETWEEN the Nth frames 
		(when True)

		"""
		self._invertFrameNth = state

	def setJobName(self, text):
		"""
		Set the job name that will be used for the farm job when it is 
		created to the inputed text

		"""
		self._jobName = text

	def setJobSubName(self, text):
		"""
		Set the job sub-name that will be used when building the farm 
		job's name

		"""
		self._jobSubName = text

	def setJobType(self, jobType):
		"""
		Set the job type for this submitter to the inputed jobType record.  
		When this property is set, it will automatically call the 
		reset method to setup the default arguments that are going to be 
		used on a per job/submit type basis

		"""
		self._jobType = jobType
		self.reset()

	def setMaxTaskTime(self, maxTaskTime):
		"""
		Ssets the maximum task time to be used for a single frame to 
		process when the job is running
		
		:param maxTaskTime: seconds
		:type maxTaskTime: int

		"""
		self._maxTaskTime = maxTaskTime

	def setNotifyOnComplete(self, notifyType):
		"""
		Set the completion notification preferences for this submission
		to the inputed type
		 
		:param notifyType: :data:`cross3d.constants.NotifyType`
		
		"""
		self._notifyOnComplete = notifyType

	def setNotifyOnError(self, notifyType):
		"""
		Set the error notification preferences for this submission to the
		inputed type
		
		:param notifyType: :data:`cross3d.constants.NotifyType`
		
		"""
		self._notifyOnError = notifyType

	def setPacketSize(self, packetSize):
		"""
		Set the packet size that will be used if the autoPacketSize is 
		turned off
		
		:param packetSize: int
		
		"""
		self._packetSize = packetSize

	def setPacketType(self, packetType):
		"""
		Set the packet type that will be used for this submission
		
		:param packetType: "sequential" or "random"
			
		"""
		self._packetType = packetType

	def setPriority(self, priority):
		"""
		Set the priority for the job to have when it is submitted
		
		:param priority: int
			
		"""
		self._priority = priority

	def setPrioritizeOuterFrames(self, state=True):
		"""
		Set whether or not the job should prioritize processing of the 
		first and last frames before the inner frames

		"""
		self._prioritizeOuterFrames = state

	def setProjectName(self, projectName):
		"""
		Set the name of the project this submission should be associated with
S
		"""
		self._projectName = projectName

	def setProxyFPS(self, fps):
		"""
		Set the frames-per-second value for the proxy job that will be 
		created if the CreateProxyJob flag is set in the SubmitFlags
		
		:param fps: float
		
		"""
		self._proxyFPS = fps

	def setProxyType(self, proxyType):
		"""
		Set the proxy type to the inputed type.  if the ProxyType.Disabled 
		value is supplied, then the SubmitFlags.CreateProxyJob will 
		automatically be removed from the submission flags, otherwise, 
		it will be added to the submission flags for this submit
		
		:param proxyType: :data:`cross3d.constants.ProxyType`

		"""
		self._proxyType = proxyType

		from cross3d.constants import ProxyType, SubmitFlags
		self.setSubmitFlag(SubmitFlags.CreateProxyJob, proxyType != ProxyType.Disabled)

	def setRenderElements(self, renderElements):
		"""
		Set the render elements that will be processed and then 
		submitted to the farm
		
		:param renderElements: list of filenames
		
		.. warning::
		
		   This is considered legacy support - # EKH 03/21/11

		"""
		self._renderElements = renderElements

	def setServices(self, services):
		"""
		Set the service list that will be used on submission to the 
		inputed list of services.  This method is a wrapper on top of the 
		setServiceNames method
		
		:param services: list of :class:`trax.api.data.Service` records

		"""
		self._serviceNames = [str(service.service()) for service in services]

	def setServiceNames(self, servicenames):
		"""
		Set the service name list that will be used on submission to the 
		inputed list of service names
		
		:param servicenames: list of names

		"""
		self._serviceNames = [str(servicename) for servicename in servicenames]

	def setSubmitFlag(self, flag, state=True):
		"""
		Set the inputed submit flag to the given state
		
		:param flag: :data:`cross3d.constants.SubmitFlag`
		
		"""
		# set the flag as active
		if (state):
			self._submitFlags |= flag

		# set the flag as inactive
		elif (self._submitFlags & flag):
			self._submitFlags ^= flag

	def setSubmitFlags(self, flags):
		"""
		Set the submit flags for this submission to the inputed flags
			
		:param flags: :data:`cross3d.constants.SubmitFlag`
		
		"""
		self._submitFlags = flags

	def setSubmitType(self, submitType):
		"""
		Set the generic submit type for this submitter to the inputed +
		submitType.  This will call the setJobType method with the result 
		of the defaultJobType() call to abstractly set the default job 
		types per submit type
		
		:param submitType: :data:`cross3d.constants.SubmitType`

		"""
		self._submitType = submitType

		# initialize the job type and services
		jobtype = self.defaultJobType()

		self.setJobType(jobtype)

	def setUseFrameNth(self, state=True):
		"""
		Set whether or not the job is setup to moderate through the 
		frames with a variable number

		"""
		self._useFrameNth = state

	def setUseMaxTaskTime(self, state=True):
		"""
		Set whether or not the max task time should be used for this submission.
S
		"""
		self._useMaxTaskTime = state

	def setUsername(self, username):
		"""
		Set the username for the user that is associated with this submission
s
		"""
		self._username = username

	def setupProgress(self, progress):
		"""
		Setup the inputed multiprogress dialog for the different 
		submission sections we'll be using
		
		:param progress: :class:`blurdev.gui.dialogs.multiprogressdialog.MultiProgressDialog`
			
		"""
		if (self._progress):
			return False

		from cross3d.constants import SubmitType, SubmitFlags

		sections = []

		# include the render submission settings
		if (self.submitType() == SubmitType.Render):
			if (self.hasSubmitFlag(SubmitFlags.RemoteSubmit)):
				sections += self.SCRIPT_PROGRESS_SECTIONS
			else:
				sections += self.RENDER_PROGRESS_SECTIONS

		# include the script progress sections
		elif (self.submitType() == SubmitType.Script):
			sectiosn += self.SCRIPT_PROGRESS_SECTIONS

		sections += self.SUBMIT_PROGRESS_SECTIONS

		# add the sections
		for section in sections:
			progress.addSection(section)

		# create the connections
		scene = self.scene()
		scene.progressUpdated.connect(progress.sectionUpdated)
		scene.progressErrored.connect(progress.sectionErrored)
		scene.submitError.connect(progress.complete)
		scene.submitSuccess.connect(progress.complete)

	def submit(self):
		"""
		Processes all of the data stored in this instance and then 
		submits the job to the farm.  While this method will return a 
		bool 'success' value, it will only get so far as processing and 
		actually submitting to the backend system.  To get full responses 
		from the backend system, you need to connect slots to the 
		submitSucceeded and submitErrored signals from this submitter's scene

		"""
		from cross3d.constants import SubmitType, SubmitFlags

		# make sure we have a valid job name and job type at least for this submission (required for all jobs)
		if (not (self.jobName() and self.jobType())):
			self.scene.emitProgressErrored('Preparing to Submit', 'No job name and/or job type has been provided for submission.')
			return False

		# submit a render job
		if (self.submitType() == SubmitType.Render):
			# create a remote submission
			if (self.hasSubmitFlag(SubmitFlags.RemoteSubmit)):
				return self._submitRemoteRender()

			# create an element submission
			elif (self.renderElements()):
				return self._submitRenderElements()

			# otherwise, perform a standard render element submission
			else:
				return self._submitRender()

		# submit a script job
		elif (self.submitType() == SubmitType.Script):
			return self._submitScript()

	def submitFlags(self):
		"""
		Return the submit flags that are currently set for this submission
		
		:return: :data:`cross3d.constants.SubmitFlag`
		
		.. warning::
		
		   This property is only used during processing, and is not actually a property on a farm job
			
		"""
		return self._submitFlags

	def submitType(self):
		"""Return the submit type for this submitter+
		
		:return: :data:`cross3d.constants.SubmitType`
			
		"""
		return self._submitType

	def useMaxTaskTime(self):
		"""
		Return whether or not the max task time should be used for 
		this submission.
		
		"""
		return self._useMaxTaskTime

	def useFrameNth(self):
		"""
		Return whether or not the ability to mod through frames is 
		enabled for this job submission

		"""
		return self._useFrameNth

	def username(self):
		"""
		Return the username that is going to be created with this submitter
		
		.. warning::
		
		   This property is set to the logged in user by default

		"""
		return self._username

	def writeInfoFile(self, path):
		"""
		Records the submission information to the inputed path

		"""
		import os.path
		path = os.path.split(str(path))[0]
		if (path and os.path.exists(path)):
			from PyQt4.QtCore import QDateTime
			fname = path + '/Render History Info.txt'

			# create the data for the file
			lines = ['\n\n--------------------------------------------------------------------']
			lines.append('time:		%s' % QDateTime.currentDateTime().toString('M/d/yyyy h:mm:ss AP'))
			lines.append('from:		%s' % self.hostname())
			lines.append('by:		%s' % self.username())
			lines.append('max file:	%s' % self.fileOriginal())
			lines.append('frames:		%s' % self.frameList())
			lines.append('camera:		%s' % self.customArg('camera', ''))
			lines.append('net job name:	%s' % self.jobName())
			lines.append('--------------------------------------------------------------------')

			# append to the existing file
			f = open(fname, 'a')
			f.write('\n'.join(lines))
			f.close()
		else:
			print '%s does not exist, cannot write history file' % path

	#------------------------------------------------------------------------------------------------------------------------
	# 												static/class methods
	#------------------------------------------------------------------------------------------------------------------------
	@classmethod
	def fromXml(cls, scene, xml):
		"""
		Implements AbstractSceneWrapper.fromXml method to create a new
		wrapper instance from the inputed xml data
		
		:param scene: :class:`cross3d.Scene`
		:param xml: :class:`cross3d.migrate.XMLElement`
		:return: :class:`cross3d.SceneSubmitter` or None
		
		"""
		if (xml.nodeName != 'submitter'):
			return None

		from cross3d 		import SceneSubmitter
		from cross3d.constants 	import SubmitType

		submitter = SceneSubmitter(scene, int(xml.attribute('type', 0)))

		# restore settings
		submitter._jobName 				 = xml.findProperty('jobName')
		submitter._fileOriginal			 = xml.findProperty('fileOriginal')
		submitter._fileName				 = xml.findProperty('fileName')
		submitter._jobSubName			 = xml.findProperty('jobSubName')
		submitter._projectName			 = xml.findProperty('projectName')
		submitter._username				 = xml.findProperty('username')
		submitter._hostname				 = xml.findProperty('hostname')
		submitter._frameList			 = xml.findProperty('frameList')
		submitter._packetType			 = xml.findProperty('packetType')
		submitter._hostNames			 = xml.findProperty('hostnames').split(';')
		submitter._serviceNames			 = xml.findProperty('services').split(';')
		submitter._renderElements		 = xml.findProperty('renderElements').split(';')
		submitter._cameras				 = xml.findProperty('cameras').split(';')

		submitter._autoPacketSize			 = xml.findProperty('autoPacketSize') != 'False'
		submitter._deleteJobOnComplete		 = xml.findProperty('deleteJobOnComplete') == 'True'
		submitter._prioritizeOuterFrames	 = xml.findProperty('prioritizeOuterFrames') == 'True'
		submitter._useFrameNth				 = xml.findProperty('useFrameNth') == 'True'
		submitter._invertFrameNth			 = xml.findProperty('invertFrameNth') == 'True'
		submitter._useMaxTaskTime			 = xml.findProperty('useMaxTaskTime') == 'True'

		submitter._maxTaskTime			 = int(xml.findProperty('maxTaskTime', 90 * 60))
		submitter._frameNth				 = int(xml.findProperty('frameNth', 0))
		submitter._packetSize			 = int(xml.findProperty('packetSize', 0))
		submitter._priority				 = int(xml.findProperty('priority', 50))
		submitter._notifyOnError		 = int(xml.findProperty('notifyOnError', 0))
		submitter._notifyOnComplete		 = int(xml.findProperty('notifyOnComplete', 0))
		submitter._submitFlags			 = int(xml.findProperty('submitFlags', 0))
		submitter._proxyType			 = int(xml.findProperty('proxyType', 0))
		submitter._proxyFPS				 = float(xml.findProperty('proxyFPS', 0.0))

		submitter._customArgs			 = xml.restoreProperty('customArgs')

		return submitter

	@classmethod
	def loadXml(cls, scene, filename):
		"""
		Loads the submitter from the xml file for the inputed scene
		
		:param scene: :class:`cross3d.Scene`
		:param filename: filepath
		:return: :class:`cross3d.SceneSubmitter` or None
		"""
		doc = cross3d.migrate.XMLDocument()
		if (doc.load(filename)):
			return cls.fromXml(scene, doc.root())
		return None


# register the symbol
cross3d.registerSymbol('SceneSubmitter', AbstractSceneSubmitter, ifNotFound=True)
