##
#   :namespace  blur3d.api.maya.external
#
#   :remarks    This class can be used even outside of Maya. It gives you info on where
#				Maya is installed, and allows you to run scripts in Maya.
#				To Access this class use: blur3d.api.external('maya')
#   
#   :author     mikeh@blur.com
#   :author     Blur Studio
#   :date       09/10/14
#
#

import os
import re
import subprocess

from blur3d.api import Exceptions
from blur3d.constants import ScriptLanguage
from blur3d.api.abstract.external import External as AbstractExternal

class External(AbstractExternal):
	_hkeyBase = r'Software\Autodesk\Maya'
	# In case the software is installed but not used don't find it when not passing in a version
	_ignoredVersions = set(os.environ.get('BDEV_STUDIO_IGNORED_MAYA', '').split(','))
	# map years to version numbers. Maya doesnt use these anymore, add older versions if support is needed
	_yearForVersion = {}

	@classmethod
	def name(cls):
		return 'Maya'

	@classmethod
	def runScript(cls, script, version=None, architecture=64, language=ScriptLanguage.Python, debug=False, headless=True):

		# If the script argument is a path to a file.
		if os.path.exists(script):

			# If the language is MEL we just use the script as is.
			if language == ScriptLanguage.MEL:
				scriptPath = script

			# If the language is Python we parse the file to get the content.
			elif language == ScriptLanguage.Python:
				with open(script, 'r') as fle:
					script = fle.read()

		if language == ScriptLanguage.Python:
			scriptTemplate = os.path.join(os.path.dirname(__file__), 'templates', 'external_python_script.mstempl')
			pythonScritpPath = os.path.splitext(cls.scriptPath())[0] + '.py'

			with open(pythonScritpPath, 'w') as fle:
				fle.write(script)

			with open(scriptTemplate) as fle:
				script = fle.read().format(debug=unicode(debug).lower())
				
			scriptPath = os.path.splitext(cls.scriptPath())[0] + '.mel'
			with open(scriptPath, "w") as fle:
				fle.write(script)

		# TODO: Unforunately headless mode does not work for now.
		headless = False

		binary = os.path.join(cls.binariesPath(version, architecture), 'mayabatch.exe' if headless else 'maya.exe')
		print ' '.join([binary, '-script', scriptPath])
		process = subprocess.Popen([binary, '-script', scriptPath], creationflags=subprocess.CREATE_NEW_CONSOLE, env=os.environ)

		return True
		
		# TODO: This is the way to check for success. But it is blocking.
		# Check what Perry has done here \\source\source\dev\perry\winTest.py.
		# # Writing the log file.
		# fle = open(cls.scriptLog(), 'w')
		# fle.write(process.stdout.read())
		# fle.close()

		# # Checking the error in the log file.
		# fle = open(cls.scriptLog())
		# content = fle.read()

		# return False if 'FATAL' in content else True

	@classmethod
	def binariesPath(cls, version=None, architecture=64, language='English'):
		""" Finds the install path for various software installations.
		:param version: The version of the software. Default is None
		:param architecture: The bit type to query the registry for(32, 64). Default is 64
		:param language: Optional language that may be required for specific softwares.
		"""
		def buildHKey(version):
			return r'{hkeyBase}\{version}\Setup\InstallPath'.format(hkeyBase=cls._hkeyBase, version=version)
		version = cls._yearForVersion.get(unicode(version), version)
		hive = 'HKEY_LOCAL_MACHINE'
		valueName = 'MAYA_INSTALL_LOCATION'
		ret = None
		if version == None:
			# Get all of the installed versions so we can find the latest version.
			versions = cls._listRegKeys(hive, cls._hkeyBase, architecture=architecture)
			for v in sorted(versions, reverse=True):
				if v not in cls._ignoredVersions:
					hkey = buildHKey(v)
					try:
						ret = cls._registryValue(hive, hkey, valueName, architecture)[0]
					except WindowsError:
						continue
					if ret:
						version = v
						break
		else:
			hkey = buildHKey(version)
			try:
				ret = cls._registryValue(hive, hkey, valueName, architecture)[0]
			except WindowsError:
				raise Exceptions.SoftwareNotInstalled('Maya', version=version, architecture=architecture, language=language)
		# If the version is not installed this will return '.', we want to return False.
		if ret:
			return os.path.join(os.path.normpath(ret), 'bin')
		raise Exceptions.SoftwareNotInstalled('Maya', version=version, architecture=architecture, language=language)
