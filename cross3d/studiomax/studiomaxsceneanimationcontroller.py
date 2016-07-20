##
#	\namespace	cross3d.abstract.abstractsceneanimationcontroller
#
#	\remarks	The AbstractSceneAnimationController class provides an interface to editing controllers in a Scene environment for any DCC application
#
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

import math

from Py3dsMax import mxs
from cross3d import FCurve
from cross3d.constants import ControllerType, TangentType, TimeUnit, ExtrapolationType
from cross3d.abstract.abstractsceneanimationcontroller import AbstractSceneAnimationController


class StudiomaxSceneAnimationController(AbstractSceneAnimationController):

	_nativeToAbstractTypes = {'bezier_float': ControllerType.BezierFloat,
                           'linear_float': ControllerType.LinearFloat,
                           'script_float': ControllerType.ScriptFloat,
                           'Alembic_Float_Controller': ControllerType.AlembicFloat}

	_abstractToNativeTypes = {ControllerType.BezierFloat: mxs.bezier_float,
                           ControllerType.LinearFloat: mxs.linear_float,
                           ControllerType.ScriptFloat: mxs.script_float,
                           ControllerType.AlembicFloat: mxs.Alembic_Float_Controller}

	_nativeToAbstractExtrapolationType = {'constant': ExtrapolationType.Constant,
                                       'linear': ExtrapolationType.Linear,
                                       'cycle': ExtrapolationType.Cycled,
                                       'loop': ExtrapolationType.Cycled,
                                       'pingPong': ExtrapolationType.PingPong,
                                       'relativeRepeat': ExtrapolationType.CycledWithOffset}

	_abstractToNativeExtrapolationType = {ExtrapolationType.Constant: mxs.pyhelper.namify('constant'),
                                       ExtrapolationType.Linear: mxs.pyhelper.namify('linear'),
                                       ExtrapolationType.Cycled: mxs.pyhelper.namify('loop'),
                                       ExtrapolationType.CycledWithOffset: mxs.pyhelper.namify('relativeRepeat'),
                                       ExtrapolationType.PingPong: mxs.pyhelper.namify('pingPong')}

	_slopeDistortions = {24: 0.12, 25: 0.13, 30: 0.187, 60: 0.75}

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	def _createNativeKeyAt(self, time):
		"""
			\remarks	implements the AbstractSceneAnimationController._nativeKeys method to create a new key at the inputed time
			\param		time		<float>
			\return		<Py3dsMax.mxs.Key> nativeKey || None
		"""
		return mxs.addNewKey(self._nativePointer, time)

	def _nativeKeys(self):
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
			\param		scene				<cross3d.Scene>
			\param		controllerType		<cross3d.constants.ControllerType>
			\return		<cross3d.SceneAnimationController> || None
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
			\return		<cross3d.constants.ControllerType>
		"""
		return self._nativeToAbstractTypes.get(str(mxs.classOf(self._nativePointer)), 0)

	def displayName(self):
		return self.name().split('.')[-1]

	def name(self):
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

	def extrapolation(self):
		extrapolation = [mxs.getBeforeORT(self._nativePointer), mxs.getAfterORT(self._nativePointer)]
		return [self._nativeToAbstractExtrapolationType.get(str(e), ExtrapolationType.Constant) for e in extrapolation]

	def setExtrapolation(self, extrapolation=[None, None]):
		""" None will leave the the extrapolation unaffected.
		"""
		if not isinstance(extrapolation, (list, tuple)):
			extrapolation = (extrapolation, extrapolation)
		if extrapolation[0]:
			mxs.setBeforeORT(self._nativePointer, self._abstractToNativeExtrapolationType.get(extrapolation[0], ExtrapolationType.Constant))
		if extrapolation[1]:
			mxs.setAfterORT(self._nativePointer, self._abstractToNativeExtrapolationType.get(extrapolation[1], ExtrapolationType.Constant))
		return True

	def fCurve(self):
		""" Returns a FCurve object to manipulate or save the curve data.
		"""

		# Importing SceneAnimationKey to get abstract types information.
		from cross3d import SceneAnimationKey

		# Getting what we need.
		controllerType = self.type()
		fCurve = FCurve(name=self.displayName(), tpe=controllerType)

		# Writing the extrapolation.
		fCurve.setExtrapolation(self.extrapolation())

		# We only support controllers that can have keys.
		if controllerType in (ControllerType.BezierFloat, ControllerType.LinearFloat):

			# Getting the slope distortion based on scene frame rate. On of Max's treats.
			sd = self._slopeDistortions.get(int(self._scene.animationFPS()), 0.1)

			# Getting keys.
			keys = self.keys()
			keyCount = len(keys)

			# Looping through keys.
			for index in range(keyCount):

				# Getting native key.
				key = keys[index].nativePointer()

				# Storing key data.
				kwargs = {}
				kwargs['value'] = key.value
				kwargs['time'] = key.time
				kwargs['normalizedTangents'] = not key.freeHandle

				# Storing tangent type.
				inTangentType = key.inTangentType
				outTangentType = key.outTangentType

				# If tangents are normalized calculating the tangent lenght is a bit more work.
				# Do not try to bypass that by temporarly changing the key mode. This is the way I had it before.
				# Restoring the key mode takes a lot of time somehow has a great impact on tools. Especialy with V-Ray cameras.
				if kwargs['normalizedTangents']:

					if index > 0:
						pKey = keys[index - 1].nativePointer()
						inTangentLength = (kwargs['time'] - pKey.time) * key.inTangentLength
					else:
						inTangentLength = 0.0

					if index < keyCount - 1:
						nKey = keys[index + 1].nativePointer()
						outTangentLength = (nKey.time - kwargs['time']) * key.outTangentLength
					else:
						outTangentLength = 0.0

				else:
					inTangentLength = key.inTangentLength
					outTangentLength = key.outTangentLength

				# Bare in mind that inTangent and outTangent are the slopes.
				kwargs['inTangentAngle'] = math.atan((key.inTangent * 0.1 / sd) * 10.0)
				kwargs['outTangentAngle'] = math.atan((key.outTangent * 0.1 / sd) * 10.0)
				kwargs['inTangentType'] = SceneAnimationKey._nativeToAbstractTangentTypes.get(str(inTangentType), TangentType.Automatic)
				kwargs['outTangentType'] = SceneAnimationKey._nativeToAbstractTangentTypes.get(str(outTangentType), TangentType.Automatic)

				# Bare in mind that Max tangent length is actually not the length but the length on the time axis.
				kwargs['inTangentLength'] = inTangentLength / math.cos(kwargs['inTangentAngle']) if kwargs['inTangentAngle'] != 0.0 else inTangentLength
				kwargs['outTangentLength'] = outTangentLength / math.cos(kwargs['outTangentAngle']) if kwargs['outTangentAngle'] != 0.0 else outTangentLength
				kwargs['brokenTangents'] = not key.x_locked
				fCurve.addKey(**kwargs)

		return fCurve

	def setFCurve(self, fCurve):
		""" 
			Takes a fCurve object data and applies it to the controller.
		"""

		# Importing SceneAnimationKey to get abstract types information.
		from cross3d import SceneAnimationKey

		# Getting what we need.
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
					key.inTangentType = SceneAnimationKey._abstractToNativeTangentTypes.get(k.inTangentType, mxs.pyhelper.namify('auto'))
					key.outTangentType = SceneAnimationKey._abstractToNativeTangentTypes.get(k.outTangentType, mxs.pyhelper.namify('auto'))
					key.freeHandle = not k.normalizedTangents
					key.x_locked = not k.brokenTangents

				mxs.replaceInstances(self._nativePointer, controller)

				# It is essential to re-point the native pointer.
				self._nativePointer = controller

		# Setting the extrapolation.
		print fCurve.extrapolation()
		self.setExtrapolation(fCurve.extrapolation())
		return True

	def _nativeDerivatedController(self, timeUnit=TimeUnit.Seconds):
		derivatedController = mxs.Float_Script()
		derivatedController.addObject('Integral', self._nativePointer)

		# We can have a time ratio based on seconds of frames.
		t = 't / frameRate' if timeUnit == TimeUnit.Seconds else 't'

		# Making a float script that approximates the derivative of the time curve.
		derivatedController.script = """t = F - 1
										a = (at time t (point2 ({t}) (Integral.value)))
										t = F + 1
										b = (at time t (point2 ({t}) (Integral.value)))
										c = b - a
										c.y / c.x""".format(t=t)
		return derivatedController

	def framesForValue(self, value, closest=True):
		""" Returns a list o frames that match the given controller value.
		
		Args:
		    value (float): The value we want to lookup frame for.
		    closest (bool, optional): This will return the closest value if not value can be found.
		
		Returns:
		    list: The list of matching frames.
		"""

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
					if abs(value - currentValue) < abs(value - closestValue):
						closestValue = currentValue
						closestFrame = frame

				if round(currentValue) == round(value):
					if previousValue is None or abs(value - currentValue) < abs(value - previousValue):
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
import cross3d
cross3d.registerSymbol('SceneAnimationController', StudiomaxSceneAnimationController)
