##
#	\namespace	cross3d.classes.clipboard
#
#	\remarks	This file defines the clipboard class that allows to manipulate the clipboard.
#	
#	\author		douglas
#	\author		Blur Studio
#	\date		12/01/15
#

import subprocess

class FlipBook(object):

	def __init__(self, fps=30.0):
		super(FlipBook, self).__init__()
		self.fps = fps
		self._sources = []

	def addSource(self, path='', start=None, enter=0, out=0, position=(0,0), scale=100):
		source = {}
		source['path'] = path
		source['start'] = start
		source['enter'] = enter
		source['out'] = out + 1
		source['position'] = position
		source['scale'] = scale
		self._sources.append(source)
		return True

	def run(self):
		command = []
		duration = 0

		# TODO: We should problably find a better way to get to the software.
		command.append(r'C:\Program Files\Pdplayer 64\pdplayer64.exe')

		for source in self._sources:
			enter = source['enter']
			start = source['start']
			out = source['out']

			command.append('{}'.format(source['path']))
			
			# I consider a None start to automatically queue sources.
			begin = duration-enter if start is None else start-enter 
			command.append('--begin={}'.format(begin))

			if source['enter']:
				command.append('--in_point={}'.format(enter))

			if source['out']:
				command.append('--out_point={}'.format(out))

			command.append('--position={},{}'.format(*source['position']))
			command.append('--scale={}'.format(source['scale']))
			command.append('--layer_preload_into_cache')
			command.append('--auto_update=1')
			
			newDuration = begin + out
			duration = newDuration if newDuration > duration else duration

		# Command footer.
		command.append('--fps={}'.format(self.fps))
		command.append('--timeline={}'.format(duration))
		command.append('--preload_all_layers')
		command.append('--repeat_type=loop')
		command.append('--play_forward')

		# Running the command.
		if cross3d.debugLevel >= cross3d.constants.DebugLevels.Mid:
			print 'PDPLAYER COMMAND:', ' '.join(command)
		subprocess.Popen(command)
		return True

