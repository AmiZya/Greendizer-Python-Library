import time
import urllib, urllib2
import simplejson
import re
import zlib
from datetime import datetime, date
from gzip import GzipFile
from StringIO import StringIO
import greendizer
from greendizer.base import (is_empty_or_none, timestamp_to_datetime,
                             datetime_to_timestamp)




COMPRESSION_DEFLATE = "deflate"
COMPRESSION_GZIP = "gzip"
API_ROOT = "https://api.greendizer.com/"
USE_GZIP = True



class ApiException(Exception):
    '''
    Represents an API-related exception
    '''
    def __init__(self, response):
        '''
        Initializes a new instance of the ApiException class.
        @param response:Response
        '''
        self.__response = response


    @property
    def code(self):
        '''
        Gets the error code
        @return: int
        '''
        return self.__response.status_code


    def __str__(self):
        '''
        Returns a string representation of the exception
        @return: str
        '''
        return ((self.__response.data or {})
                .get('desc', "Unexpected error (code: %s)" % self.code))




class Request(object):
    '''
    Represents an HTTP request to the Greendizer API
    '''
    class HttpRequest(urllib2.Request):
        '''
        Represents an HTTP request
        This class inherits from the urllib2 Request class to extend the
        HTTP methods available beyond the GET and POST already built-in.
        '''
        def __init__(self, uri, method="GET", **kwargs):
            '''
            Initializes a new instance of the Request class.
            @param uri:str The URI to which will be bound.
            @param method:str The HTTP method to use with the request.
            '''
            self.__method = method
            urllib2.Request.__init__(self, uri, **kwargs)


        def get_method(self):
            '''
            Gets the HTTP method in use.
            @return: str
            '''
            return self.__method


    def __init__(self, client=None, method="GET", uri=None, data=None,
                 content_type="application/x-www-form-urlencoded"):
        '''
        Initializes a new instance of the Request class.
        @param method:str HTTP method
        @param content_type:str MIME type of the data to carry to the server.
        '''
        if is_empty_or_none(uri):
            raise ValueError("Invalid URI.")

        if (is_empty_or_none(method)
            or method.lower() not in ["head", "get", "post", "put", "patch",
                                      "delete", "options"]):
            raise ValueError("Invalid HTTP method.")

        if (is_empty_or_none(content_type)
            or content_type not in ["application/xml",
                                    "application/x-www-form-urlencoded"]):
            raise ValueError("Invalid content type value.")

        if not data and method.lower() in ["post", "put", "patch"]:
            raise ValueError("Data is not expected to be None.")

        self.__content_type = content_type
        self.data = data
        self.uri = uri
        self.method = method
        self.headers = {}
        if client:
            client.sign_request(self)


    def __getitem__(self, header):
        '''
        Gets the value of a header
        @param header:str
        @return object
        '''
        return self.headers.get(header, None)


    def __setitem__(self, header, value):
        '''
        Sets a header
        @param header:str Header name
        @param value:object Header value
        '''
        self.headers[header] = value


    def __delitem__(self, header):
        '''
        Removes a header
        @param header:str
        '''
        if header in self.headers:
            del self.headers[header]


    def __serialize_headers(self):
        '''
        Serializes the values of the headers to strings
        @return: dict
        '''
        serialized = {}
        for header, value in self.headers.items():
            if isinstance(value, datetime) or isinstance(value, date):
                serialized[header] = value.isoformat()
            else:
                serialized[header] = str(value)

        return serialized


    def get_response(self):
        '''
        Sends the request and returns an HTTP response object.
        @return: Response
        '''
        headers = self.__serialize_headers()
        headers.update({
            "Accept": "application/json",
            "User-Agent": "Greendizer Python Library/1.0",
            "Accept-Encoding": "gzip, deflate"
        })

        method = self.method
        if self.method == "PATCH":
            headers["X-HTTP-Method-Override"] = self.method
            method = "POST"

        encoded_data = None
        if method in ["POST", "PATCH", "PUT"] and self.data:
            headers["Content-Type"] = self.__content_type
            if self.__content_type == "application/x-www-form-urlencoded":
                encoded_data = urllib.urlencode(self.data)
            else:
                if USE_GZIP:
                    #Compress to GZip
                    headers["Content-Encoding"] = COMPRESSION_GZIP
                    bf = StringIO('')
                    f = GzipFile(fileobj=bf, mode='wb', compresslevel=9)
                    f.write(self.data)
                    f.close()
                    encoded_data = bf.getvalue()
                else:
                    encoded_data = self.data

        request = Request.HttpRequest(API_ROOT + self.uri, data=encoded_data,
                                      method=method, headers=headers)

        try:
            response = urllib2.urlopen(request)
            return Response(self, 200, response.read(), response.info())

        except(urllib2.HTTPError), e:
            instance = Response(self, e.code, e.read(), e.info())
            if e.code not in [201, 202, 204, 206, 304, 408, 416]:
                raise ApiException(instance)

            return instance

        except urllib2.URLError:
            raise Exception("Unable to reach the server")




