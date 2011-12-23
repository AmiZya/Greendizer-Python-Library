import hashlib
from datetime import date
from greendizer.base import is_empty_or_none, extract_id_from_uri
from greendizer.dal import Resource, Node
from greendizer.http import Request




class User(Resource):
    '''
    Represents a generic user on Greendizer.
    '''
    def __init__(self, client):
        '''
        Initializes a new instance of the User class.
        '''
        super(User, self).__init__(client, "me")
        self.__company = Employer(self)
        self.__settings = Settings(self)
        self.__emailNode = Node(client, self.uri + "emails/", None)


    @property
    def emails(self):
        '''
        Gets access to the email addresses attached to this user.
        @return: Node
        '''
        return self.__emailNode


    @property
    def settings(self):
        '''
        Gets the settings of this user.
        @return: Settings
        '''
        return self.__settings


    @property
    def company(self):
        '''
        Gets the company of this user.
        @return: Company
        '''
        return self.__company


    @property
    def first_name(self):
        '''
        Gets the first name.
        @return: str
        '''
        return self._get_attribute("firstname")


    @property
    def last_name(self):
        '''
        Gets the last name
        @return: str
        '''
        return self._get_attribute("lastname")


    @property
    def full_name(self):
        '''
        Gets the last name
        @return: str
        '''
        return "%s %s" % (self.first_name, self.last_name)


    @property
    def avatar_url(self):
        '''
        Gets the URL of the user's profile picture
        @return: str
        '''
        return self._get_attribute("avatar")


    @property
    def birthday(self):
        '''
        Gets the birthday
        @return: date
        '''
        return self._get_date_attribute("birthday").date




class Settings(Resource):
    '''
    Represents generic settings attached a user's account.
    '''
    def __init__(self, user):
        '''
        Initializes a new instance of the Settings class.
        @param client:Client Current client instance.
        '''
        self.__user = user
        super(Settings, self).__init__(user.client)


    @property
    def uri(self):
        '''
        Gets the URI of the resource.
        @return:str
        '''
        return self.__user.uri + "settings/"


    @property
    def language(self):
        '''
        Gets the language of the user.
        @return: str
        '''
        return self._get_attribute("language")


    @property
    def region(self):
        '''
        Gets the region of the user
        @return: str
        '''
        return self._get_attribute("region")


    @property
    def currency(self):
        '''
        Gets the currency
        @return: str
        '''
        return self._get_attribute("currency")




class Company(Resource):
    '''
    Represents a generic company's profile on Greendizer.
    '''
    @property
    def uri(self):
        '''
        Gets the URI of the resource.
        @return: str
        '''
        return "/companies/%s/" + self.id


    @property
    def name(self):
        '''
        Gets the name of the company
        @return: str
        '''
        return self._get_attribute("name")


    @property
    def description(self):
        '''
        Gets the description of the company
        @return: str
        '''
        return self._get_attribute("description")


    @property
    def small_logo_url(self):
        '''
        Gets the URL of a small version of the company's logo.
        @return: str
        '''
        return self._get_attribute("smallLogo")


    @property
    def large_logo_url(self):
        '''
        Gets the URL of a large version of the company's logo.
        @return: str
        '''
        return self._get_attribute("largeLogo")



class Employer(Company):
    '''
    Represents the company employing a user on Greendizer.
    '''
    def __init__(self, user):
        '''
        Initializes a new instance of the Settings class.
        @param user:User currently authenticated user.
        @param identifier:Id of the company
        '''
        self.__user = user
        super(Employer, self).__init__(user.client)


    @property
    def uri(self):
        '''
        Gets the URI of the resource.
        @return: str
        '''
        return self.__user.uri + "company/"



