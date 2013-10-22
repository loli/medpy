"""
@package medpy.utilities.arsparseu
Holds additional functionality for the argparse commandline parser package.

@author Oskar Maier
@version r0.1.1
@since 2013-07-02
@status Release
"""

# build-in modules
import argparse
import itertools

# third-party modules

# own modules

# code
def sequenceOfIntegersGeAscendingStrict(string):
    """
    A custom type for the argparse commandline parser.
    Accepts only colon-separated lists of valid integer values that are greater than or
    equal to 0 and in ascending order.
    
    Usage:
    parser.add_argument('argname', type=sequenceOfIntegersGeAscending, help='help')
    """
    return __sequenceAscendingStrict(__sequenceGe(sequenceOfIntegers(string)))

def sequenceOfIntegers(string):
    """
    A custom type for the argparse commandline parser.
    Accepts only colon-separated lists of valid integer values.

    Usage:
    parser.add_argument('argname', type=sequenceOfIntegers, help='help')

    """
    value = map(int, string.split(','))
    return value

def sequenceOfIntegersGt(string):
    """
    A custom type for the argparse commandline parser.
    Accepts only colon-separated lists of valid integer values that are greater than 0.

    Usage:
    parser.add_argument('argname', type=sequenceOfIntegersGt, help='help')

    """
    value = sequenceOfIntegers(string)
    return __sequenceGt(value)

def sequenceOfIntegersGe(string):
    """
    A custom type for the argparse commandline parser.
    Accepts only colon-separated lists of valid integer values that are greater than or
    equal to 0.

    Usage:
    parser.add_argument('argname', type=sequenceOfIntegersGe, help='help')

    """
    value = sequenceOfIntegers(string)
    return __sequenceGe(value)

def sequenceOfIntegersLt(string):
    """
    A custom type for the argparse commandline parser.
    Accepts only colon-separated lists of valid integer values that are less than 0.

    Usage:
    parser.add_argument('argname', type=sequenceOfIntegersLt, help='help')

    """
    value = sequenceOfIntegers(string)
    return __sequenceLt(value)

def sequenceOfIntegersLe(string):
    """
    A custom type for the argparse commandline parser.
    Accepts only colon-separated lists of valid integer values that are less than or
    equal to 0.

    Usage:
    parser.add_argument('argname', type=sequenceOfIntegersLe, help='help')

    """
    value = sequenceOfIntegers(string)
    return __sequenceLe(value)

def sequenceOfFloats(string):
    """
    A custom type for the argparse commandline parser.
    Accepts only colon-separated lists of valid float values.

    Usage:
    parser.add_argument('argname', type=sequenceOfFloats, help='help')

    """
    value = map(float, string.split(','))
    return value

def sequenceOfFloatsGt(string):
    """
    A custom type for the argparse commandline parser.
    Accepts only colon-separated lists of valid float values that are greater than 0.

    Usage:
    parser.add_argument('argname', type=sequenceOfFloatsGt, help='help')

    """
    value = sequenceOfFloats(string)
    return __sequenceGt(value)

def sequenceOfFloatsGe(string):
    """
    A custom type for the argparse commandline parser.
    Accepts only colon-separated lists of valid float values that are greater than or
    equal to 0.

    Usage:
    parser.add_argument('argname', type=sequenceOfFloatsGe, help='help')

    """
    value = sequenceOfFloats(string)
    return __sequenceGe(value)

def sequenceOfFloatsLt(string):
    """
    A custom type for the argparse commandline parser.
    Accepts only colon-separated lists of valid float values that are less than 0.

    Usage:
    parser.add_argument('argname', type=sequenceOfFloatsLt, help='help')

    """
    value = sequenceOfFloats(string)
    return __sequenceLt(value)

def sequenceOfFloatsLe(string):
    """
    A custom type for the argparse commandline parser.
    Accepts only colon-separated lists of valid float values that are less than or
    equal to 0.

    Usage:
    parser.add_argument('argname', type=sequenceOfFloatsLe, help='help')

    """
    value = sequenceOfFloats(string)
    return __sequenceLe(value)

def __sequenceGt(l):
    "Test a sequences values for being greater than 0."
    for e in l:
        if 0 >= e: raise argparse.ArgumentTypeError('All values have to be greater than 0.')
    return l

def __sequenceGe(l):
    "Test a sequences values for being greater than or equal to 0."
    for e in l:
        if 0 > e: raise argparse.ArgumentTypeError('All values have to be greater than or equal to 0.')
    return l

def __sequenceLt(l):
    "Test a sequences values for being less than 0."
    for e in l:
        if 0 <= e: raise argparse.ArgumentTypeError('All values have to be less than 0.')
    return l

def __sequenceLe(l):
    "Test a sequences values for being less than or equal to 0."
    for e in l:
        if 0 < e: raise argparse.ArgumentTypeError('All values have to be less than or equal to 0.')
    return l

def __sequenceAscendingStrict(l):
    "Test a sequences values to be in strictly ascending order."
    it = iter(l)
    it.next()
    if not all(b > a for a, b in itertools.izip(l, it)):
        raise argparse.ArgumentTypeError('All values must be given in strictly ascending order.')
    return l

def __sequenceDescendingStrict(l):
    "Test a sequences values to be in strictly descending order."
    it = iter(l)
    it.next()
    if not all(b < a for a, b in itertools.izip(l, it)):
        raise argparse.ArgumentTypeError('All values must be given in strictly descending order.')
    return l