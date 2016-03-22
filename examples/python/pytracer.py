import sys
import inspect
from collections import OrderedDict

class TracebackFancy:
	def __init__(self,traceback):
		self.t = traceback

	def getFrame(self):
		return FrameFancy(self.t.tb_frame)

	def getLineNumber(self):
		return self.t.tb_lineno if self.t != None else None

	def getNext(self):
		return TracebackFancy(self.t.tb_next)

	def __str__(self):
		if self.t == None:
			return ""
		str_self = "{0!s} @ {1!s}".format(self.getFrame().getName(), self.getLineNumber())
		return str_self + "\n" + self.getNext().__str__()

class ExceptionFancy:
	def __init__(self,frame):
		self.etraceback = frame.f_exc_traceback
		self.etype = frame.exc_type
		self.evalue = frame.f_exc_value

	def __init__(self,tb,ty,va):
		self.etraceback = tb
		self.etype = ty
		self.evalue = va

	def getTraceback(self):
		return TracebackFancy(self.etraceback)

	def __nonzero__(self):
		return self.etraceback != None or self.etype != None or self.evalue != None

	def getType(self):
		return str(self.etype)

	def getValue(self):
		return self.evalue

class CodeFancy:
	def __init__(self,code):
		self.c = code

	def getArgCount(self):
		return self.c.co_argcount if self.c != None else 0

	def getFilename(self):
		return self.c.co_filename if self.c != None else ""

	def getVariables(self):
		return self.c.co_varnames if self.c != None else []

	def getName(self):
		return self.c.co_name if self.c != None else ""

	def getFileName(self):
		return self.c.co_filename if self.c != None else ""

class ArgsFancy:
	def __init__(self,frame,arginfo):
		self.f = frame
		self.a = arginfo

	def __str__(self):
		args, varargs, kwargs = self.getArgs(), self.getVarArgs(), self.getKWArgs()
		ret = ""
		count = 0
		size = len(args)
		for arg in args:
			ret = ret + ("{0!s} = {1!s}".format(arg, args[arg]))
			count = count + 1
			if count < size:
				ret = ret + ", "
		if varargs:
			if size > 0:
				ret = ret + " "
			ret = ret + "varargs are " + str(varargs)
		if kwargs:
			if size > 0:
				ret = ret + " "
			ret = ret + "kwargs are " + str(kwargs)
		return ret

	def getNumArgs(wantVarargs = False, wantKWArgs=False):
		args, varargs, keywords, values = self.a
		size = len(args)
		if varargs and wantVarargs:
			size = size+len(self.getVarArgs())
		if keywords and wantKWArgs:
			size = size+len(self.getKWArgs())
		return size

	def getArgs(self):
		args, _, _, values = self.a
		argWValues = OrderedDict()
		for arg in args:
			argWValues[arg] = values[arg]
		return argWValues

	def getVarArgs(self):
		_, vargs, _, _ = self.a
		if vargs:
			return self.f.f_locals[vargs]
		return ()

	def getKWArgs(self):
		_, _, kwargs, _ = self.a
		if kwargs:
			return self.f.f_locals[kwargs]
		return {}

class FrameFancy:
	def __init__(self,frame):
		self.f = frame

	def getCaller(self):
		return FrameFancy(self.f.f_back)

	def getLineNumber(self):
		return self.f.f_lineno if self.f != None else 0

	def getCodeInformation(self):
		return CodeFancy(self.f.f_code) if self.f != None else None

	def getExceptionInfo(self):
		return ExceptionFancy(self.f) if self.f != None else None

	def getName(self):
		return self.getCodeInformation().getName() if self.f != None else ""

	def getFileName(self):
		return self.getCodeInformation().getFileName() if self.f != None else ""

	def getLocals(self):
		return self.f.f_locals if self.f != None else {}
		
	def getArgumentInfo(self):
		return ArgsFancy(self.f,inspect.getargvalues(self.f)) if self.f != None else None

class TracerClass:
	def callEvent(self,frame):
		pass

	def lineEvent(self,frame):
		pass

	def returnEvent(self,frame,retval):
		pass

	def exceptionEvent(self,frame,exception,value,traceback):
		pass

	def cCallEvent(self,frame,cfunct):
		pass

	def cReturnEvent(self,frame,cfunct):
		pass

	def cExceptionEvent(self,frame,cfunct):
		pass

tracer_impl = TracerClass()


def the_tracer_entrypoint(frame,event,args):
	if tracer_impl == None:
		return None
	if event == "call":
		call_retval = tracer_impl.callEvent(FrameFancy(frame))
		if call_retval == False:
			return None
		return the_tracer_entrypoint
	elif event == "line":
		line_retval = tracer_impl.lineEvent(FrameFancy(frame))
		if line_retval == False:
			return None
		return the_tracer_entrypoint
	elif event == "return":
		tracer_impl.returnEvent(FrameFancy(frame),args)
	elif event == "exception":
		exty,exva,extb = args
		exception_retval = tracer_impl.exceptionEvent(FrameFancy(frame),ExceptionFancy(extb,exty,exva))
		if exception_retval == False:
			return None
		return the_tracer_entrypoint
	elif event == "c_call":
		tracer_impl.cCallEvent(FrameFancy(frame),args)
	elif event == "c_return":
		tracer_impl.cReturnEvent(FrameFancy(frame),args)
	elif event == "c_exception":
		tracer_impl.cExceptionEvent(FrameFancy(frame),args)
	return None