class EmailBase(Resource):
    '''
    Represent an email address on Greendizer
    '''
    def __init__(self, user, identifier):
        '''
        Initializes a new instance of the Email class
        @param user:User Current user.
        @param identifier:str ID of the email resource.
        '''
        if "@" in identifier:
            identifier = hashlib.sha1(identifier).hexdigest()

        super(EmailBase, self).__init__(user.client, identifier)
        self.__user = user
        self.__id = identifier


    @property
    def uri(self):
        '''
        Gets the URI of this resource.
        @return: str
        '''
        return "%semails/%s/" % (self.__user.uri, self.id)


    @property
    def label(self):
        '''
        Gets the label of this address
        @return: str
        '''
        return self._get_attribute("label")




class InvoiceBase(Resource):
    '''
    Represent an email address on Greendizer
    '''
    def __init__(self, email, identifier):
        '''
        Initializes a new instance of the Email class
        @param email:Email Email instance of the origin of this invoice.
        @param identifier:str ID of the email resource.
        '''
        super(InvoiceBase, self).__init__(email.client, identifier)
        self.__email = email
        self.__id = identifier


    @property
    def email(self):
        '''
        Gets the email instance to which this invoice is attached.
        @return:Email
        '''
        return self.__email


    @property
    def uri(self):
        '''
        Gets the URI of this resource.
        @return: str
        '''
        return "%sinvoices/%s/" % (self.__email.uri, self.id)


    @property
    def name(self):
        '''
        Gets the name of the invoice.
        @return: str
        '''
        return self._get_attribute("name")


    @property
    def description(self):
        '''
        Gets the description of the invoice
        @return: str
        '''
        return self._get_attribute("description")


    @property
    def total(self):
        '''
        Gets the total of the invoice.
        @return: float
        '''
        return self._get_attribute("total")


    @property
    def body(self):
        '''
        Gets the body of the invoice.
        @return: str 
        '''
        return self._get_attribute("body")


    @property
    def currency(self):
        '''
        Gets the currency of the invoice.
        @return:str
        '''
        return self._get_attribute("currency")


    @property
    def date(self):
        '''
        Gets the invoice date.
        @return: datetime
        '''
        return self._get_date_attribute("date")


    @property
    def due_date(self):
        '''
        Gets the due date of the invoice.
        @return: datetime
        '''
        return self._get_date_attribute("due_date")


    @property
    def secretKey(self):
        '''
        Gets the secret key of the invoice.
        @return: str
        '''
        return self._get_attribute("secretKey")


    def __get_location(self):
        '''
        Gets a value indicating the location of the invoice.
        @return: int
        '''
        return self._get_attribute("location")


    def __set_location(self, value):
        '''
        Sets a value indicating the location of the invoice.
        @param value:int
        '''
        self._register_update("location", value)


    def __get_read(self):
        '''
        Gets a value indicating whether the invoice has been read or not.
        @return: bool
        '''
        return self._get_attribute("read")


    def __set_read(self, value):
        '''
        Sets a value indicating whether the invoice has been read or not.
        @param value:bool
        '''
        self._register_update("read", value)


    def __get_flagged(self):
        '''
        Gets a value indicating whether the invoice has been flagged or not.
        @return: bool
        '''
        return self._get_attribute("flagged")


    def __set_flagged(self, value):
        '''
        Sets a value indicating whether the invoice has been flagged or not.
        @param value:bool
        '''
        self._register_update("flagged", value)


    def __get_paid(self):
        '''
        Gets a value indicating whether the invoice has been paid or not.
        @return: bool
        '''
        return self._get_attribute("paid")


    def __set_paid(self, value):
        '''
        Sets a value indicating whether the invoice has been paid or not.
        @param value:bool
        '''
        self._register_update("paid", value)


    location = property(__get_location, __set_location)
    read = property(__get_read, __set_read)
    flagged = property(__get_flagged, __set_flagged)
    paid = property(__get_flagged, __set_flagged)




