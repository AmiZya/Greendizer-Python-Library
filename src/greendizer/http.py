from datetime import datetime, date, time
import urllib, urllib2
import simplejson
import re
import io
import zlib
from gzip import GzipFile


COMPRESSION_DEFLATE = "deflate"
COMPRESSION_GZIP = "gzip"


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
        return self.__response


    def __str__(self):
        '''
        Returns a string representation of the exception
        @return: str
        '''
        try:
            return simplejson.loads(self.__response.get_data())["description"]
        except:
            return "Unknown"




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


        @property
        def method(self):
            '''
            Gets the HTTP method in use.
            '''
            return self.__method


    def __init__(self, client, method="GET", uri=None,
                 content_type="application/x-www-form-urlencoded", data=None):
        '''
        Initializes a new instance of the Request class.
        @param method:str HTTP method
        @param content_type:str MIME type of the data to carry to the server.
        '''
        self.__client = client
        self.__content_type = content_type
        self.data = data
        self.uri = uri
        self.method = method
        self.headers = {}


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
        for header, value in self.headers:
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
            "Authorization": self.__client.generate_authorization_header(),
            "Accept-Encoding": "gzip, deflate"
        })

        method = self.__method
        if self.__method == "PATCH":
            headers["X-Http-Method-Override"] = self.__method
            method = "POST"

        data = None
        if method in ["POST", "PATCH", "PUT"] and self.data:
            headers["Content-Type"] = self.__content_type
            if self.__content_type != "application/x-www-form-urlencoded":
                data = urllib.urlencode(self.data)
            else:
                #Compress to GZip
                headers["Content-Encoding"] = COMPRESSION_GZIP
                bf = io.BytesIO('')
                f = GzipFile(fileobj=bf, mode='wb', compresslevel=9)
                f.write(data)
                f.close()
                data = bf.getvalue()

        request = Request.HttpRequest("https://api.greendizer.com/" + self.uri,
                                      method)
        try:
            response = urllib2.urlopen(request, data, headers)
            return Response(self, 200, response.read(), response.info)
        except(urllib2.URLError), e:
            instance = Response(self, e.status, e.read(), e.info)
            if e.status not in [201, 202, 204, 206, 304, 408, 416]:
                raise ApiException(instance)

            return instance




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

        content_encoding = info.getHeader("Content-Encoding", None)
        if content_encoding == COMPRESSION_DEFLATE:
            data = zlib.decompress(data)
        elif content_encoding == COMPRESSION_GZIP:
            data = GzipFile(fileobj=io.BytesIO(data)).read()

        self.__data = data
        self.__info = info


    def __getitem__(self, header):
        '''
        Gets the value of a header
        @return: object
        '''
        if(header in ["Date", "Last-Modified"]
           and self.__info.getHeader(header, None)):
            value = self.__info.getHeader(header)
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


        if header == "Etag":
            return Etag.parse(self.__info.getHeader(header, None))

        if header == "Content-Range":
            return ContentRange.parse(self.__info.getHeader(header, None))

        return self.__info.getHeader(header, None)


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
            return




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


    def __str__(self):
        '''
        Returns a string representation of the Etag
        @return: str
        '''
        return "%s-%s" % (self.__last_modified.time() * 1000, self.__id)


    @classmethod
    def parse(cls, raw):
        '''
        Parses a string into a new instance of the Etag class.
        @param raw:str String to parse
        @return: Etag
        '''
        if not raw or len(raw) == 0:
            return

        parts = raw.split("-")
        return cls(datetime.fromtimestamp(int(parts[0]) / 1000), long(parts[1]))




class Range(object):
    '''
    Represents an HTTP Range
    '''
    def __init__(self, unit="resources", offset=0, last=200):
        '''
        Initializes a new instance of the Range class.
        @param unit:str Range unit
        @param offset:int Range offset
        @param last:int Zero-based of the last element to include
        '''
        self.unit = unit
        self.offset = offset
        self.last = last


    def __str__(self):
        '''
        Returns a string representation of the object
        @return: str
        '''
        return "%s=%d-%d" % (self.unit, self.offset, self.last)



class ContentRange(object):
    '''
    Represents an HTTP Content-Range
    '''
    REG_EXP = r'^(?P<unit>\w+) (?P<offset>\d+)-(?P<last>\d+)\/(?P<total>\d+)$'


    def __init__(self, unit, offset, last, total):
        '''
        Initializes a new instance of the ContentRange class.
        @param unit:str Range unit
        @param offset:int Range offset
        @param last:int Range last item zero-based index
        @param total:total Total number of items available
        '''
        self.__unit = unit
        self.__offset = int(offset)
        self.__last = int(last)
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
    def last(self):
        '''
        Gets the zero-based index of the last element in the range
        @return: int
        '''
        return self.__last


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
        if not raw or len(raw) == 0:
            return

        match = re.match(cls.REG_EXP, raw)
        if len(match.groupdict()) < 4:
            return

        return cls(**match.groupdict())

