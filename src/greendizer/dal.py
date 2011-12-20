import urllib
import time
from datetime import datetime, date
from greendizer.base import is_empty_or_none
from greendizer.http import Request, Etag, Range




RESPONSE_SIZE_LIMIT = 200




class ResourceDeletedException(Exception):
    '''
    Represents the exception raised if a resource has been 
    deleted.
    '''
    pass




class ResourceConflictException(Exception):
    '''
    Represents the exception raised if a resource could not be 
    updated or deleted because of a potential conflict
    '''
    def __init__(self, resource, conflict_type="PATCH"):
        '''
        Initializes a new instance of the ResourceConflictException
        @param resource:Resource Conflicting resource
        '''
        self.__resource = resource
        self.__conflict_type = conflict_type


    @property
    def resource(self):
        '''
        Gets the conflicting resource
        @return: Resource
        '''
        return self.__resource


    def refresh(self):
        '''
        Refreshes the resource.
        '''
        self.__resource.load()


    def force(self):
        '''
        Forces the operation on the resource.
        '''
        if self.__conflict_type == "PATCH":
            self.__resource.update()
        elif self.__conflict_type == "DELETE":
            self.__resource.delete()




class Resource(object):
    '''
    Represents a generic resource
    '''
    def __init__(self, client, identifier=None):
        '''
        Initializes a new instance of the Resource class.
        @param container:Container Resource container
        @param identifier:str ID of the resource
        '''
        self.__client = client
        self.__id = identifier or "0"
        self.__last_modified = datetime(1970, 1, 1)
        self.__rawData = {}
        self.__rawUpdates = {}
        self.__deleted = False


    def _get_date_attribute(self, name):
        '''
        Parses the value of an attribute retrieved from the server
        as a date
        @param name:str Attribute name
        @return: datetime
        '''
        value = self._get_attribute(name)
        if value:
            return datetime.fromtimestamp(value / 1000)


    def _get_attribute(self, name):
        '''
        Returns the value of an attribute retrieved from the server
        @param name:str Attribute name
        @return: object
        '''
        if self.__deleted:
            raise ResourceDeletedException()

        if len(self.__rawData) == 0: #Lazy loading
            self.load()

        return self.__rawData.get(name, None)


    def _set_attribute(self, name, value):
        '''
        Sets the value of an internal attribute.
        @param name:str Attribute name.
        @param value:object Attribute value
        @return: A value indicating whether the attribute changed or not.
        '''
        if self.__deleted:
            raise ResourceDeletedException()

        if isinstance(value, datetime) or isinstance(value, date):
            value = (time.mktime(value.utctimetuple()) * 1000
                    + value.microsecond / 1000)

        if self.__rawData.get(name, None) != value:
            self.__rawData[name] = value
            return True

        return False


    def _register_update(self, attribute, value):
        '''
        Adds an update to the stack.
        @param attribute:str Attribute name.
        @param value:object Attribute value.
        '''
        if self.__deleted:
            raise ResourceDeletedException()

        if self.__rawData.get(attribute, None) != value:
            self.__rawUpdates[attribute] = value


    @property
    def created_date(self):
        '''
        Gets the date on which the resource was created.
        @return: date
        '''
        return self._get_date_attribute("createdDate")


    @property
    def is_deleted(self):
        '''
        Gets a value indicating whether the resource has been deleted.
        '''
        return self.__deleted


    @property
    def client(self):
        '''
        Returns the current client instance.
        @return: Client
        '''
        return self.__client


    @property
    def etag(self):
        '''
        Returns the ETag of the resource.
        @return: Etag
        '''
        return Etag(self.__last_modified, self.__id)


    @property
    def id(self):
        '''
        Returns the ID of this resource.
        @return: str
        '''
        return self.__id


    @property
    def uri(self):
        '''
        Returns the uri of this resource.
        @return: str
        '''
        raise NotImplementedError()


    def sync(self, data, etag):
        '''
        Updates the current representation with another one.
        @param data:dict New representation
        @return: bool A value indicating whether the representation has changed.
        '''
        if not len(data):
            return

        self.__last_modified = etag.last_modified
        self.__id = etag.id

        if "etag" in data:
            del data["etag"]

        changed = False
        for item, value in data.items():
            changed = self._set_attribute(item, value) or False

        return changed


    def load(self):
        '''
        Loads the resource.
        '''
        if self.__deleted:
            raise ResourceDeletedException()

        request = Request(self.__client, uri=self.uri)
        request["If-Match"] = self.etag
        request["If-Unmodified-Since"] = self.etag.last_modified

        response = request.get_response()
        if response.status_code == 200:
            self.sync(response.data, response["Etag"])


    def update(self, prevent_conflicts=False):
        '''
        Updates the resource.
        @param prevent_conflicts:bool A value indicating whether the resource
        should not be updated if the current version is not the most recent
        one available.
        '''
        if self.__deleted:
            raise ResourceDeletedException()

        if len(self.__rawUpdates) == 0:
            return

        request = Request(self.__client, method="PATCH",
                          uri=self.uri, data=self.__rawUpdates)

        if prevent_conflicts:
            request["If-Match"] = self.etag
            request["If-Unmodified-Since"] = self.etag.last_modified

        response = request.get_response()
        if response.status_code == 408: #Conflict
            raise ResourceConflictException(self, "PATCH")

        if response.status_code == 204: #No-Content
            self.sync(self.__rawUpdates, response["Etag"])
            self.__rawUpdates = {}


    def delete(self, prevent_conflicts=False):
        '''
        Deletes the resource.
        @param prevent_conflicts:bool A value indicating whether the resource
        should not be deleted if the current version is not the most recent
        one available.
        '''
        if self.__deleted:
            raise ResourceDeletedException()

        request = Request(self.__client, method="DELETE", uri=self.uri)

        if prevent_conflicts:
            request["If-Match"] = self.etag
            request["If-Unmodified-Since"] = self.etag.last_modified

        response = request.get_response()
        if response.status_code == 408: #Conflict
            raise ResourceConflictException(self, "DELETE")

        if response.status_code == 204: #No-Content
            self.__deleted = True
            self.__rawData = {}
            self.__rawUpdates = {}




