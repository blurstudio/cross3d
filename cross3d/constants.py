##
#	\namespace	cross3d.constants
#
#	\remarks	This package defines all the constant enum types that will be used throughout the blur3d package
#
#	\author		eric
#	\author		Blur Studio
#	\date		03/15/10
#

from cross3d.enum import enum, Enum, EnumGroup

# A

AnimationType = enum('FCurve', 'StaticFCurve', 'Expression', 'Transforms', 'Position', 'Rotation', 'Scale', 'Layer')

# B

# C

CameraType = enum('Standard', 'VRayPhysical', 'Physical')
CacheType = enum('Point_Cache', 'Transform_Cache', 'XmeshLoader')
CloneType = enum('Copy', 'Instance', 'Reference')
ControllerType = enum('BezierFloat', 'LinearFloat', 'ScriptFloat', 'AlembicFloat')

# D

class _DebugLevel(Enum): pass
class DebugLevels(EnumGroup):
	Disabled = _DebugLevel(0)
	Low = _DebugLevel()
	Mid = _DebugLevel()
	High = _DebugLevel()

DepartmentGroup = enum('All', 'Simulation', 'PostPerformance', 'Performance', 'Rendering')

# E

ExtrapolationType = enum('Constant', 'Linear', 'Cycled', 'CycledWithOffset', 'PingPong')

class EnvironmentType(Enum): pass
class EnvironmentTypes(EnumGroup):
	Unknown = EnvironmentType()
	Atmospheric = EnvironmentType()
	Effect = EnvironmentType()

# F

FPSChangeType = enum('Frames', 'Seconds')
FPSContext = enum('Project', 'Sequence', 'Shot')
FPSChangeType.setDescription(FPSChangeType.Frames, 'Timings fixed on frames, animation curves scaled to compensate.')
FPSChangeType.setDescription(FPSChangeType.Seconds, 'Timings fixed on seconds, animation key values in frame will change.')

# G

# H

# I

IODirection = enum('Input', 'Output', InAndOut=3)

# J

# K

TangentType = enum('Automatic', 'Bezier', 'Linear', 'Stepped')

# L

# M

MaterialType = enum('Generic', 'VRay')
MaterialCacheType = enum('BaseMaterial', 'MaterialOverrideList')
MaterialOverrideOptions = enum('KeepOpacity', 'KeepDisplacement', 'KeepBump', All=3)
MapCacheType = enum('EnvironmentMap')
MapType = enum('Generic', 'VRay')
MaterialPropertyMap = enum(outColor='diffuse')

# N

NotifyType = enum('Email', 'Jabber')

# O

ObjectType = enum(
	'Generic',
	'Geometry',
	'Light',
	'Camera',
	'Model',
	'Group',
	'Bone',
	'Particle',
	'FumeFX',
	'Curve',
	'PolyMesh',
	'NurbsSurface',
	'Thinking',
	'XMeshLoader',
	'CameraInterest',
	'Null'
)

# P
class PointerType(Enum): pass
class PointerTypes(EnumGroup):
	Shape = PointerType()
	Transform = PointerType()
	Pointer = PointerType()
	
ProxyType = enum('Disabled', 'Lossy', 'Lossless')
PaddingStyle = enum('Blank', 'Number', 'Pound', 'Percent', 'Wildcard')

# Q

# R

RendererType = enum('Scanline', 'VRay', 'MentalRay', 'Quicksilver')
RotationOrder = enum('XYZ', 'YZX', 'ZXY', 'XZY', 'YXZ', 'ZYX')

class RigMake(Enum):
	pass

class RigMakes(EnumGroup):
	Biped = RigMake()
	HumanIK = RigMake()
	CAT = RigMake()
	MadCar = RigMake()
	Harbie = RigMake()
	Gear = RigMake()
	BradNoble = RigMake()

# S

ScriptLanguage = enum('Python', 'MAXScript', 'JavaScript', 'VisualBasic', 'MEL')
SubmitType = enum('Render', 'Script', 'Batch')
SubmitFlags = enum('WriteInfoFile', 'DeleteOldFrames', 'VisibleToRenderable', 'RemoteSubmit', 'DeleteHiddenGeometry', 'CreateProxyJob', Default=1)
Source = enum('Remote', 'Local')

# T

TimeUnit = enum('Frames', 'Seconds', 'Milliseconds', 'Ticks')

# U

UpVector = enum('Y', 'Z')

# V

VideoCodec = enum('PhotoJPEG', 'H264', 'GIF')
Viewports = enum('Current', 'One', 'Two', 'Three', 'Four')
VisibilityToggleOptions = enum(
	'ToggleLights',
	'ToggleFX',
	'ToggleAtmospherics',
	'TogglePointCaches',
	'ToggleTransformCaches',
	'ToggleXMeshes',
	'ToggleFrost',
	'ToggleVRayStereoscopics',
	'ToggleAlembic',
	All=511
)

# W

# X

# Y

# Z