class InvoiceNodeBase(Node):
    '''
    Represents a node giving access to invoices.
    '''
    def __init__(self, email, resource_cls=InvoiceBase):
        '''
        Initializes a new instance of the InvoiceNode class.
        @param email:Email Email instance to which the node is tied.
        @param resource_cls:Class Class with which invoices will be instantiated
        '''
        self.__email = email
        super(InvoiceNodeBase, self).__init__(email.client,
                                              uri=email.uri + "invoices/",
                                              resource_cls=resource_cls)


    def get_resource_by_id(self, identifier):
        '''
        Gets an invoice using its ID.
        @param identifier:str ID of the invoice.
        @return: Invoice
        '''
        return self._resource_cls(self.__email, identifier)


    def get_email(self):
        '''
        Gets the email instance to which this node is attached.
        @return: Email
        '''
        return self.__email


    @property
    def archived(self):
        '''
        Gets a collection to manipulate archived invoices.
        @return: Collection
        '''
        return self.search("location==1")


    @property
    def trashed(self):
        '''
        Gets a collection to manipulate trashed invoices.
        @return: Collection
        '''
        return self.search("location==2")


    @property
    def unread(self):
        '''
        Gets a collection to manipulate unread invoices.
        @return: Collection
        '''
        return self.search("read==0|location<<2")


    @property
    def flagged(self):
        '''
        Gets a collection to manipulate flagged invoices.
        @return: Collection
        '''
        return self.search("flagged==1|location<<2")


    @property
    def due(self):
        '''
        Gets a collection to manipulate all due invoices.
        @return: Collection
        '''
        return self.search("paid==0|location<<2|canceled==0")


    @property
    def overdue(self):
        '''
        Gets a collection to manipulate overdue invoices.
        @return: Collection
        '''
        return self.search("paid==0|location<<2|canceled==0|dueDate>>"
                           + date.today().isoformat())




class ThreadBase(Resource):
    '''
    Represents a conversation thread.
    '''
    @property
    def messagesCount(self):
        '''
        Gets the number of messages in the thread
        @return: int
        '''
        return self._get_attribute("count")


    @property
    def subject(self):
        '''
        Gets the subject of the thread.
        @return: str
        '''
        return self._get_attribute("subject")


    @property
    def snippet(self):
        '''
        Gets a snippet of the lastest message in the thread
        @return: str 
        '''
        return self._get_attribute("snippet")


    @property
    def lastMessageDate(self):
        '''
        Gets the date at which the latest message was sent.
        @return: date
        '''
        return self._get_date_attribute("lastMessage")


    def __get_location(self):
        '''
        Gets a value indicating the location of the thread.
        @return: int
        '''
        return self._get_attribute("location")


    def __set_location(self, value):
        '''
        Sets a value indicating the location of the thread.
        @param value:int
        '''
        self._register_update("location", value)


    def __get_read(self):
        '''
        Gets a value indicating whether the thread has been read or not.
        @return: bool
        '''
        return self._get_attribute("read")


    def __set_read(self, value):
        '''
        Sets a value indicating whether the thread has been read or not.
        @param value:bool
        '''
        self._register_update("read", value)


    def __get_flagged(self):
        '''
        Gets a value indicating whether the thread has been flagged or not.
        @return: bool
        '''
        return self._get_attribute("flagged")


    def __set_flagged(self, value):
        '''
        Sets a value indicating whether the thread has been flagged or not.
        @param value:bool
        '''
        self._register_update("flagged", value)


    location = property(__get_location, __set_location)
    read = property(__get_read, __set_read)
    flagged = property(__get_flagged, __set_flagged)