class Collection(object):
    '''
    Represents a collection of resources
    '''
    def __init__(self, node, uri, query=None):
        '''
        Initializes a new instance of the Collection class
        @param node:Node Node on which the collection is built
        @param uri:str URI of the collection
        @param query:str Filter query string
        '''
        self.__node = node
        self.__query = query
        self.__uri = uri + (("?q=" + urllib.quote_plus(query)) if query else "")
        self.__content_range = None
        self.__etag = Etag(datetime(1970, 1, 1), 0)
        self.__resources = {}
        self.__list = []


    def __iter__(self):
        '''
        Allows iterations over the resource dict contained in the collection.
        '''
        return self.__resources


    def __getitem__(self, identifier):
        '''
        Gets a resource inside the collection by its ID or None.
        @param identifier:ID of the resource.
        @return: Resource
        '''
        return self.__resources.get(identifier, None)


    def __len__(self):
        '''
        Returns the number of items contained in the collection.
        @return: int
        '''
        return len(self.__resources)


    @property
    def node(self):
        '''
        Gets the node on which the collection is built
        @return: Node
        '''
        return self.__node


    @property
    def uri(self):
        '''
        Gets the URI of the collection
        @return: str
        '''
        return self.__uri


    @property
    def last_modified(self):
        '''
        Gets the date of the last modification recorded
        @return: datetime
        '''
        return self.__etag.last_modified


    @property
    def resources(self):
        '''
        Gets the loaded resources
        @return: dict
        '''
        return self.__list


    @property
    def count(self):
        '''
        Gets the estimated number of resources available on the server
        @return: int
        '''
        if not self.__content_range:
            self.load_info()

        return self.__content_range.total


    def load_info(self):
        '''
        Loads the headers of the collection.
        '''
        self.populate(0, 1, head=True)


    def populate(self, offset=0, limit=200, head=False, fields=None):
        '''
        Populates the collection with resources from the server
        @param offset:int Offset
        @param limit:int Limit (Max: 200)
        '''
        uri = self.__uri

        if not is_empty_or_none(fields):
            fields = "fields=" + urllib.quote_plus(fields)
            uri = uri + ("?" if not self.__query else "&") + fields

        request = Request(self.__node.client, uri=uri,
                          method="HEAD" if head else "GET")

        if offset != None and limit != None:
            request["Range"] = Range(offset=offset,
                                     limit=min(RESPONSE_SIZE_LIMIT, limit))
        else:
            request["If-None-Match"] = self.__etag
            request["If-Modified-Since"] = self.__etag.last_modified


        response = request.get_response()
        self.__content_range = response["Content-Range"]
        self.__etag = response["Etag"]

        if response.status_code in [204, 416]: #(No-Content, Out-Range)
            self.__resources = {}
            self.__list = []
            return

        if response.status_code not in [200, 206]: #(OK, Partial Content)
            return Exception("Unexpected response from the server (code: %s)"
                             % response.status_code)

        if not head:
            self.__resources = {}
            self.__list = []
            for item in response.data:
                etag = Etag.parse(item["etag"])
                resource = self.__node[etag.id]
                resource.sync(item, etag)
                self.__list.append(resource)
                self.__resources[str(resource.id)] = resource




class Node(object):
    '''
    Represents a node to access a certain type of resources
    '''
    def __init__(self, client, uri, resource_cls):
        '''
        Initializes a new instance of th Node class.
        @param client:Client Current client instance
        @param uri:str URI of the node.
        @param resource_cls:Class Class of the resource to instantiate.
        '''
        self.__client = client
        self.__uri = uri
        self.__collections = {}
        self._resource_cls = resource_cls


    def __getitem__(self, identifier):
        '''
        Gets a resource by its ID.
        @param identifier:str ID of the resource
        @return: Resource
        '''
        return self.get_resource_by_id(identifier)


    def get_resource_by_id(self, identifier):
        '''
        Gets a resource by its ID.
        @param identifier:str ID of the resource
        @return: Resource
        '''
        return self._resource_cls(self.__client, identifier)


    @property
    def client(self):
        '''
        Gets the current client instance
        @return: Client
        '''
        return self.__client


    @property
    def all(self):
        '''
        Gets a collection to access all the resources accessible from this node.
        @return: Collection
        '''
        return self.search()


    def search(self, query=""):
        '''
        Returns a collection to filter the resources accessible from this node.
        @param query:str Query
        @return: Collection
        '''
        if query not in self.__collections:
            self.__collections[query] = Collection(self, self.__uri, query)

        return self.__collections[query]

