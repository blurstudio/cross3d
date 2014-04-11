
import os
import sys
import shutil
import subprocess

from blur3d.api.abstract.external import External as AbstractExternal
from blurdev.media import dsofile

#------------------------------------------------------------------------------------------------------------------------

class External(AbstractExternal):

	_architectureTokens = {64: r'_x64', 32: r''}
	_versionTokens = {2012: r'Max2012'}

	@classmethod
	def getFileVersion(cls, filepath):
		"""
		Reads the max version that a max file was saved with from a custom 
		dso property added to the file when it is saved from max.
		"""
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
	def runScript(cls, script, version=None, architecture=64):

		if os.path.exists(script):
			scriptPath = script

		else:
			scriptPath = cls.scriptPath()
			fle = open(scriptPath, "w")
			fle.write(script)
			fle.close()

		binary = os.path.join(cls.binariesPath(version, architecture), '3dsmax.exe')
		process = subprocess.Popen([binary, '-U', 'MAXScript', scriptPath], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		
		# Writing the log file.
		fle = open(cls.scriptLog(), 'w')
		fle.write(process.stdout.read())
		fle.close()

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
	def binariesPath(cls, version=None, architecture=64):
		
		# Getting the latest version if not provided.
		version = version or sorted(cls._versionTokens.keys())[-1]

		# Getting tokens for the the binary folder path.
		tokens = {}
		tokens['architecture'] = cls._architectureTokens.get(architecture)
		tokens['version'] = cls._versionTokens.get(version)

		if tokens['architecture'] and tokens['version']:
			return r'C:\{version}{architecture}\3ds Max 2012'.format(**tokens)

		else:
			raise Exception('Invalid version or architecture.')