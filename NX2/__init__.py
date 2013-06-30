'''Module to load, analyze ans plot data taken with out Roman warships.
'''
from .NX2 import read_NX2, NX2Table
from atpy.registry import register_reader
register_reader('nx2', read_NX2, override = True)
