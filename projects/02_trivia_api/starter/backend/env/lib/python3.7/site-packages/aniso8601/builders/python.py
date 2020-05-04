# -*- coding: utf-8 -*-

# Copyright (c) 2019, Brandon Nielsen
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the BSD license.  See the LICENSE file for details.

import datetime
import math

from aniso8601.builders import BaseTimeBuilder, TupleBuilder
from aniso8601.exceptions import (DayOutOfBoundsError,
                                  HoursOutOfBoundsError,
                                  LeapSecondError, MidnightBoundsError,
                                  MinutesOutOfBoundsError,
                                  SecondsOutOfBoundsError,
                                  WeekOutOfBoundsError, YearOutOfBoundsError)
from aniso8601.utcoffset import UTCOffset

class PythonTimeBuilder(BaseTimeBuilder):
    @classmethod
    def build_date(cls, YYYY=None, MM=None, DD=None, Www=None, D=None,
                   DDD=None):

        if YYYY is not None:
            #Truncated dates, like '19', refer to 1900-1999 inclusive,
            #we simply parse to 1900
            if len(YYYY) < 4:
                #Shift 0s in from the left to form complete year
                YYYY = YYYY.ljust(4, '0')

            year = cls.cast(YYYY, int,
                            thrownmessage='Invalid year string.')

        if MM is not None:
            month = cls.cast(MM, int,
                             thrownmessage='Invalid month string.')
        else:
            month = 1

        if DD is not None:
            day = cls.cast(DD, int,
                           thrownmessage='Invalid day string.')
        else:
            day = 1

        if Www is not None:
            weeknumber = cls.cast(Www, int,
                                  thrownmessage='Invalid week string.')

            if weeknumber == 0 or weeknumber > 53:
                raise WeekOutOfBoundsError('Week number must be between '
                                           '1..53.')
        else:
            weeknumber = None

        if DDD is not None:
            dayofyear = cls.cast(DDD, int,
                                 thrownmessage='Invalid day string.')
        else:
            dayofyear = None

        if D is not None:
            dayofweek = cls.cast(D, int,
                                 thrownmessage='Invalid day string.')

            if dayofweek == 0 or dayofweek > 7:
                raise DayOutOfBoundsError('Weekday number must be between '
                                          '1..7.')
        else:
            dayofweek = None

        #0000 (1 BC) is not representable as a Python date so a ValueError is
        #raised
        if year == 0:
            raise YearOutOfBoundsError('Year must be between 1..9999.')

        if dayofyear is not None:
            return PythonTimeBuilder._build_ordinal_date(year, dayofyear)
        elif weeknumber is not None:
            return PythonTimeBuilder._build_week_date(year, weeknumber,
                                                      isoday=dayofweek)

        return datetime.date(year, month, day)

    @classmethod
    def build_time(cls, hh=None, mm=None, ss=None, tz=None):
        #Builds a time from the given parts, handling fractional arguments
        #where necessary
        hours = 0
        minutes = 0
        seconds = 0

        floathours = float(0)
        floatminutes = float(0)
        floatseconds = float(0)

        if hh is not None:
            if '.' in hh:
                hours, floathours = cls._split_and_cast(hh, 'Invalid hour string.')
            else:
                hours = cls.cast(hh, int,
                                 thrownmessage='Invalid hour string.')

        if mm is not None:
            if '.' in mm:
                minutes, floatminutes = cls._split_and_cast(mm, 'Invalid minute string.')
            else:
                minutes = cls.cast(mm, int,
                                   thrownmessage='Invalid minute string.')

        if ss is not None:
            if '.' in ss:
                seconds, floatseconds = cls._split_and_cast(ss, 'Invalid second string.')
            else:
                seconds = cls.cast(ss, int,
                                   thrownmessage='Invalid second string.')

        if floathours != 0:
            remainderhours, remainderminutes = cls._split_and_convert(floathours, 60)

            hours += remainderhours
            floatminutes += remainderminutes

        if floatminutes != 0:
            remainderminutes, remainderseconds = cls._split_and_convert(floatminutes, 60)

            minutes += remainderminutes
            floatseconds += remainderseconds

        if floatseconds != 0:
            totalseconds = float(seconds) + floatseconds

            #Truncate to maximum supported precision
            seconds = cls._truncate(totalseconds, 6)

        #Range checks
        if hours == 23 and minutes == 59 and seconds == 60:
            #https://bitbucket.org/nielsenb/aniso8601/issues/10/sub-microsecond-precision-in-durations-is
            raise LeapSecondError('Leap seconds are not supported.')

        if (hours == 24
                and (minutes != 0 or seconds != 0)):
            raise MidnightBoundsError('Hour 24 may only represent midnight.')

        if hours > 24:
            raise HoursOutOfBoundsError('Hour must be between 0..24 with '
                                        '24 representing midnight.')

        if minutes >= 60:
            raise MinutesOutOfBoundsError('Minutes must be less than 60.')

        if seconds >= 60:
            raise SecondsOutOfBoundsError('Seconds must be less than 60.')

        #Fix ranges that have passed range checks
        if hours == 24:
            hours = 0
            minutes = 0
            seconds = 0

        #Datetimes don't handle fractional components, so we use a timedelta
        if tz is not None:
            return (datetime.datetime(1, 1, 1,
                                      hour=hours,
                                      minute=minutes,
                                      tzinfo=cls._build_object(tz))
                    + datetime.timedelta(seconds=seconds)
                   ).timetz()

        return (datetime.datetime(1, 1, 1,
                                  hour=hours,
                                  minute=minutes)
                + datetime.timedelta(seconds=seconds)
               ).time()

    @classmethod
    def build_datetime(cls, date, time):
        return datetime.datetime.combine(cls._build_object(date),
                                         cls._build_object(time))

    @classmethod
    def build_duration(cls, PnY=None, PnM=None, PnW=None, PnD=None, TnH=None,
                       TnM=None, TnS=None):
        years = 0
        months = 0
        days = 0
        weeks = 0
        hours = 0
        minutes = 0
        seconds = 0

        floatyears = float(0)
        floatmonths = float(0)
        floatdays = float(0)
        floatweeks = float(0)
        floathours = float(0)
        floatminutes = float(0)
        floatseconds = float(0)

        if PnY is not None:
            if '.' in PnY:
                years, floatyears = cls._split_and_cast(PnY, 'Invalid year string.')
            else:
                years = cls.cast(PnY, int,
                                 thrownmessage='Invalid year string.')

        if PnM is not None:
            if '.' in PnM:
                months, floatmonths = cls._split_and_cast(PnM, 'Invalid month string.')
            else:
                months = cls.cast(PnM, int,
                                  thrownmessage='Invalid month string.')

        if PnW is not None:
            if '.' in PnW:
                weeks, floatweeks = cls._split_and_cast(PnW, 'Invalid week string.')
            else:
                weeks = cls.cast(PnW, int,
                                 thrownmessage='Invalid week string.')

        if PnD is not None:
            if '.' in PnD:
                days, floatdays = cls._split_and_cast(PnD, 'Invalid day string.')
            else:
                days = cls.cast(PnD, int,
                                thrownmessage='Invalid day string.')

        if TnH is not None:
            if '.' in TnH:
                hours, floathours = cls._split_and_cast(TnH, 'Invalid hour string.')
            else:
                hours = cls.cast(TnH, int,
                                 thrownmessage='Invalid hour string.')

        if TnM is not None:
            if '.' in TnM:
                minutes, floatminutes = cls._split_and_cast(TnM, 'Invalid minute string.')
            else:
                minutes = cls.cast(TnM, int,
                                   thrownmessage='Invalid minute string.')

        if TnS is not None:
            if '.' in TnS:
                seconds, floatseconds = cls._split_and_cast(TnS, 'Invalid second string.')
            else:
                seconds = cls.cast(TnS, int,
                                   thrownmessage='Invalid second string.')

        if floatyears != 0:
            remainderyears, remainderdays = cls._split_and_convert(floatyears, 365)

            years += remainderyears
            floatdays += remainderdays

        if floatmonths != 0:
            remaindermonths, remainderdays = cls._split_and_convert(floatmonths, 30)

            months += remaindermonths
            floatdays += remainderdays

        if floatweeks != 0:
            remainderweeks, remainderdays = cls._split_and_convert(floatweeks, 7)

            weeks += remainderweeks
            floatdays += remainderdays

        if floatdays != 0:
            remainderdays, remainderhours = cls._split_and_convert(floatdays, 24)

            days += remainderdays
            floathours += remainderhours

        if floathours != 0:
            remainderhours, remainderminutes = cls._split_and_convert(floathours, 60)

            hours += remainderhours
            floatminutes += remainderminutes

        if floatminutes != 0:
            remainderminutes, remainderseconds = cls._split_and_convert(floatminutes, 60)

            minutes += remainderminutes
            floatseconds += remainderseconds

        if floatseconds != 0:
            totalseconds = float(seconds) + floatseconds

            #Truncate to maximum supported precision
            seconds = cls._truncate(totalseconds, 6)

        #Note that weeks can be handled without conversion to days
        totaldays = years * 365 + months * 30 + days

        return datetime.timedelta(days=totaldays,
                                  seconds=seconds,
                                  minutes=minutes,
                                  hours=hours,
                                  weeks=weeks)

    @classmethod
    def build_interval(cls, start=None, end=None, duration=None):
        if start is not None and end is not None:
            #<start>/<end>
            startobject = cls._build_object(start)
            endobject = cls._build_object(end)

            return (startobject, endobject)

        durationobject = cls._build_object(duration)

        #Determine if datetime promotion is required
        datetimerequired = (duration[4] is not None
                            or duration[5] is not None
                            or duration[6] is not None
                            or durationobject.seconds != 0
                            or durationobject.microseconds != 0)

        if end is not None:
            #<duration>/<end>
            endobject = cls._build_object(end)
            if end[-1] == 'date' and datetimerequired is True:
                #<end> is a date, and <duration> requires datetime resolution
                return (endobject,
                        cls.build_datetime(end, TupleBuilder.build_time())
                        - durationobject)

            return (endobject,
                    endobject
                    - durationobject)

        #<start>/<duration>
        startobject = cls._build_object(start)

        if start[-1] == 'date' and datetimerequired is True:
            #<start> is a date, and <duration> requires datetime resolution
            return (startobject,
                    cls.build_datetime(start, TupleBuilder.build_time())
                    + durationobject)

        return (startobject,
                startobject
                + durationobject)

    @classmethod
    def build_repeating_interval(cls, R=None, Rnn=None, interval=None):
        startobject = None
        endobject = None

        if interval[0] is not None:
            startobject = cls._build_object(interval[0])

        if interval[1] is not None:
            endobject = cls._build_object(interval[1])

        if interval[2] is not None:
            durationobject = cls._build_object(interval[2])
        else:
            durationobject = endobject - startobject

        if R is True:
            if startobject is not None:
                return cls._date_generator_unbounded(startobject,
                                                     durationobject)

            return cls._date_generator_unbounded(endobject,
                                                 -durationobject)

        iterations = cls.cast(Rnn, int,
                              thrownmessage='Invalid iterations.')

        if startobject is not None:
            return cls._date_generator(startobject, durationobject, iterations)

        return cls._date_generator(endobject, -durationobject, iterations)

    @classmethod
    def build_timezone(cls, negative=None, Z=None, hh=None, mm=None, name=''):
        if Z is True:
            #Z -> UTC
            return UTCOffset(name='UTC', minutes=0)

        if hh is not None:
            tzhour = cls.cast(hh, int,
                              thrownmessage='Invalid hour string.')
        else:
            tzhour = 0

        if mm is not None:
            tzminute = cls.cast(mm, int,
                                thrownmessage='Invalid minute string.')
        else:
            tzminute = 0

        if negative is True:
            return UTCOffset(name=name, minutes=-(tzhour * 60 + tzminute))

        return UTCOffset(name=name, minutes=tzhour * 60 + tzminute)

    @staticmethod
    def _build_week_date(isoyear, isoweek, isoday=None):
        if isoday is None:
            return (PythonTimeBuilder._iso_year_start(isoyear)
                    + datetime.timedelta(weeks=isoweek - 1))

        return (PythonTimeBuilder._iso_year_start(isoyear)
                + datetime.timedelta(weeks=isoweek - 1, days=isoday - 1))

    @staticmethod
    def _build_ordinal_date(isoyear, isoday):
        #Day of year to a date
        #https://stackoverflow.com/questions/2427555/python-question-year-and-day-of-year-to-date
        builtdate = (datetime.date(isoyear, 1, 1)
                     + datetime.timedelta(days=isoday - 1))

        #Enforce ordinal day limitation
        #https://bitbucket.org/nielsenb/aniso8601/issues/14/parsing-ordinal-dates-should-only-allow
        if isoday == 0 or builtdate.year != isoyear:
            raise DayOutOfBoundsError('Day of year must be from 1..365, '
                                      '1..366 for leap year.')

        return builtdate

    @staticmethod
    def _iso_year_start(isoyear):
        #Given an ISO year, returns the equivalent of the start of the year
        #on the Gregorian calendar (which is used by Python)
        #Stolen from:
        #http://stackoverflow.com/questions/304256/whats-the-best-way-to-find-the-inverse-of-datetime-isocalendar

        #Determine the location of the 4th of January, the first week of
        #the ISO year is the week containing the 4th of January
        #http://en.wikipedia.org/wiki/ISO_week_date
        fourth_jan = datetime.date(isoyear, 1, 4)

        #Note the conversion from ISO day (1 - 7) and Python day (0 - 6)
        delta = datetime.timedelta(days=fourth_jan.isoweekday() - 1)

        #Return the start of the year
        return fourth_jan - delta

    @staticmethod
    def _date_generator(startdate, timedelta, iterations):
        currentdate = startdate
        currentiteration = 0

        while currentiteration < iterations:
            yield currentdate

            #Update the values
            currentdate += timedelta
            currentiteration += 1

    @staticmethod
    def _date_generator_unbounded(startdate, timedelta):
        currentdate = startdate

        while True:
            yield currentdate

            #Update the value
            currentdate += timedelta

    @classmethod
    def _split_and_cast(cls, floatstr, thrownmessage):
        #Splits a string with a decimal point into int, and
        #float portions
        intpart, floatpart = floatstr.split('.')

        intvalue = cls.cast(intpart, int,
                            thrownmessage=thrownmessage)

        floatvalue = cls.cast('.' + floatpart, float,
                              thrownmessage=thrownmessage)

        return (intvalue, floatvalue)

    @staticmethod
    def _split_and_convert(f, conversion):
        #Splits a float into an integer, and a converted float portion
        floatpart, integerpart = math.modf(f)

        return (int(integerpart), float(floatpart) * conversion)

    @staticmethod
    def _truncate(f, n):
        #Truncates/pads a float f to n decimal places without rounding
        #https://stackoverflow.com/a/783927
        #This differs from the given implementation in that we expand the string
        #two additional characters, than truncate the resulting string
        #to mitigate rounding effects
        floatstr = repr(f)

        if 'e' in floatstr or 'E' in floatstr:
            expandedfloatstr = '{0:.{1}f}'.format(f, n + 2)
        else:
            integerpartstr, _, floatpartstr = floatstr.partition('.')

            expandedfloatstr = '.'.join([integerpartstr,
                                         (floatpartstr
                                          + '0' * (n + 2))[:n + 2]])

        return float(expandedfloatstr[:expandedfloatstr.index('.') + n + 1])
