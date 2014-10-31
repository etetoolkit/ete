try:
    import numpy
except ImportError:
    mean = numpy.mean
else:
    mean = lambda v: sum(v)/len(v)
