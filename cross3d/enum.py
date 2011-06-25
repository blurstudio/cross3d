##
#	\namespace	blur3d.api.enum
#
#	\remarks	Defines the global and most commonly used enumerated types for blur3d.api
#	
#	\author		Mikeh@blur.com
#	\author		Blur Studio
#	\date		06/24/11
#

from blurdev.enum import enum as _enum

# Used to define what viewport is to be used. Current will get the active viewport.
viewports = _enum('Current', 'One', 'Two', 'Three', 'Four')