class ThreadNodeBase(Node):
    '''
    Represents a node giving access to conversation threads.
    '''
    @property
    def inbox(self):
        '''
        Gets a collection to manipulate threads in the inbox.
        @return: Collection
        '''
        return self.search("location==0")


    @property
    def archived(self):
        '''
        Gets a collection to manipulate archived threads.
        @return: Collection
        '''
        return self.search("location==1")


    @property
    def trashed(self):
        '''
        Gets a collection to manipulate trashed threads.
        @return: Collection
        '''
        return self.search("location==2")


    @property
    def unread(self):
        '''
        Gets a collection to manipulate unread threads.
        @return: Collection
        '''
        return self.search("read==0|location<<2")


    @property
    def flagged(self):
        '''
        Gets a collection to manipulate flagged threads.
        @return: Collection
        '''
        return self.search("flagged==1|location<<2")


    def open(self, recipient_id, subject, message):
        '''
        Opens a new conversation thread.
        @param recipient:str ID of the recipient
        @param subject:str Subject of the thread
        @param message:str Message
        '''
        if is_empty_or_none(recipient_id):
            raise ValueError("Invalid recipient ID")

        if is_empty_or_none(subject):
            raise ValueError("Invalid subject")

        if is_empty_or_none(message):
            raise ValueError("Invalid message")

        data = {"recipient":recipient_id, "subject":subject, "message":message}
        request = Request(self.__seller.client, method="POST",
                          uri=self.get_uri(), data=data)

        response = request.get_response()
        if response.get_status_code() == 201:
            thread_id = extract_id_from_uri(response["Location"])
            thread = self.get_resource_by_id(thread_id)
            thread.sync(response.data, response["Etag"])
            return thread




class MessageBase(Resource):
    '''
    Represents a message inside a conversation thread.
    '''
    def __init__(self, thread, identifier):
        '''
        Initializes a new instance of the Message class.
        @param thread:ThreadBase Parent thread.
        @param identifier:ID of the message.
        '''
        self.__thread = thread
        super(MessageBase, self).__init__(thread.client, identifier)


    @property
    def uri(self):
        '''
        Gets the URI of the message.
        @return: str
        '''
        return "%smessages/%s/" % (self.__thread.uri, self.id)


    @property
    def thread(self):
        '''
        Gets the parent thread.
        @return: ThreadBase
        '''
        return self.__thread


    @property
    def text(self):
        '''
        Gets the content of the message
        @return: str
        '''
        return self._get_attribute("text")


    @property
    def sender(self):
        '''
        Gets a value indicating whether the message has been sent by the
        currently authenticated user.
        @return: bool
        '''
        return self._get_attribute("sender") is not None




class MessageNodeBase(Node):
    '''
    Represents an API node giving access to messages.
    '''
    def __init__(self, thread, resource_cls=MessageBase):
        '''
        Initializes a new instance of the MessageNode
        @param thread: ThreadBase instance.
        @param resource_cls: Class Message class.
        '''
        super(MessageNodeBase, self).__init__(thread.client,
                                              thread.uri + "messages/",
                                              resource_cls)



class HistoryBase(Resource):
    '''
    Represents a resource holding a history for different currencies.
    '''
    def __getitem__(self, currency_code):
        '''
        Gets stats about the exchanges made with a specific currency.
        @param currency_code:str 3 letters ISO Currency code.
        @return: dict
        '''
        return self.get_currency_stats(currency_code)


    def get_currency_stats(self, currency_code):
        '''
        Gets stats about the exchanges made with a specific currency.
        @param currency_code:str 3 letters ISO Currency code.
        @return: dict
        '''
        return self._get_attribute(currency_code.upper())


    @property
    def currencies(self):
        '''
        Gets the list of currencies used.
        @return: list
        '''
        return self._get_attribute("currencies")


    @property
    def invoices_count(self):
        '''
        Gets the number of invoices exchanged.
        @return: int
        '''
        return self._get_attribute("invoicesCount")


    @property
    def threads_count(self):
        '''
        Gets the number of threads opened.
        @return: int
        '''
        return self._get_attribute("threadsCount")


    @property
    def messages_count(self):
        '''
        Gets the number of messages exchanged.
        @return: int
        '''
        return self._get_attribute("messagesCount")