def enable(t=None):
	global tracer_impl
	if t:
		tracer_impl = t
	sys.settrace(the_tracer_entrypoint)

def disable():
	sys.settrace(None)

class LoggingTracer:
	def callEvent(self,frame):
		print "call " + frame.getName() + " from " + frame.getCaller().getName() + " @ " + str(frame.getCaller().getLineNumber()) + " args are " + str(frame.getArgumentInfo())

	def lineEvent(self,frame):
		print "running " + frame.getName() + " @ " + str(frame.getLineNumber()) + " locals are " + str(frame.getLocals()) + " in " + frame.getFileName()

	def returnEvent(self,frame,retval):
		print "return from " + frame.getName() + " value is " + str(retval) + " locals are " + str(frame.getLocals())

	def exceptionEvent(self,frame,exception):
		print "exception {0!s} {1!s} raised from {2!s} @ {3!s}".format(exception.getType(), str(exception.getValue()), frame.getName(), frame.getLineNumber())
		print "tb: " + str(exception.getTraceback())

# the same functionality as LoggingTracer, but with a little more lldb-specific smarts
class LLDBAwareTracer:
	def callEvent(self,frame):
		if frame.getName() == "<module>":
			return
		if frame.getName() == "run_one_line":
			print "call run_one_line({0!s})".format((frame.getArgumentInfo().getArgs()["input_string"]))
			return
		if "Python.framework" in frame.getFileName():
			print "call into Python at " + frame.getName()
			return
		if frame.getName() == "__init__" and frame.getCaller().getName() == "run_one_line" and frame.getCaller().getLineNumber() == 101:
			return False
		strout = "call " + frame.getName()
		if (frame.getCaller().getFileName() == ""):
			strout += " from LLDB - args are "
			args = frame.getArgumentInfo().getArgs()
			for arg in args:
				if arg == "dict" or arg == "internal_dict":
					continue
				strout = strout + ("{0!s} = {1!s} ".format(arg, args[arg]))
		else:
			strout += " from " + frame.getCaller().getName() + " @ " + str(frame.getCaller().getLineNumber()) + " args are " + str(frame.getArgumentInfo())
		print strout

	def lineEvent(self,frame):
		if frame.getName() == "<module>":
			return
		if frame.getName() == "run_one_line":
			print "running run_one_line({0!s}) @ {1!s}".format(frame.getArgumentInfo().getArgs()["input_string"], frame.getLineNumber())
			return
		if "Python.framework" in frame.getFileName():
			print "running into Python at " + frame.getName() + " @ " + str(frame.getLineNumber())
			return
		strout = "running " + frame.getName() + " @ " + str(frame.getLineNumber()) + " locals are " 
		if (frame.getCaller().getFileName() == ""):
			locals = frame.getLocals()
			for local in locals:
				if local == "dict" or local == "internal_dict":
					continue
				strout = strout + ("{0!s} = {1!s} ".format(local, locals[local]))
		else:
			strout = strout + str(frame.getLocals())
		strout = strout + " in " + frame.getFileName()
		print strout

	def returnEvent(self,frame,retval):
		if frame.getName() == "<module>":
			return
		if frame.getName() == "run_one_line":
			print "return from run_one_line({0!s}) return value is {1!s}".format(frame.getArgumentInfo().getArgs()["input_string"], retval)
			return
		if "Python.framework" in frame.getFileName():
			print "return from Python at " + frame.getName() + " return value is " + str(retval)
			return
		strout = "return from " + frame.getName() + " return value is " + str(retval) + " locals are "
		if (frame.getCaller().getFileName() == ""):
			locals = frame.getLocals()
			for local in locals:
				if local == "dict" or local == "internal_dict":
					continue
				strout = strout + ("{0!s} = {1!s} ".format(local, locals[local]))
		else:
			strout = strout + str(frame.getLocals())
		strout = strout + " in " + frame.getFileName()
		print strout

	def exceptionEvent(self,frame,exception):
		if frame.getName() == "<module>":
			return
		print "exception {0!s} {1!s} raised from {2!s} @ {3!s}".format(exception.getType(), str(exception.getValue()), frame.getName(), frame.getLineNumber())
		print "tb: " + str(exception.getTraceback())

def f(x,y=None):
	if x > 0:
		return 2 + f(x-2)
	return 35

def g(x):
	return 1.134 / x

def print_keyword_args(**kwargs):
     # kwargs is a dict of the keyword args passed to the function
     for key, value in kwargs.iteritems():
         print "{0!s} = {1!s}".format(key, value)

def total(initial=5, *numbers, **keywords):
    count = initial
    for number in numbers:
        count += number
    for key in keywords:
        count += keywords[key]
    return count

if __name__ == "__main__":
	enable(LoggingTracer())
	f(5)
	f(5,1)
	print_keyword_args(first_name="John", last_name="Doe")
	total(10, 1, 2, 3, vegetables=50, fruits=100)
	try:
		g(0)
	except:
		pass
	disable()
