# 2014.05.21 01:38:31 Central Daylight Time
#Embedded file name: pytz\exceptions.py
"""
Custom exceptions raised by pytz.
"""
__all__ = ['UnknownTimeZoneError',
 'InvalidTimeError',
 'AmbiguousTimeError',
 'NonExistentTimeError']

class UnknownTimeZoneError(KeyError):
    """Exception raised when pytz is passed an unknown timezone.
    
    >>> isinstance(UnknownTimeZoneError(), LookupError)
    True
    
    This class is actually a subclass of KeyError to provide backwards
    compatibility with code relying on the undocumented behavior of earlier
    pytz releases.
    
    >>> isinstance(UnknownTimeZoneError(), KeyError)
    True
    """
    pass


class InvalidTimeError(Exception):
    """Base class for invalid time exceptions."""
    pass


class AmbiguousTimeError(InvalidTimeError):
    """Exception raised when attempting to create an ambiguous wallclock time.
    
    At the end of a DST transition period, a particular wallclock time will
    occur twice (once before the clocks are set back, once after). Both
    possibilities may be correct, unless further information is supplied.
    
    See DstTzInfo.normalize() for more info
    """
    pass


class NonExistentTimeError(InvalidTimeError):
    """Exception raised when attempting to create a wallclock time that
    cannot exist.
    
    At the start of a DST transition period, the wallclock time jumps forward.
    The instants jumped over never occur.
    """
    pass
+++ okay decompyling C:\Users\dalma_000\Dropbox\TT Stuff\TTSC(new)\TTSC(new)\pytz\exceptions.pyc 
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
# 2014.05.21 01:38:31 Central Daylight Time
