import re
from math import modf
from datetime import datetime, timedelta



## {{{ http://code.activestate.com/recipes/65215/ (r5)
def is_valid_email(s):
    return (s and len(s) > 7 and
            re.match('''^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]
                    {1,3})(\\]?)$''', s))
## end of http://code.activestate.com/recipes/65215/ }}}




def timestamp_to_datetime(s):
    '''
    Parses a timestamp to a datetime instance.
    @param: s:str Timestamp string.
    @return: datetime
    '''
    f, i = modf(long(s) / float(1000))
    return datetime.fromtimestamp(i) + timedelta(milliseconds=f * 1000)




def datetime_to_timestamp(d):
    '''
    Converts a datetime instance into a timestamp string.
    @param d:datetime Date instance
    @return:long
    '''
    return long(d.strftime("%s") + "%03d" % (d.time().microsecond / 1000))




def is_empty_or_none(s):
    '''
    Returns a value indicating whether the string is empty or none
    @param s:str String to check.
    @return: bool
    '''
    if s is None:
        return True

    try:
        return len(s) == 0
    except:
        return False




def extract_id_from_uri(s):
    '''
    Returns the ID section of an URI.
    @param s:str URI
    @return: str
    '''
    return [ item for item in s.split("/") if not is_empty_or_none(item) ][-1]




class Address(object):
    '''
    Represents a postal address.
    '''
    def __init__(self, address_dict={}, mutable=False):
        '''
        Initializes a new instance of the Address class.
        @param address_dict:dict Address dictionary.
        '''
        self.__address_dict = address_dict
        self.__mutable = mutable


    def __getattr__(self, field):
        '''
        Gets a field of the address.
        @param field:str Field name.
        @return: str
        '''
        try:
            return self.__address_dict[field]
        except KeyError:
            raise AttributeError, field


    def __setattribute__(self, field, value):
        '''
        Sets an address field.
        @param field:str Field name.
        @param value:str Field value.
        '''
        if not self.__mutable:
            raise Exception("Address is not mutable.")

        if field not in ["number", "street", "city", "zipcode", "state",
                         "country"]:
            raise AttributeError("Address has no such attribute.")

        self.__address_dict[field] = value

