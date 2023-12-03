import cv2

class Mouse(object):

   _X = 0
   _Y = 0
   _command = False
   _shift = False
   _option = False
   _alt = False
   _leftDown = False
   _rightDown = False
   _middleDown = False
   _leftUp = False
   _rightUp = False
   _middleUp = False
   _leftDoubleClick = False
   _rightDoubleClick = False
   _middleDoubleClick = False

   def __init__(self, windowName):
      cv2.setMouseCallback(windowName, self._on_mouse)

   @staticmethod
   def command():
      return Mouse._command

   @staticmethod
   def shift():
      return Mouse._shift

   @staticmethod
   def option():
      return Mouse._option

   @staticmethod
   def alt():
      return Mouse._alt

   @staticmethod
   def left_down():
      return Mouse._leftDown

   @staticmethod
   def right_down():
      return Mouse._rightDown

   @staticmethod
   def middle_down():
      return Mouse._middleDown

   @staticmethod
   def left_up():
      return Mouse._leftUp

   @staticmethod
   def right_up():
      return Mouse._rightUp

   @staticmethod
   def middle_up():
      return Mouse._middleUp

   @staticmethod
   def left_double_click():
      return Mouse._leftDoubleClick

   @staticmethod
   def right_double_click():
      return Mouse._rightDoubleClick

   @staticmethod
   def middle_double_click():
      return Mouse._middleDoubleClick

   @staticmethod
   def clear():
      Mouse._command = False
      Mouse._shift = False
      Mouse._option = False
      Mouse._alt = False
      Mouse._leftDown = False
      Mouse._rightDown = False
      Mouse._middleDown = False
      Mouse._leftUp = False
      Mouse._rightUp = False
      Mouse._middleUp = False
      Mouse._leftDoubleClick = False
      Mouse._rightDoubleClick = False
      Mouse._middleDoubleClick = False

   @staticmethod
   def coordinate():
      return Mouse._X, Mouse._Y

   @staticmethod
   def _on_mouse(event, x, y, flags, params):
      """
      event (Enumerations)
         (0) - CV_EVENT_MOUSEMOVE
         (1) - CV_EVENT_LBUTTONDOWN
         (2) - CV_EVENT_RBUTTONDOWN
         (3) - CV_EVENT_MBUTTONDOWN
         (4) - CV_EVENT_LBUTTONUP
         (5) - CV_EVENT_RBUTTONUP
         (6) - CV_EVENT_MBUTTONUP
         (7) - CV_EVENT_LBUTTONDBLCLK
         (8) - CV_EVENT_RBUTTONDBLCLK
         (9) - CV_EVENT_MBUTTONDBLCLK
      flags
         00000001  (1) - Left Button
         00000010  (2) - Right Button
         00000100  (4) - Middle Button
         00001001  (9) - Command-Left Button
         00001010 (10) - Command-Right Button
         00001100 (12) - Command-Middle Button
         00010001 (17) - Shift-Left Button
         00010010 (18) - Shift-Right Button
         00010100 (20) - Shift-Middle Button
         00100001 (33) - Option/Alt-Left Button
         00100010 (34) - Option/Alt-Right Button
         00100100 (36) - Option/Alt-Middle Button
      """
      Mouse._X = x
      Mouse._Y = y

      if flags & 8: # COMMAND
         Mouse._command = True
      if flags & 16: # SHIFT
         Mouse._shift = True
      if flags & 32: # OPTION/ALT
         Mouse._option = True
         Mouse._alt = True

      if event == cv2.EVENT_MOUSEMOVE:
         pass
      elif event == cv2.EVENT_LBUTTONDOWN:
         Mouse._leftDown = True
      elif event == cv2.EVENT_RBUTTONDOWN:
         Mouse._rightDown = True
      elif event == cv2.EVENT_MBUTTONDOWN:
         Mouse._middleDown = True
      elif event == cv2.EVENT_LBUTTONUP:
         Mouse._leftUp = True
      elif event == cv2.EVENT_RBUTTONUP:
         Mouse._rightUp = True
      elif event == cv2.EVENT_MBUTTONUP:
         Mouse._middleUp = True
      elif event == cv2.EVENT_LBUTTONDBLCLK:
         Mouse._leftDoubleClick = True
      elif event == cv2.EVENT_RBUTTONDBLCLK:
         Mouse._rightDoubleClick = True
      elif event == cv2.EVENT_MBUTTONDBLCLK:
         Mouse._middleDoubleClick = True
      else:
         msg = 'Unrecognized mouse event encountered ({0})'.format(event)
         raise ValueError(msg)
