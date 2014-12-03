##
#	\namespace	blur3d.api.abstract.abstractsceneanimationcontroller
#
#	\remarks	The AbstractSceneAnimationController class provides an interface to editing controllers in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

import math

from Py3dsMax import mxs
from blur3d.api import FCurve
from blur3d.constants import ControllerType
from blur3d.api.abstract.abstractsceneanimationcontroller import AbstractSceneAnimationController

class StudiomaxSceneAnimationController( AbstractSceneAnimationController ):

	_nativeToAbstractTypes = { 'bezier_float'             : ControllerType.BezierFloat,
							   'linear_float'             : ControllerType.LinearFloat,
							   'script_float'             : ControllerType.ScriptFloat,
							   'Alembic_Float_Controller' : ControllerType.AlembicFloat }

	_abstractToNativeTypes = { ControllerType.BezierFloat  : mxs.bezier_float,
							   ControllerType.LinearFloat  : mxs.linear_float,
							   ControllerType.ScriptFloat  : mxs.script_float,
							   ControllerType.AlembicFloat : mxs.Alembic_Float_Controller }

	_slopeDistortions = {24:0.12, 25:0.13, 30:0.187, 60:0.75}

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	def _createNativeKeyAt( self, time ):
		"""
			\remarks	implements the AbstractSceneAnimationController._nativeKeys method to create a new key at the inputed time
			\param		time		<float>
			\return		<Py3dsMax.mxs.Key> nativeKey || None
		"""
		return mxs.addNewKey( self._nativePointer, time )
	
	def _nativeKeys( self ):
		"""
			\remarks	implements the AbstractSceneAnimationController._nativeKeys method to collect a list of the current keys
						for this controller instance
			\return		<list> [ <Py3dsMax.mxs.Key> nativeKey, .. ]
		"""

		# This method only supports controllers with keys.
		if mxs.classOf(self._nativePointer) in [mxs.bezier_float, mxs.linear_float]:
			return self._nativePointer.keys
		return []
		
	@classmethod
	def _createNewNative(cls, scene, controllerType):
		"""
			\remarks	implements the AbstractSceneAnimationController._createNewNative method to create a new native controller in the scene of the inputed controller type
			\param		scene				<blur3d.api.Scene>
			\param		controllerType		<blur3d.constants.ControllerType>
			\return		<blur3d.api.SceneAnimationController> || None
		"""
		if (controllerType == ControllerType.BezierFloat):
			return mxs.bezier_float()
		elif (controllerType == ControllerType.LinearFloat):
			return mxs.linear_float()
		return None
	
	def _setNativeKeyAt(self, time, nativeKey):
		"""
			\remarks	set the key at the inputed time to the given native key
			\param		time		<float>
			\param		nativeKey	<variant>
			\return		<bool> success
		"""
		key = self.keyAt(time)
		if nativeKey == None:
			# remove the key if it exists
			if key:
				index = mxs.getKeyIndex(self._nativePointer, time)
				# index is 1 based, zero indecates that the key was not found.
				if index != 0:
					return mxs.deleteKey(self._nativePointer, index)
		elif not key:
			# Create the key so we can set the value
			key = self._createNativeKeyAt(time)
			if not key:
				return False
		return key.setValue(nativeKey)
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def type(self):
		"""
			\remarks	implements AbstractSceneAnimationController.controllerType method to return the controller type for this instance
			\return		<blur3d.constants.ControllerType>
		"""
		return self._nativeToAbstractTypes.get(str(mxs.classOf(self._nativePointer)), 0)

	def displayName(self):
		return self.name().split('.')[-1]

	def name( self ):
		"""
			\remarks	implements AbstractSceneWrapper.name to return the name of this animation controller instance
			\sa			setName
			\return		<str> name
		"""
		return '.'.join(mxs.exprForMaxObject(self._nativePointer).split('.')[1:])

	def valueAtFrame(self, frame):
		mxs.execute("""fn getControllerValueAtFrame controller frame = (
			at time frame
			return controller.value
		)""")
		return mxs.getControllerValueAtFrame(self._nativePointer, frame)

	def fCurve(self):
		""" Returns a FCurve object to manipulate or save the curve data.
		"""
		fCurve = None
		controllerType = self.type()
		
		# We only support controllers that can have keys.
		if controllerType in (ControllerType.BezierFloat, ControllerType.LinearFloat):

			# Creating a new fCurve object.
			fCurve = FCurve(name=self.displayName(), tpe=controllerType)

			# Getting the slope distortion based on scene frame rate. On of Max's treats.
			sd = self._slopeDistortions.get(int(self._scene.animationFPS()), 0.1)


			for key in self.keys():
				key = key.nativePointer()
				
				# Storing current key values.
				freeHandle = key.freeHandle
				inTangentLength = key.inTangentLength
				inTangentType = key.inTangentType
				outTangentLength = key.outTangentLength
				outTangentType = key.outTangentType
				
				# It takes time to set and restore the free handles so I only do it if necessary.
				needsFreeHandle = not (str(inTangentType) == 'linear' and str(outTangentType) == 'linear') and not freeHandle
				if needsFreeHandle:

					# We want the non normalized handle length values.
					key.freeHandle = True

				kwargs ={}
				kwargs['value'] = key.value
				kwargs['time'] = key.time

				# Bare in mind that inTangent and outTangent are the slopes.
				kwargs['inTangentAngle'] = math.atan((key.inTangent * 0.1 / sd) * 10.0)
				kwargs['outTangentAngle'] = math.atan((key.outTangent * 0.1 / sd) * 10.0)
				kwargs['inTangentType'] = key.inTangentType
				kwargs['outTangentType'] = key.outTangentType

				# Bare in mind that Max tangent length is actually not the length but the length on the time axis.
				kwargs['inTangentLength'] = key.inTangentLength / math.cos(kwargs['inTangentAngle']) if kwargs['inTangentAngle'] != 0.0 else key.inTangentLength
				kwargs['outTangentLength'] = key.outTangentLength / math.cos(kwargs['outTangentAngle']) if kwargs['outTangentAngle'] != 0.0 else key.outTangentLength
				kwargs['normalizedTangents'] = not freeHandle
				kwargs['brokenTangents'] = not key.x_locked
				fCurve.addKey(**kwargs)

				# It takes time to set and restore the free handles so I only do it if necessary.
				if needsFreeHandle:

					# Restoring the key settings.
					key.freeHandle = freeHandle
					key.inTangentType = inTangentType
					key.outTangentType = outTangentType
					key.inTangentLength = inTangentLength
					key.outTangentLength = outTangentLength

		return fCurve

	def setFCurve(self, fCurve):
		""" Takes a fCurve object data and applies it to the controller.
		"""

		tpe = fCurve.type()
		keys = fCurve.keys()


		if tpe and keys:

			# Making a fresh controller.
			controller = self._abstractToNativeTypes.get(tpe)()

			if controller:

				# Getting the slope distortion based on scene frame rate. On of Max's treats.
				sd = self._slopeDistortions.get(int(self._scene.animationFPS()), 0.1)

				# For a reason that falls beyond my comprehension, it is important to set all the keys first.
				for k in keys:
					key = mxs.addNewKey(controller, k.time)
					key.value = k.value
				
				# And then do a second pass to process the tangents.
				for k in keys:
					key = mxs.getKey(controller, mxs.getKeyIndex(controller, k.time))
					
					# The tangeants do not expected the same values if the are free.
					key.freeHandle = True
					key.x_locked = False
					key.inTangentType = mxs.pyhelper.namify('custom')
					key.outTangentType = mxs.pyhelper.namify('custom')

					# The Max tangent lenght is actually the distance on the time axis.	
					key.inTangentLength = math.cos(k.inTangentAngle) * k.inTangentLength
					key.inTangent = (math.tan(k.inTangentAngle) / 10.0) * sd / 0.1

					# The Max tangent lenght is actually the distance on the time axis.
					key.outTangentLength = math.cos(k.outTangentAngle) * k.outTangentLength
					key.outTangent = (math.tan(k.outTangentAngle) / 10.0) * sd / 0.1
							
					# Restore other key properties.
					key.inTangentType = mxs.pyhelper.namify(k.inTangentType)
					key.outTangentType = mxs.pyhelper.namify(k.outTangentType)
					key.freeHandle = not k.normalizedTangents
					key.x_locked = not k.brokenTangents

				mxs.replaceInstances(self._nativePointer, controller)

				# It is essential to re-point the native pointer.
				self._nativePointer = controller

	def framesForValue(self, value, closest=True):

		# TODO: (Douglas) This function is far from being perfect but it does the job.
		frames = {}

		keys = self.keys()
		closestFrame = 0
		if keys:
			start = int(round(keys[0].time()))
			end = int(round(keys[-1].time()))
			index = 0
			previousValue = None
			closestValue = 0.0

			# Looping through frames.
			for frame in range(start, end + 1):
				currentValue = self.valueAtFrame(frame)

				if closest:
					if abs(value-currentValue) < abs(value-closestValue):
						closestValue = currentValue
						closestFrame = frame
				
				if round(currentValue) == round(value):
					if previousValue is None or abs(value-currentValue) < abs(value-previousValue):
						frames[index] = frame

						# Saving value as previous value.
						previousValue = currentValue

				elif frames.get(index):
					index += 1
					previousValue = None

		if not frames and closest:
			return [closestFrame]

		return sorted(frames.values())		

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneAnimationController', StudiomaxSceneAnimationController )