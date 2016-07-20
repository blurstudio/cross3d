import os
import re

# define the default environment variables
OS_TYPE = ''
if (os.name == 'posix'):
	OS_TYPE = 'Linux'
elif (os.name == 'nt'):
	OS_TYPE = 'Windows'
elif (os.name == 'osx'):
	OS_TYPE = 'MacOS'

def imageSequenceFromFileName(fileName):
	r"""
	Gets a list of files that belong to the same image sequence as the 
	passed in file.
	
		note:: 
	
		This only works if the last number in filename is part of the 
		image sequence.  For example, a file signature like this would 
		not work::

		 C:\temp\test_1234_v01.jpg

		It will ignore numbers inside the extension::
	
		C:\temp\test_1234.png1
		
	:rtype: list
	"""
	flags = 0
	if OS_TYPE == 'Windows':
		flags = re.I
	match = imageSequenceInfo(fileName)
	output = []
	if match:
		import glob
		files = glob.glob('%s*%s' % (match.group('pre'), match.group('post')))
		regex = re.compile(r'%s(\d+)%s' % (re.escape(match.group('pre')), match.group('post')), flags=flags)
		for file in files:
			if regex.match(file):
				output.append(file)
	if not output:
		output = [os.path.normpath(fileName)]
	return output

def imageSequenceInfo(path, osystem=None):
	""" Return a re.match object that seperates the file path into pre/postfix and frame number.
	
	Args:
		path (str): The path to split
		osystem (str): pass 'Windows' to make the check case insensitive. If None(the default) is
			passed in it will default to the contents of OS_TYPE.
	
	Returns:
		match: Returns the results of the re.match call or None
	"""
	flags = 0
	if osystem == None:
		osystem = OS_TYPE
	if osystem == 'Windows':
		flags = re.I
	# Look for ScXXX or SXXXX.XX to include in the prefix. This prevents problems with incorrectly
	# identifying a shot number as a image sequence. Thanks willc.
	regex = re.compile(r'(?P<pre>^.+?(?:Sc\d{3}_S\d{4}\.\d{2})?\D*)(?P<frame>\d+)(?P<post>\D*\.[A-Za-z0-9]+?$)', flags=flags)
	path = os.path.normpath(path)
	return regex.match(path)

def imageSequenceRepr(files, strFormat='{pre}[{firstNum}:{lastNum}]{post}', forceRepr=False):
	""" Takes a list of files and creates a string that represents the sequence.
	Args:
		files (list): A list of files in the image sequence.
		format (str): Used to format the output. Uses str.format() command and requires the 
			keys [pre, firstNum, lastNum, post]. Defaults to '{pre}[{firstNum}:{lastNum}]{post}'
		forceRepr (bool): If False and a single frame is provided, it will return just that frame.
			If True and a single frame is provided, it will return a repr with that frame as the
			firstNum and lastNum value. False by default.
	
	Returns:
		str: A string representation of the Image Sequence.
	"""
	if len(files) > 1 or (forceRepr and files):
		match = imageSequenceInfo(files[0])
		if match:
			info = {}
			for f in files:
				frame = imageSequenceInfo(f)
				if frame and frame.group('frame'):
					frame = frame.group('frame')
					info.update({int(frame):frame})
			if info:
				keys = sorted(info.keys())
				low = info[keys[0]]
				high = info[keys[-1]]
				if forceRepr or low != high:
					return strFormat.format(pre=match.group('pre'), firstNum=low, lastNum=high, post=match.group('post'))
	if files:
		return files[0]
	return ''

def imageSequenceReprFromFileName(fileName, strFormat=None, forceRepr=False):
	"""
	Given a filename in a image sequence, return a representation of the image sequence on disk. 
	"""
	if strFormat:
		return imageSequenceRepr(imageSequenceFromFileName(fileName), strFormat=strFormat, forceRepr=forceRepr)
	return imageSequenceRepr(imageSequenceFromFileName(fileName), forceRepr=forceRepr)

def imageSequenceForRepr(fileName):
	"""
	Returns the list of file names for a imageSequenceRepr. Only existing 
	files are returned.
	
	:rtype: list
	
	"""
	flags = 0
	if OS_TYPE == 'Windows':
		flags = re.I
	fileName = unicode(fileName)
	filter = re.compile(r'(?P<pre>^.+?)\[(?P<start>\d+)(?P<separator>[^\da-zA-Z]?)(?P<end>\d+)\](?P<post>\.[A-Za-z0-9]+?$)', flags=flags)
	match = re.match(filter, fileName)
	if match:
		import glob
		start = int(match.group('start'))
		end = int(match.group('end'))
		files = glob.glob('%s*%s' % (match.group('pre'), match.group('post')))
		regex = re.compile(r'%s(?P<frame>\d+)%s' % (match.group('pre').replace('\\', '\\\\'), match.group('post')), flags=flags)
		# Filter the results of the glob and return them in the image sequence order
		out = {}
		for f in files:
			match = regex.match(f)
			if match and start <= int(match.group('frame')) <= end:
				out.update({int(match.group('frame')): f})
		# Return the file paths sorted by frame number
		return [out[key] for key in sorted(out)]
	return [fileName]