##
#   :namespace  cross3d.motionbuilder.external
#
#   :remarks    This class can be used even outside of motionbuilder. It gives you info on where
#				motionbuilder is installed, and allows you to run scripts in motionbuilder.
#				To Access this class use: cross3d.external('motionbuilder')
#   
#   :author     mikeh
#   :author     Blur Studio
#   :date       09/03/14
#

#------------------------------------------------------------------------------------------------------------------------

import os
import subprocess

from cross3d import Exceptions
from cross3d.constants import ScriptLanguage
from cross3d.abstract.external import External as AbstractExternal

#------------------------------------------------------------------------------------------------------------------------

class External(AbstractExternal):
	_hkeyBase = r'Software\Autodesk\MotionBuilder'
	# In case the software is installed but not used don't find it when not passing in a version
	_ignoredVersions = set(os.environ.get('CROSS3D_STUDIO_IGNORED_MOTIONBUILDER', '2013,2015').split(','))
	# map years to version numbers 
	# NOTE: I am guessing that these are correct based on 2014 being version 14000.0
	_yearForVersion = {'12': '2012', '13': '2013', '14': '2014', '15': '2015', '16': '2016'}
	
	@classmethod
	def binariesPath(cls, version=None, architecture=64, language='English'):
		""" Finds the install path for various software installations.
		:param version: The version of the software. Default is None
		:param architecture: The bit type to query the registry for(32, 64). Default is 64
		:param language: Optional language that may be required for specific softwares.
		"""
		version = cls._yearForVersion.get(unicode(version), version)
		hive = 'HKEY_LOCAL_MACHINE'
		from cross3d.migrate import winregistry
		if version == None:
			# Get all of the installed versions so we can find the latest version.
			versions = winregistry.listRegKeys(hive, cls._hkeyBase, architecture=architecture)
			for v in sorted(versions, reverse=True):
				if v not in cls._ignoredVersions:
					version = v
					break
		hkey = r'{hkeyBase}\{version}'.format(hkeyBase=cls._hkeyBase, version=version)
		try:
			ret = winregistry.registryValue(hive, hkey, 'InstallPath', architecture)[0]
		except WindowsError:
			raise Exceptions.SoftwareNotInstalled('MotionBuilder', version=version, architecture=architecture, language=language)
		# If the version is not installed this will return '.', we want to return False.
		if ret:
			return os.path.normpath(ret)
		raise Exceptions.SoftwareNotInstalled('MotionBuilder', version=version, architecture=architecture, language=language)

	@classmethod
	def runScript(cls, script, version=None, architecture=64, language=ScriptLanguage.Python, debug=False, headless=True):

		# If the script argument is a path to a file.
		if os.path.exists(script):
			with open(script, 'r') as fle:
				script = fle.read()

		scriptPath = os.path.splitext(cls.scriptPath())[0] + '.py'
		with open(scriptPath, 'w') as fle:
			fle.write(script)
	
		binary = os.path.join(cls.binariesPath(version, architecture), 'mayabatch.exe' if headless else 'maya.exe')
		args = [binary, '-console', '-verbosePython', scriptPath]
		subprocess.Popen(args, creationflags=subprocess.CREATE_NEW_CONSOLE, env=os.environ)

		# TODO: Need to figure out a way to return False if the script has failed.
		return True

	@classmethod
	def scriptPath(cls):
		return r'C:\temp\motionbuilder_script.py'

	@classmethod
	def scriptLog(cls):
		return r'C:\temp\motionbuilder_script.log'