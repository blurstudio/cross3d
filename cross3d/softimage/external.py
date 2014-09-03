##
# 	\namespace	blur3d.api.softimage.external
#
#	\remarks	This class can be used even outside of softimage. It gives you info on where
#				softimage is installed, and allows you to run scripts in softimage.
#				To Access this class use: blur3d.api.external('softimage')
#
# 	\author		dougl@blur.com
# 	\author		Blur Studio
# 	\date		01/21/14
#

#------------------------------------------------------------------------------------------------------------------------

import os
#import glob
import subprocess
import xml.etree.cElementTree as ET

from blur3d.api.abstract.external import External as AbstractExternal

#------------------------------------------------------------------------------------------------------------------------

class External(AbstractExternal):

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
	def runScript(cls, script, version=None, architecture=64):

		if os.path.exists(script):
			scriptPath = script

		else:
			scriptPath = cls.scriptPath()
			fle = open(scriptPath, "w")
			fle.write(script)
			fle.close()

		binary = os.path.join(cls.binariesPath(version, architecture), 'xsibatch.exe')
		pipe = subprocess.Popen([binary, '-processing', '-script', scriptPath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		
		# Writing the log file.
		fle = open(cls.scriptLog(), 'w')
		fle.write(pipe.stdout.read())
		fle.close()

		# Checking the error in the log file.
		fle = open(cls.scriptLog())
		content = fle.read()

		return False if 'FATAL' in content else True

	@classmethod
	def scriptPath(cls):
		return r'C:\temp\softimage_batchscript.py'

	@classmethod
	def scriptLog(cls):
		return r'C:\temp\softimage_batchscript.log'

	@classmethod
	def binariesPath(cls, version=None, architecture=64, language='English'):
		""" Finds the install path for various software installations. Does not need to be
		:param version: The version of the software. Default is None
		:param architecture: The bit type to query the registry for(32, 64). Default is 64
		:param language: Optional language that may be required for specific softwares.
		"""
		ret = cls._registryValue('HKEY_LOCAL_MACHINE', r'Software\Autodesk\Softimage\InstallPaths', unicode(version), architecture)[0]
		# If the version is not installed this will return '.', we want to return False.
		if ret:
			return os.path.normpath(ret)
		return False
