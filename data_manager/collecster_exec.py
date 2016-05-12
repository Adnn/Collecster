from inspect import currentframe
import os

def collecster_exec(filename):
    caller_frame = currentframe().f_back
    caller_frame.f_globals["__loader__"] = None
    with open(filename) as f:
        code = compile(f.read(), os.path.abspath(f.name), 'exec')
        exec(code, caller_frame.f_globals, caller_frame.f_locals)
