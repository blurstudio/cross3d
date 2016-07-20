##
#   :namespace  rescaletime
#
#   :remarks    This is a Hack to provide script access to the Re-Scale Time option in the maxscipt interface.
#				It is not available through Maxscript
#   
#   :author     mikeh
#   :author     Blur Studio
#   :date       12/04/12
#

from win32gui import *
from win32api import *
import win32con
from Py3dsMax import GetWindowHandle, mxs
from PyQt4.QtCore import QRect, QPoint, QTimer, pyqtSignal, QObject

class RescaleTime(QObject):
	virtualKeyMap = {'del':0x2e, '0':0x30, '1':0x31, '2':0x32, '3':0x33, '4':0x34, '5':0x35, '6':0x36, '7':0x37, '8':0x38, '9':0x39}
	hardwareKeyMap = {'del':0xE0, '0':0x0B, '1':0x02, '2':0x03, '3':0x04, '4':0x05, '5':0x06, '6':0x07, '7':0x08, '8':0x09, '9':0x0A}
	# Listen for this signal to be emitted when calling scaleTime. scaleTime is using QTimers to wait for window animation
	# so the code execution does not block code exicution moving foward. The int value provided is the framerate requested,
	# it can be used to check if the change was successfull.
	scaleTimeFinished = pyqtSignal(int)

	def __init__(self):
		super(RescaleTime, self).__init__()
		self.minimzedWindows = []
		self.endTimeValue = 0
		self.timerDelay = 50
		self.useTimers = False
		self.uiWarningWND = None
		self.restoreMaxWindow = False

	def scaleTime(self, value):
		"""
		Uses the Mouse and keyboard to rescale the max timeline to value. This is a hack to add script
		functionality that maxscript has been lacking for at least 2 years.
		"""
		# Max does not expect floats for this value
		self.endTimeValue = int(value)
		self.useTimers = True
		self.maximizeMax()

	def warningDialog(self, parent, title='FPS', msg='Adjusting frame rate,\n please wait...'):
		from cross3d.migrate import Window
		# Tell the user what is going on and that they should wait for it to complete.
		# Because of the this system works it can not block keyboard and mouse input to Max
		# TODO: Re-build this in a generic non-blurdev specific way.
		if Window:
			from PyQt4.QtGui import QLabel
			self.uiWarningWND = Window()
			self.uiWarningWND.setWindowTitle(title)
			x,y,w,h = GetWindowRect(parent)
			self.uiWarningWND.setGeometry(x+15, y+40, 303, 80)
			lbl = QLabel(self.uiWarningWND)
			fnt = lbl.font()
			fnt.setPointSize(20)
			lbl.setGeometry(0,0,300,86)
			lbl.setFont(fnt)
			lbl.setText(msg)
			self.uiWarningWND.show()

	@staticmethod
	def EnumWindowsProc(hwnd,list):
		list.append(hwnd)

	def findThreadWindow(self, name):
		hwnds = []
		threadID = GetCurrentThreadId()
		EnumThreadWindows( threadID, self.EnumWindowsProc, hwnds)
		for hwnd in hwnds: 
			if GetWindowText(hwnd) == name:
				tcDlg = hwnd
				break
		else:
#			print 'Unable to find the %s window' % name
			return None
		return tcDlg

	def clickPoint(self, id):
		if id:
			pnt = ClientToScreen(id,(5,5))
#			print 'ClickPoint', pnt
			currentCursorPos = GetCursorPos()
			SetCursorPos(pnt)
			mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,pnt[0],pnt[1],0,0)
			mouse_event(win32con.MOUSEEVENTF_LEFTUP,pnt[0],pnt[1],0,0)
			SetCursorPos(currentCursorPos)
			mxs.setWaitCursor()
