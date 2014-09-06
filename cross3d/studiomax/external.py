##
#   :namespace  blur3d.api.studiomax.external
#
#   :remarks    This class can be used even outside of studiomax. It gives you info on where
#				studiomax is installed, and allows you to run scripts in studiomax.
#				To Access this class use: blur3d.api.external('studiomax')
#   
#   :author     mikeh@blur.com
#   :author     Blur Studio
#   :date       09/03/14
#

import os
import subprocess

from blur3d.api import Exceptions
from blur3d.constants import ScriptLanguage
from blur3d.api.abstract.external import External as AbstractExternal

#------------------------------------------------------------------------------------------------------------------------

class External(AbstractExternal):
	
	_hkeyBase = r'Software\Autodesk\3dsMax'
	_ignoredVersions = set(os.environ.get('BDEV_STUDIO_IGNORED_STUDIOMAX', '2011,2013,2015').split(','))
	# map years to version numbers
	_versionForYear = {'2008': '10', '2009': '11', '2010': '12', '2011': '13', '2012': '14', 
						'2013': '15', '2014': '16', '2015': '17'}
	_yearForVersion = dict((v, k) for k,v in _versionForYear.iteritems())

	@classmethod
	def getFileVersion(cls, filepath):
		"""
			Reads the max version that a max file was saved with from a custom 
			dso property added to the file when it is saved from max.
		"""

		# TODO: This was move here, otherwise this top import causes an error in MotionBuilder.
		from blurdev.media import dsofile

		dso = dsofile.DSOFile()
		try:
			dso.open(filepath)
			saved_as_version = dso.customProperty('SavedAsVersion')
			if saved_as_version:
				return saved_as_version.value()
		except:
			raise
		return None
	
	@classmethod
	def runScript(cls, script, version=None, architecture=64, language=ScriptLanguage.Python, debug=False):

		if os.path.exists(script):
			scriptPath = script

		else:
			scriptPath = cls.scriptPath()
			with open(scriptPath, "w") as fle:
				fle.write(script)

		if language == ScriptLanguage.Python:
			scriptTemplate = os.path.join(os.path.dirname(__file__), 'templates', 'external_python_script.mstempl')

			with open(scriptTemplate) as fle:
				script = fle.read().format(scriptPath =scriptPath, debug=debug)
			
			scriptPath = os.path.splitext(cls.scriptPath())[0] + '.ms'

			with open(scriptPath, "w") as fle:
				fle.write(script)

		binary = os.path.join(cls.binariesPath(version, architecture), '3dsmax.exe')
		process = subprocess.Popen([binary, '-U', 'MAXScript', scriptPath], creationflags=subprocess.CREATE_NEW_CONSOLE, env=os.environ)

		# Checking the error in the log file.
		fle = open(cls.scriptLog())
		content = fle.read()

		return False if 'FATAL' in content else True

	@classmethod
	def scriptPath(cls):
		return r'C:\temp\studiomax_script.py'

	@classmethod
	def scriptLog(cls):
		return r'C:\temp\studiomax_script.log'

	@classmethod
	def _getHkey(cls, version, langId):
		# Max uses diffrent locations to store its install path
		if float(version) >= 15:
			return r'{hkeyBase}\{version}.0'.format(hkeyBase=cls._hkeyBase, version=version)
		return r'{hkeyBase}\{version}.0\MAX-1:{langId}'.format(hkeyBase=cls._hkeyBase, version=version, langId=langId[0])

	@classmethod
	def binariesPath(cls, version=None, architecture=64, language='English'):
		""" Finds the install path for various software installations. If version is None, the default
		it will return the latest installed version of the software. Raises blur3d.api.Exceptions.SoftwareNotInstalled
		if the software is not installed.
		:param version: The version of the software. Default is None
		:param architecture: The bit type to query the registry for(32, 64). Default is 64
		:param language: Optional language that may be required for specific softwares.
		"""
		langId = cls._languageIDs.get(language, cls._languageIDs['English'])
		hive = 'HKEY_LOCAL_MACHINE'
		# Ensure we get a valid version number
		version = cls._versionForYear.get(unicode(version), version)
		if version == None:
			# Get all of the installed versions so we can find the latest version.
			versions = set(cls._listRegKeys(hive, cls._hkeyBase, architecture=architecture))
			# Years to ignore isnt very useful, convert them to version numbers ('14.0').
			# This allows the environment variable to remain the same for all of the software implemntations
			ignoredVersions = set(['{}.0'.format(cls._versionForYear[year]) for year in cls._ignoredVersions if year in cls._versionForYear])
			for v in sorted(versions, reverse=True):
				if v in versions and v not in ignoredVersions:
					version = v.replace('.0', '')
					# Ignore all keys that don't store Installdir info.
					hkey = cls._getHkey(version, langId)
					try:
						ret = cls._registryValue(hive, hkey, 'Installdir', architecture)[0]
						if not ret:
							continue
					except WindowsError:
						continue
					break
		dispVersion = cls._yearForVersion.get(unicode(version), version)
		hkey = cls._getHkey(version, langId)
		try:
			ret = cls._registryValue(hive, hkey, 'Installdir', architecture)[0]
		except WindowsError:
			raise Exceptions.SoftwareNotInstalled('Studiomax', version=dispVersion, architecture=architecture, language=language)
		# If the version is not installed this will return '.', we want to return False.
		if ret:
			return os.path.normpath(ret)
		raise Exceptions.SoftwareNotInstalled('Studiomax', version=dispVersion, architecture=architecture, language=language)
