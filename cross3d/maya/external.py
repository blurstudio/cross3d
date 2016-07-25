##
#   :namespace  cross3d.maya.external
#
#   :remarks    This class can be used even outside of Maya. It gives you info on where
#				Maya is installed, and allows you to run scripts in Maya.
#				To Access this class use: cross3d.external('maya')
#   
#   :author     mikeh
#   :author     Blur Studio
#   :date       09/10/14
#
#

import os
import re
import subprocess

from cross3d import Exceptions
from cross3d.constants import ScriptLanguage
from cross3d.abstract.external import External as AbstractExternal

class External(AbstractExternal):
	_hkeyBase = r'Software\Autodesk\Maya'
	# In case the software is installed but not used don't find it when not passing in a version
	_ignoredVersions = set(os.environ.get('CROSS3D_STUDIO_IGNORED_MAYA', '2015').split(','))
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
			scriptTemplate = os.path.join(os.path.dirname(__file__), 'templates', 'external_python_script.meltempl')
			pythonScritpPath = os.path.splitext(cls.scriptPath())[0] + '.py'

			with open(pythonScritpPath, 'w') as fle:
				fle.write(script)

			with open(scriptTemplate) as fle:
				script = fle.read().format(debug=unicode(debug).lower())
				
			scriptPath = os.path.splitext(cls.scriptPath())[0] + '.mel'
			logPath = os.path.splitext(cls.scriptPath())[0] + '.log'
			with open(scriptPath, "w") as fle:
				fle.write(script)

		#--------------------------------------------------------------------------------
		# Developer's note: When running headless, these three messages are to be expected
		# I did my testing in Maya 2015 with Bonus Tools installed. The first two lines are because
		# bifrost doesn't properly check if it is in mayabatch mode. The third is because a script
		# in Bonus Tools also does not check if its in mayabatch mode.
		#--------------------------------------------------------------------------------
		# 1 error generated.
		# Error while processing C:\Program Files\Autodesk\Maya2015\plug-ins\bifrost\db\presets\__rootincludeall__.h.
		# Error: file: C:/ProgramData/Autodesk/ApplicationPlugins/MayaBonusTools/Contents/scripts-2015/bonusToolsMenu.mel line 1546: UI commands can't be run in batch mode.
		#--------------------------------------------------------------------------------

		binary = os.path.join(cls.binariesPath(version, architecture), 'mayabatch.exe' if headless else 'maya.exe')
		args = [binary, '-script', scriptPath, '-log', logPath]
		if debug and headless:
			# run mayabatch inside a cmd.exe prompt so you can see the output of mayabatch
			args = ['cmd.exe', '/k'] + args
		process = subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE, env=os.environ)

		# TODO: Need to figure out a way to return False if the script has failed.
		return True

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
		from cross3d.migrate import winregistry
		if version == None:
			# Get all of the installed versions so we can find the latest version.
			versions = winregistry.listRegKeys(hive, cls._hkeyBase, architecture=architecture)
			for v in sorted(versions, reverse=True):
				if v not in cls._ignoredVersions:
					hkey = buildHKey(v)
					try:
						ret = winregistry.registryValue(hive, hkey, valueName, architecture)[0]
					except WindowsError:
						continue
					if ret:
						version = v
						break
		else:
			hkey = buildHKey(version)
			try:
				ret = winregistry.registryValue(hive, hkey, valueName, architecture)[0]
			except WindowsError:
				raise Exceptions.SoftwareNotInstalled('Maya', version=version, architecture=architecture, language=language)
		# If the version is not installed this will return '.', we want to return False.
		if ret:
			return os.path.join(os.path.normpath(ret), 'bin')
		raise Exceptions.SoftwareNotInstalled('Maya', version=version, architecture=architecture, language=language)