#		else:
#			print "Could not find window to click on"

	def pressKey(self, key):
		keybd_event(self.virtualKeyMap[key], self.hardwareKeyMap[key], 0, 0)
		keybd_event(self.virtualKeyMap[key], self.hardwareKeyMap[key], win32con.KEYEVENTF_KEYUP, 0)

	def clearInput(self, count=9):
		for i in range(count):
			self.pressKey('del')

	def typeNumber(self, number):
		for char in str(number):
			self.pressKey(char)
	
	def minimizeWindows(self, id):
		hwnds = []
		maxHwnd = GetWindowHandle()
		threadID = GetCurrentThreadId()
		EnumThreadWindows( threadID, self.EnumWindowsProc, hwnds)
		pnt = ClientToScreen(id,(5,5))
		pnt = QPoint(pnt[0], pnt[1])
		for hwnd in hwnds:
			if hwnd != maxHwnd:
				rect = GetWindowRect(hwnd)
				if QRect(QPoint(rect[0], rect[1]), QPoint(rect[2], rect[3])).contains(pnt) and IsWindowVisible(hwnd):
#					print hwnd, GetWindowRect(hwnd), GetWindowText(hwnd), GetClassName(hwnd), IsWindowVisible(hwnd)
					self.minimzedWindows.append(hwnd)
					ShowWindow( hwnd, win32con.SW_MINIMIZE )
		
	def restoreWindows(self):
		for hwnd in self.minimzedWindows:
			ShowWindow( hwnd, win32con.SW_RESTORE )
		self.minimzedWindows = []
	
	def maximizeMax(self):
		"""
			Maximize max to ensure that the Time Configuration button is on the monitor and clickable, and to 
			ensure that the dialogs will be on screen.
		"""
		self.restoreMaxWindow = False
		maxHwnd = GetWindowHandle()
		if GetWindowPlacement(maxHwnd)[1] == win32con.SW_SHOWNORMAL:
			ShowWindow( maxHwnd, win32con.SW_MAXIMIZE )
			self.restoreMaxWindow = True
			QTimer.singleShot(self.timerDelay, self.mouseToTimeButton)
			return
		self.mouseToTimeButton()
	
	def mouseToTimeButton(self):
		mxs.setWaitCursor()
		maxHwnd = GetWindowHandle()
		if self.useTimers:
			self.warningDialog(maxHwnd)
		hwnds = []
		EnumChildWindows(maxHwnd,self.EnumWindowsProc,hwnds)
		stack = [maxHwnd]
		depth = 0
		tpDepth = 0
		tpChildren = []
		for hwnd in hwnds:
			while len(stack) > 1 and GetParent(hwnd) != stack[-1]:
				del stack[-1]
				if tpDepth > 0:
					tpDepth -= 1
			if tpDepth == 1:
				tpChildren.append((hwnd,GetWindowRect(hwnd)[1]))
#			if tpDepth:
#				print '\t'*len(stack), hwnd, GetClassName(hwnd), GetWindowRect(hwnd)
			stack.append(hwnd)
			if tpDepth or GetClassName(hwnd) == 'TimePanel':
				tpDepth += 1
		timeButtonParent = None
		# It's probably always the second in line but we'll compare their y-coords just in case
		if len(tpChildren) == 2:
			if tpChildren[0][1] > tpChildren[1][1]:
				timeButtonParent = tpChildren[0][0]
			else:
				timeButtonParent = tpChildren[1][0]
		else:
#			print "Couldn't find the CustToolbar that is the parent of the time button"
			return
#		print "Found timeButtonParent", timeButtonParent
		hwnds = []
		EnumChildWindows(timeButtonParent,self.EnumWindowsProc,hwnds)
		timeButton, timeButtonX = None, None
		# Time Button is left most child of the CustToolbar
		for hwnd in hwnds:
			if GetClassName(hwnd) != 'CustButton':
				continue
			xPos = GetWindowRect(hwnd)[0]
			if timeButtonX is None or xPos > timeButtonX:
				timeButton = hwnd
				timeButtonX = xPos
		try:
			SetForegroundWindow(maxHwnd)
		except:
			import cross3d
			cross3d.logger.debug('Unable to set forground window to max')
		SetActiveWindow (maxHwnd)
		self.minimizeWindows(timeButton)
		self.clickPoint(timeButton)
		# Allow the window to appear before continuing
		if self.useTimers:
			QTimer.singleShot(self.timerDelay, self.mouseToReScaleButton)
		else:
			# scale time failed, emit callback so caller can reset the values.
			self.scaleTimeFinished.emit(self.endTimeValue)

	def mouseToReScaleButton(self):
		mxs.setWaitCursor()
		tcDlg = self.findThreadWindow('Time Configuration')
