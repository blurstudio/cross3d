##
# 	\namespace	cross3d.softimage.external
#
#	\remarks	This class can be used even outside of softimage. It gives you info on where
#				softimage is installed, and allows you to run scripts in softimage.
#				To Access this class use: cross3d.external('softimage')
#
# 	\author		dougl
# 	\author		Blur Studio
# 	\date		01/21/14
#

#------------------------------------------------------------------------------------------------------------------------

import os
import subprocess
import xml.etree.cElementTree as ET

from cross3d import Exceptions
from cross3d.constants import ScriptLanguage
from cross3d.abstract.external import External as AbstractExternal

#------------------------------------------------------------------------------------------------------------------------

class External(AbstractExternal):
	# In case the software is installed but not used don't find it when not passing in a version
	_ignoredVersions = set(os.environ.get('CROSS3D_STUDIO_IGNORED_SOFTIMAGE', '').split(','))
	# map years to version numbers
	_yearForVersion = {'8': '2010', '9': '2011', '10': '2012', '11': '2013', '12': '2014', '13': '2015'}

	@classmethod
	def name(cls):
		return 'Softimage'

	@classmethod
	def getFileVersion(cls, filepath):
		"""
		Reads the xsi version of an xsi file from the associated scntoc. 
		"""
		scntoc_path = filepath + 'toc'
		if os.path.isfile(scntoc_path):
			tree = ET.parse(scntoc_path)
			root = tree.getroot()
			return root.get('xsi_version')
		return None

	@classmethod
	def runScript(cls, script, version=None, architecture=64, language=ScriptLanguage.Python, debug=False, headless=True):

		if os.path.exists(script):
			scriptPath = script

		else:
			scriptPath = cls.scriptPath()
			with open(scriptPath, "w") as fle:
				fle.write(script)

		binary = os.path.join(cls.binariesPath(version, architecture), 'xsibatch.exe' if headless else 'xsi.exe')
		scriptArgumentName = '-script' if headless else '-uiscript'

		# Contrinue makes sure there is no prompts.
		command = [binary, '-continue', scriptArgumentName, scriptPath]

		# Processing means that it will not shot the GUI and not grab a license.
		if headless:
			command.insert(1, '-processing')

		process = subprocess.Popen(command, stdout=subprocess.PIPE)

		# TODO: This is the way to check for success. But it is blocking.
		# Writing the log file.
		with open(cls.scriptLog(), 'w') as fle:
			fle.write(process.stdout.read())

		# Checking the error in the log file.
		with open(cls.scriptLog()) as fle:
			content = fle.read()

		return False if 'FATAL' in content else True

	@classmethod
	def binariesPath(cls, version=None, architecture=64, language='English'):
		""" Finds the install path for various software installations. If version is None, the default
		it will return the latest installed version of the software. Raises cross3d.Exceptions.SoftwareNotInstalled
		if the software is not installed.
		:param version: The version of the software. Default is None
		:param architecture: The bit type to query the registry for(32, 64). Default is 64
		:param language: Optional language that may be required for specific softwares.
		"""
		hive = 'HKEY_LOCAL_MACHINE'
		hkey = r'Software\Autodesk\Softimage\InstallPaths'
		ret = None
		if version == None:
			# Find the latest version
			from cross3d.migrate import winregistry
			versions = winregistry.listRegKeyValues(hive, hkey, architecture=architecture)
			for version in sorted(versions, key= lambda i: i[0], reverse=True):
				if version[0] not in cls._ignoredVersions:
					ret = version[1]
					break
		else:
			version = cls._yearForVersion.get(unicode(version), version)
			try:
				ret = winregistry.registryValue(hive, hkey, unicode(version), architecture)[0]
			except WindowsError:
				raise Exceptions.SoftwareNotInstalled('Softimage', version=version, architecture=architecture, language=language)
		# If the version is not installed this will return '.', we want to return False.
		if ret:
			return os.path.join(os.path.normpath(ret), 'Application', 'bin')
		raise Exceptions.SoftwareNotInstalled('Softimage', version=version, architecture=architecture, language=language)
