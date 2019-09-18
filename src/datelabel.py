"""Classes and utility methods for dealing with dates as expressed in filenames 
and paths. Intended use case is, eg, determining if a file contains data for a
given year from the filename, without having to open it and parse the header.

Note:
    These classes should *not* be used for calendar math! We currently implement
    and test comparison logic only, not anything more (eg addition, subtraction).
"""
import re
import datetime

class DateLabel(datetime.datetime):
    """Define a date with variable level precision.
    """
    # define __new__, not __init__, because datetime is immutable
    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and type(args[0]) is str:
            args = cls._parse_input_string(args[0])
        precision = len(args)
        if precision == 1:
            args = (args[0], 1, 1) # missing month & day
        elif precision == 2:
            args = (args[0], args[1], 1) # missing day
        obj = super(DateLabel, cls).__new__(cls, *args, **kwargs) 
        obj.precision = precision
        return obj

    @classmethod
    def _parse_input_string(cls, s):
        """Define a date and precision level from a string in YYYYMMDDHH format.
        """
        if len(s) == 4:
            return (int(s[0:4]), )
        elif len(s) == 6: 
            return (int(s[0:4]), int(s[4:6]))
        elif len(s) == 8: 
            return (int(s[0:4]), int(s[4:6]), int(s[6:8]))
        elif len(s) == 10: 
            return (int(s[0:4]), int(s[4:6]), int(s[6:8]), int(s[8:10]))
        else:
            raise ValueError("Malformed input {}".format(s))

    def label_format(self):
        """Print date in YYYYMMDDHH format, with length being set automatically
        from precision. 
        
        Other formats can be obtained manually with `strftime`.
        """
        if self.precision == 1:
            return self.strftime('%Y')
        elif self.precision == 2:
            return self.strftime('%Y%m')
        elif self.precision == 3:
            return self.strftime('%Y%m%d')
        elif self.precision == 4:
            return self.strftime('%Y%m%d%H')
        else:
            raise ValueError("Malformed input")

    def __lt__(self, other):
        """Overload datetime.datetime's __lt__. Coerce to datetime.date if we're
        comparing with a datetime.date.
        """
        if isinstance(other, datetime.datetime):
            return super(DateLabel, self).__lt__(other)
        else:
            return (self.date() < other)

    def __le__(self, other):
        """Overload datetime.datetime's __le__. Coerce to datetime.date if we're
        comparing with a datetime.date.
        """
        if isinstance(other, datetime.datetime):
            return super(DateLabel, self).__le__(other)
        else:
            return (self.date() <= other)

    def __gt__(self, other):
        """Overload datetime.datetime's __gt__. Coerce to datetime.date if we're
        comparing with a datetime.date.
        """
        if isinstance(other, datetime.datetime):
            return super(DateLabel, self).__gt__(other)
        else:
            return (self.date() > other)

    def __ge__(self, other):
        """Overload datetime.datetime's __ge__. Coerce to datetime.date if we're
        comparing with a datetime.date.
        """
        if isinstance(other, datetime.datetime):
            return super(DateLabel, self).__ge__(other)
        else:
            return (self.date() >= other)

    def __eq__(self, other):
        """Overload datetime.datetime's __eq__. Require precision to match as
        well as date. Coerce to datetime.date if we're comparing with a datetime.date.
        """
        if isinstance(other, DateLabel):
            return (self.precision == other.precision) and super(DateLabel, self).__eq__(other)
        elif isinstance(other, datetime.datetime):
            return super(DateLabel, self).__eq__(other)
        else:
            return (self.date() == other)

    def __ne__(self, other):
        """Overload datetime.datetime's __ne__. Require precision to match as
        well as date. Coerce to datetime.date if we're comparing with a datetime.date.
        """
        if isinstance(other, DateLabel):
            return (self.precision != other.precision) or super(DateLabel, self).__ne__(other)
        elif isinstance(other, datetime.datetime):
            return super(DateLabel, self).__ne__(other)
        else:
            return (self.date() != other)


