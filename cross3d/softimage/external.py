##
# 	\namespace	blur3d.api.softimage.external
#
#	\remarks	[desc::commented]
#
# 	\author		dougl@blur.com
# 	\author		Blur Studio
# 	\date		01/21/14
#

#------------------------------------------------------------------------------------------------------------------------

import os
import sys
import shutil
import subprocess

from blur3d.api.abstract.external import External as AbstractExternal

#------------------------------------------------------------------------------------------------------------------------

class External(AbstractExternal):

	_architectureTokens = {64: r'Program Files', 32: r'Program Files (x86)'}
	_versionTokens = {10: r'Softimage 2012', 11: r'Softimage 2013'}

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
		pipe = subprocess.Popen([binary, '-processing', '-script', scriptPath], stdout=subprocess.PIPE)
		
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
	def binariesPath(cls, version=None, architecture=64):
		
		# Getting the latest version if not provided.
		version = version or sorted(cls._versionTokens.keys())[-1]

		# Getting tokens for the the binary folder path.
		tokens = {}
		tokens['architecture'] = cls._architectureTokens.get(architecture)
		tokens['version'] = cls._versionTokens.get(version)

		if tokens['architecture'] and tokens['version']:
			return r'C:\{architecture}\Autodesk\{version}\Application\bin'.format(**tokens)

		else:
			raise Exception('Invalid version or architecture.')