##
#   \namespace  cross3d.classes.exceptions
#
#   \remarks    [desc::commented]
#   
#   \author     douglas
#   \author     Blur Studio
#   \date       02/24/12
#

#--------------------------------------------------------------------------------

class Exceptions:

	class Blur3DException( Exception ):
		'''
			Raise exceptions specific to blur3d.
		'''
		pass
	
	class FileNotDSO(Exception):
		"""
			Exception raised if unable to open dso file properties.
		"""
		pass
	
	class FPSChangeFailed(Blur3DException):
		"""
			Exception Raised if unable to change the FPS
		"""
		pass
		
	class OutputFailed(Blur3DException):
		"""
			Exception Raised if unable to change the FPS
		"""
		pass
	
	class SoftwareNotInstalled(Blur3DException):
		""" Exception rased if unable to find the software version.
		"""
		def __init__(self, name, version='', architecture=64, language='English'):
			if version:
				version = ' {}'.format(version)
			self.message = '{name} {version} {arch}-bit not installed for {language}.'.format(
					name=name, version=version, arch=architecture, language=language)
			super(Exceptions.SoftwareNotInstalled, self).__init__(self.message)

	class SignalAlreadyConnected(Blur3DException):
		""" Exception rased if a signal is already connected.
		"""
		pass

	class FileFormatNotSupported(Blur3DException):
		""" Exception raised if you try to save a file in a unsuported file format
		"""
		pass
	
	class InvalidNativeObject(Blur3DException):
		""" Exception raised if you try to access a native pointer that is no longer valid
		"""
		pass