class Response(object):
    '''
    Represents an HTTP response to a greendizer API Request
    '''
    def __init__(self, request, status_code, data, info):
        '''
        Initializes a new instance of the Response class.
        @param request:Request Request at the origin of this response
        @param status_code:int Status code
        @param data:str Data carried in the body of the response
        @param info:object Encapsulates methods to access the headers. 
        '''
        self.__request = request
        self.__status_code = status_code

        content_encoding = info.getheader("Content-Encoding", None)
        if content_encoding == COMPRESSION_DEFLATE:
            data = zlib.decompress(data)
        elif content_encoding == COMPRESSION_GZIP:
            data = GzipFile(fileobj=StringIO(data)).read()

        self.__data = data
        self.__info = info


    def __getitem__(self, header):
        '''
        Gets the value of a header
        @param header:str Header name
        @return: object
        '''
        return self.get_header(header)


    def get_header(self, name):
        '''
        Gets the value of a header
        @param name:str Header name
        @return: object
        '''
        header = name.lower()
        if(header in ["date", "last-modified"]
           and self.__info.getheader(header, None)):
            value = self.__info.getheader(header)
            if "GMT" in value:
                #RFC1122
                return datetime.strptime(value, "%a, %d %b %Y %H:%M:%S GMT")
            else:
                '''
                WARNING:
                The HTTP protocol requires dates to be UTC.
                The parsing of ISO8601 is made assuming there are no
                time zone info in the string.
                '''
                #ISO8601
                return datetime(*map(int, re.split('[^\d]', value)[:-1]))


        if header == "etag":
            return Etag.parse(self.__info.getheader(header, None))

        if header == "content-range":
            return ContentRange.parse(self.__info.getheader(header, None))

        return self.__info.getheader(header, None)


    @property
    def status_code(self):
        '''
        Gets the status code of the response
        @return: int
        '''
        return self.__status_code


    @property
    def request(self):
        '''
        Gets the request at the origin of this response
        @return: Request
        '''
        return self.__request


    @property
    def data(self):
        '''
        Gets the data found in the body of the response
        @return: dict
        '''
        try:
            return simplejson.loads(self.__data)
        except:
            if greendizer.DEBUG:
                print self.__data




class Etag(object):
    '''
    Represents a Greendizer ETag
    '''
    def __init__(self, last_modified, identifier):
        '''
        Initializes a new instance of the Etag class.
        @param last_modified:datetime Last modification date
        @pram identifier:str ID of the resource or collection
        '''
        self.__last_modified = last_modified
        self.__id = identifier


    @property
    def last_modified(self):
        '''
        Gets the date on which the resource was last modified.
        @return: datetime
        '''
        return self.__last_modified


    @property
    def timestamp(self):
        '''
        Gets the timestamp of the last modification date.
        @return: long
        '''
        return datetime_to_timestamp(self.__last_modified)


    @property
    def id(self):
        '''
        Gets the ID of the resource.
        @return: str
        '''
        return self.__id


    def __str__(self):
        '''
        Returns a string representation of the Etag
        @return: str
        '''
        return "%s-%s" % (self.timestamp, self.__id)


    @classmethod
    def parse(cls, raw):
        '''
        Parses a string and returns a new instance of the Etag class.
        @param raw:str String to parse
        @return: Etag
        '''
        if not raw or len(raw) == 0:
            return

        timestamp, identifier = raw.split("-")
        return cls(timestamp_to_datetime(timestamp), identifier)




class Range(object):
    '''
    Represents an HTTP Range
    '''
    def __init__(self, unit="resources", offset=0, limit=200):
        '''
        Initializes a new instance of the Range class.
        @param unit:str Range unit
        @param offset:int Range offset
        @param limit:int Number of elements to include.
        '''
        self.unit = unit
        self.offset = offset
        self.limit = limit


    def __str__(self):
        '''
        Returns a string representation of the object
        @return: str
        '''
        return "%s=%d-%d" % (self.unit, self.offset, self.limit)



class ContentRange(object):
    '''
    Represents an HTTP Content-Range
    '''
    REG_EXP = r'''^(?P<unit>\w+)(?:[ ]|=)(?P<offset>\d+)-(?P<last>\d+)
                \/(?P<total>\d+)$'''


    def __init__(self, unit, offset, limit, total):
        '''
        Initializes a new instance of the ContentRange class.
        @param unit:str Range unit
        @param offset:int Range offset
        @param last:int Range last item zero-based index
        @param total:total Total number of items available
        '''
        self.__unit = unit
        self.__offset = int(offset)
        self.__limit = int(limit)
        self.__total = int(total)


    @property
    def unit(self):
        '''
        Gets the content range unit
        @return: str
        '''
        return self.__unit


    @property
    def offset(self):
        '''
        Gets the offset
        @return: int
        '''
        return self.__offset


    @property
    def limit(self):
        '''
        Gets the zero-based index of the last element in the range
        @return: int
        '''
        return self.__limit


    @property
    def total(self):
        '''
        Gets the total number of resources available
        @return: int
        '''
        return self.__total


    @classmethod
    def parse(cls, raw):
        '''
        Parses a string into a new instance of the ContentRange class.
        @param raw:str String to parse
        @return: ContentRange
        '''
        if is_empty_or_none(raw):
            return

        match = re.match(cls.REG_EXP, raw)
        if not match or len(match.groupdict()) < 4:
            return

        return cls(*match.groups())