class DateLabelRange(object):
    """Class representing a range of dates. 

    This is defined as a closed interval (containing both endpoints).
    """
    def __init__(self, start, end=None):
        if type(start) is str and (end is None):
            (start, end) = self._parse_input_string(start)

        if not isinstance(start, DateLabel):
            start = DateLabel(start)
        if not isinstance(end, DateLabel):
            end = DateLabel(end)
        assert start < end

        self.start = start
        self.end = end

    @classmethod
    def _parse_input_string(cls, s):
        s2 = s.split('-')
        assert len(s2) == 2
        return tuple([DateLabel(ss) for ss in s2])
    
    def __eq__(self, other):
        return (self.start == other.start) and (self.end == other.end)

    def __ne__(self, other):
        return (self.start != other.start) or (self.end != other.end)

    def __contains__(self, item): 
        return self.overlaps(item)
    def overlaps(self, item):
        """Comparison returning `True` if `item` has any overlap at all with the
        date range.

        This method overrides the `__contains__` method, so, e.g., 
        datetime.date('2019-09-18') in DateLabelRange('2018-2019') will give
        `True`.
        """
        if isinstance(item, DateLabelRange):
            return (self.start <= item.end) and (item.start <= self.end)
        else:
            return (self.start <= item) and (self.end >= item)

    def contains(self, item):
        """Comparison returning `True` if `item` is strictly contained within 
        the range.
        """
        if isinstance(item, DateLabelRange):
            return (self.start <= item.start) and (self.end >= item.end)
        else:
            return (self.start <= item) and (self.end >= item)
    
    def label_format(self):
        return self.start.label_format() + '-' + self.end.label_format()
        

class DateLabelFrequency(datetime.timedelta):
    """Class representing a date frequency or period.

    Note:
        Period lengths are *not* defined accurately, eg. a year is taken as
        365 days and a month is taken as 30 days. 
    """
    # define __new__, not __init__, because timedelta is immutable
    def __new__(cls, quantity, unit=''):
        if (type(quantity) is str) and (unit == ''):
            (quantity, unit) = cls._parse_input_string(quantity)
        if (type(quantity) is not int) or (type(unit) is not str):
            raise ValueError("Malformed input")
        else:
            unit = unit.lower()

        if unit[0] == 'y':
            kwargs = {'days': 365 * quantity}
            unit = 'yr'
        elif unit[0] == 's':
            kwargs = {'days': 91 * quantity}
            unit = 'se'
        elif unit[0] == 'm':
            kwargs = {'days': 30 * quantity}
            unit = 'mo'
        elif unit[0] == 'w':
            kwargs = {'days': 7 * quantity}
            unit = 'wk'
        elif unit[0] == 'd':
            kwargs = {'days': quantity}
            unit = 'dy'
        elif unit[0] == 'h':
            kwargs = {'hours': quantity}
            unit = 'hr'
        else:
            raise ValueError("Malformed input")
        obj = super(DateLabelFrequency, cls).__new__(cls, **kwargs) 
        obj.quantity = quantity
        obj.unit = unit
        return obj
        
    @classmethod    
    def _parse_input_string(cls, s):
        match = re.match(r"(?P<quantity>\d+)[ _]*(?P<unit>[a-zA-Z]+)", s)
        if match:
            quantity = int(match.group('quantity'))
            unit = match.group('unit')
        else:
            quantity = 1
            if s in ['yearly', 'year', 'y', 'annually', 'annual', 'ann']:
                unit = 'yr'
            elif s in ['seasonally', 'seasonal', 'season']:      
                unit = 'se'
            elif s in ['monthly', 'month', 'mon', 'mo']:      
                unit = 'mo'
            elif s in ['weekly', 'week', 'wk', 'w']:
                unit = 'wk'
            elif s in ['daily', 'day', 'd', 'diurnal', 'diurnally']:
                unit = 'dy' 
            elif s in ['hourly', 'hour', 'hr', 'h']:
                unit = 'hr' 
            else:
                raise ValueError("Malformed input {}".format(s))
        return (quantity, unit)

    def format_adj(self):
        # weekly not used in frepp
        assert self.quantity == 1
        _frepp_dict = {
            'yr': 'annual',
            'se': 'seasonal',
            'mo': 'monthly',
            'da': 'daily',
            'hr': 'hourly'
        }
        return _frepp_dict[self.unit]

    def format(self):
        # conversion? only hr and yr used
        return "{}{}".format(self.quantity, self.unit)

    def __eq__(self, other):
        # Note: only want to match labels, don't want '24hr' == '1day'
        if isinstance(other, DateLabelFrequency):
            return (self.quantity == other.quantity) and (self.unit == other.unit)
        else:
            return super(DateLabelFrequency, self).__eq__(other)

    def __ne__(self, other):
        # Note: only want to match labels, don't want '24hr' == '1day'
        if isinstance(other, DateLabelFrequency):
            return (self.quantity != other.quantity) or (self.unit != other.unit)
        else:
            return super(DateLabelFrequency, self).__ne__(other)