#		print tcDlg
		hwnds = []
		EnumChildWindows(tcDlg,self.EnumWindowsProc,hwnds)
		shwnd = None
		for hwnd in hwnds:
			if GetWindowText(hwnd) == 'Re-scale Time':
#				print 'Found re-scale time!----------------------------------------', hwnd
				shwnd = hwnd
				break
		self.clickPoint(shwnd)
		# Allow the window to appear before continuing
		if self.useTimers:
			QTimer.singleShot(self.timerDelay, self.mouseToEndTime)
		else:
			# scale time failed, emit callback so caller can reset the values.
			self.scaleTimeFinished.emit(self.endTimeValue)

	def mouseToEndTime(self):
		mxs.setWaitCursor()
		rstDlg = self.findThreadWindow('Re-scale Time')
		labelRect = None
		labelHwnd = None
		hwnds = []
		EnumChildWindows(rstDlg, self.EnumWindowsProc, hwnds)
		endTimeEdit = None
		okBtn = None
		# use the text label to find the edit
		for hwnd in hwnds:
			if GetWindowText(hwnd) == 'End Time:':
				labelRect = GetWindowRect(hwnd)
				labelHwnd = hwnd
#				print 'Found End Time label', labelHwnd, labelRect
			elif GetWindowText(hwnd) == "OK":
				okBtn = hwnd
#				print 'Found the Ok Button', hwnd
			if okBtn and labelRect:
				break
		if labelRect:
			for hwnd in hwnds:
				if hwnd != labelHwnd:
					left, top, right, bottom = GetWindowRect(hwnd)
					# use the text label's geometry to identify the custom edit
					if top >= labelRect[1] and top <= labelRect[3] and GetClassName(hwnd) == 'CustEdit':
#						print 'Clicking on', hwnd, GetClassName(hwnd)
						endTimeEdit = hwnd
						break
		if endTimeEdit:
			self.clickPoint(hwnd)
			# Clear out the current value
			self.clearInput()
			self.typeNumber(self.endTimeValue)
			self.clickPoint(okBtn)
			# This is neccissary to allow Thinking Particles time to update when the endTimeValue
			# is updated.
			# TODO: Investigate if this can replace the QTimers.
			mxs.windows.processPostedMessages()
			# Allow the window to appear before continuing
			if self.useTimers:
				QTimer.singleShot(self.timerDelay, self.mouseToTimeConfigOk)
				return
		# scale time failed, emit callback so caller can reset the values.
		self.scaleTimeFinished.emit(self.endTimeValue)

	def mouseToTimeConfigOk(self):
		mxs.setWaitCursor()
		tcDlg = self.findThreadWindow('Time Configuration')
#		print tcDlg
		hwnds = []
		EnumChildWindows(tcDlg,self.EnumWindowsProc,hwnds)
		shwnd = None
		for hwnd in hwnds:
			if GetWindowText(hwnd) == 'OK':
#				print 'Found OK Button!----------------------------------------', hwnd
				shwnd = hwnd
				break
		self.clickPoint(shwnd)
		self.restoreWindows()
		if self.useTimers:
			QTimer.singleShot(self.timerDelay, self.finishScaling)
		else:
			# scale time failed, emit callback so caller can reset the values.
			self.scaleTimeFinished.emit(self.endTimeValue)
	
	def finishScaling(self):
		if self.useTimers:
			self.scaleTimeFinished.emit(self.endTimeValue)
			if self.restoreMaxWindow:
				ShowWindow( GetWindowHandle(), win32con.SW_RESTORE )
			mxs.setArrowCursor()
			if self.uiWarningWND:
				QTimer.singleShot(1000, self.uiWarningWND.close)
		self.useTimers = False
