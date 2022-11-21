import atexit, termios
import sys, os
import time


old_settings=None

def init_any_key():
   global old_settings
   old_settings = termios.tcgetattr(sys.stdin)
   new_settings = termios.tcgetattr(sys.stdin)
   new_settings[3] = new_settings[3] & ~(termios.ECHO | termios.ICANON) # lflags
   new_settings[6][termios.VMIN] = 0  # cc
   new_settings[6][termios.VTIME] = 0 # cc
   termios.tcsetattr(sys.stdin, termios.TCSADRAIN, new_settings)


@atexit.register
def term_any_key():
   global old_settings
   if old_settings:
      termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def any_key():
   ch_get = []
   ch = os.read(sys.stdin.fileno(), 1)
   while ch is not None and len(ch) > 0:
      ch_get.append( chr(ch[0]) )
      ch = os.read(sys.stdin.fileno(), 1)
   return ch_get


init_any_key()
end_time = time.time()
while time.time() < end_time + 5.0:
   key = any_key()
   if len(key) > 0:
      print(key)
   else:
      time.sleep(0.1)