##
#   \namespace  blur3d.api.classes.framerange
#
#   \remarks    This module holds the FrameRange class to handle frame ranges.
#   
#   \author     douglas@blur.com
#   \author     Blur Studio
#   \date       11/30/11
#

#------------------------------------------------------------------------------------------------------------------------

class FrameRange( list ):
	
	def __init__( self, args ):
		"""
			\remarks	Initialize the class.
		"""
		if len( args ) > 1:
			args = args[0:2]
		elif args:
			args.append( args[0] )
		else:
			args = [0,0]
		try:
			args = list( args )
			args[0] = int( args[0] )
			args[1] = int( args[1] )
		except:
			raise Exception( "Arguments %s are not valid." % str( args ) )	
		super( FrameRange, self ).__init__( args )

	def __repr__( self ):
		"""
			\remarks	Affects the class representation.
		"""
		return 'blur3d.api.FrameRange( %s, %s )' % ( self[0], self[1] )
		
	def string( self, separator='-' ):
		"""
			\remarks	Returns the range in its string form.
			\param		separator <string>
		"""
		return '%i%s%i' % ( self[0], separator, self[1] )
		
	def start( self ):
		return self[0]
		
	def end( self ):
		return self[1]
		
	def duration( self ):
		return self[1] - self[0] + 1
		
	def isWithin( self, frameRange ):
		if self[0] >= frameRange[0] and self[1] <= frameRange[1]:
			return True
		return False
		
	def offsets( self, frameRange ): 
		return FrameRange( [ ( frameRange[0] - self[0] ), ( frameRange[1] - self[1] ) ] )
				
	def overlaps( self, frameRange ):
		if self[0] > frameRange[1] or self[1] < frameRange[0]:
			return False
		return True
		
	def overlap( self, frameRange ):
		"""
			\remarks	Returns the overlaping range if any.
		"""
		if self.overlaps( frameRange ):
			if self[0] < frameRange[0]:
				start = frameRange[0]
			else:
				start = self[0]
			if self[1] > frameRange[1]:
				end = frameRange[1]
			else:
				end = self[1]
			return FrameRange( [ start, end ] )
		else:
			None
			
	def merge( self, frameRange ):
		"""
			\remarks	Returns a range that covers both framerange.
		"""
		return FrameRange( [ min( self[0], frameRange[0] ), max( self[1], frameRange[1] ) ] )

	def pad( self, padding ):
		"""
			\remarks	Adds handles to the range.
		"""
		self[0] = self[0] - padding
		self[1] = self[1] + padding