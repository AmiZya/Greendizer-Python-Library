from greendizer.base import extract_id_from_uri
from greendizer.dal import Node
from greendizer.resources import (User, Company, EmailBase, ThreadBase,
                                  InvoiceBase, HistoryBase, InvoiceNodeBase,
                                  ThreadNodeBase, MessageNodeBase)




class Buyer(User):
    '''
    Represents a buyer user
    '''
    def __init__(self, client):
        '''
        Initializes a new instance of the Buyer class.
        @param client:greendizer.Client Client instance.
        '''
        super(Buyer, self).__init__(client)
        self.__emailNode = EmailNode(self)


    @property
    def emails(self):
        '''
        Gives access to the emails node.
        @return: EmailNode
        '''
        return self.__emailNode


    @property
    def uri(self):
        '''
        Gets the URI of the resource
        @return: str
        '''
        return "buyers/me/"




class Email(EmailBase):
    '''
    Represents an Email address from a buyer's perspective.
    '''
    def __init__(self, user, identifier):
        '''
        Initializes a new instance of the Email class.
        @param user:User Currently authenticated user.
        @param identifier:str ID of the email.
        '''
        self.__user = user
        super(Email, self).__init__(user.client, identifier)
        self.__invoiceNode = InvoiceNodeBase(self)
        self.__threadNode = ThreadNode(self)
        self.__sellerNode = SellerNode(self)


    @property
    def invoices(self):
        '''
        Gets the node of invoices attached to the current email address.
        @return: InvoiceNode
        '''
        return self.__invoiceNode


    @property
    def threads(self):
        '''
        Gets the node of conversation threads attached to the current email
        address.
        @return: ThreadNode
        '''
        return self.__threadNode


    @property
    def sellers(self):
        '''
        Gets the 
        '''
        return self.__sellerNode




class EmailNode(Node):
    '''
    Represents an API node giving access to the email accounts attached
    to the currently authenticated user.
    '''
    def __init__(self, user):
        '''
        Initializes a new instance of the EmailNode class.
        @param user:User Currenly authenticated user.
        @param uri:str URI of the node.
        @param resource_cls:Class Email class.
        '''
        self.__user = user
        super(EmailNode, self).__init__(user.client, user.uri + "emails/",
                                        Email)


    def get_resource_by_id(self, identifier):
        '''
        Gets an email address by its ID.
        @param identifier:str ID of the email address.
        @return: Email
        '''
        return self._resource_cls(self.__user, identifier)




class Invoice(InvoiceBase):
    '''
    Represents an invoice from a buyer's perspective.
    '''
    @property
    def seller(self):
        '''
        Gets the seller who sent the invoice.
        @return: Seller
        '''
        seller_id = extract_id_from_uri(self._get_attribute("sellerURI"))
        return Seller(self.email, seller_id)




class InvoiceNode(InvoiceNodeBase):
    '''
    Represents an API node giving access to invoices sent to a specific email
    address.
    '''
    def __init__(self, email):
        '''
        Initializes a new instance of the InvoiceNode class.
        @param email:Email Parent email instance.
        '''
        self.__email = email
        super(InvoiceNode, self).__init__(email, Invoice)


    def get_resource_by_id(self, identifier):
        '''
        Gets an invoice by its ID.
        @param identifier:str ID of the invoice.
        @return: Invoice
        '''
        return self._resource_cls(self.__email, identifier)





class Thread(ThreadBase):
    '''
    Represents a conversation thread from a buyer's perspective.
    '''
    def __init__(self, email, identifier):
        '''
        Initializes a new instance of the Thread class.
        @param email:Email Parent email address.
        @param identifier:str ID of the resource.
        '''
        self.__email = email
        super(Thread, self).__init__(email.client, identifier)
        self.__messageNode = MessageNode(self)


    @property
    def uri(self):
        '''
        Gets the URI of the conversation thread.
        @return: str
        '''
        return "%sthreads/%s/" % (self.__email.uri, self.id)


    @property
    def seller(self):
        '''
        Gets the seller with which the thread was opened.
        @return: Company
        '''
        seller_id = extract_id_from_uri(self._get_attribute("sellerURI"))
        return Seller(self.client, seller_id)


    @property
    def messages(self):
        '''
        Gets access to the messages of the thread.
        @return: MessageNode
        '''
        return self.__messageNode




class ThreadNode(ThreadNodeBase):
    '''
    Represents an API node giving access to the conversation threads
    attached to a specific email address.
    '''
    def __init__(self, email):
        '''
        Initializes a new instance of the ThreadNode class.
        @param email:Email Parent email instance.
        '''
        self.__email = email
        super(ThreadNode, self).__init__(email.client, email.uri + "threads/",
                                         Thread)


    def get_resource_by_id(self, identifier):
        '''
        Gets a thread by its ID.
        @param identifier:str ID of the thread.
        @return: str
        '''
        return self._resource_cls(self.__email, identifier)




class MessageNode(MessageNodeBase):
    '''
    Represents an API node giving access to the messages contained in a
    conversation thread.
    '''
    def __init__(self, thread):
        '''
        Initializes a new instance of the MessageNode class.
        @param thread:Thread Parent thread.
        '''
        self.__thread = thread
        super(MessageNode, self).__init__(thread)




class Seller(HistoryBase):
    '''
    Represents a seller who has invoiced the currently authenticated user
    in the past.
    '''
    def __init__(self, email, identifier):
        '''
        Initializes a new instance of the Seller class.
        @param email:Email Parent email instance.
        @param identifier:str ID of the seller.
        '''
        self.__email = email
        super(Seller, self).__init__(email.client, identifier)


    @property
    def uri(self):
        '''
        Gets the URI of the seller.
        @return: str
        '''
        return "%ssellers/%s/" % (self.__email.uri, self.id)


    @property
    def email(self):
        '''
        Gets the parent email.
        @return: Email
        '''
        return self.__email


    @property
    def company(self):
        '''
        Gets the seller's company info.
        @return: greendizer.resources.Company
        '''
        company_id = extract_id_from_uri(self._get_attribute("companyURI"))
        return Company(self.__email, company_id)




class SellerNode(Node):
    '''
    Represents the node giving access to the history of exchanges that were
    made with the sellers.
    '''
    def __init__(self, email):
        '''
        Initializes a new instance of the SellerHistoryNode class.
        @param email:Email Parent email instance.
        '''
        self.__email = email
        super(SellerNode, self).__init__(email.client,
                                        email.uri + "sellers/",
                                        Seller)


    def get_resource_by_id(self, identifier):
        '''
        Gets the history of a specific seller
        @param identifier:str ID of the seller.
        @return: Seller
        '''
        return self._resource_cls(self.__email, identifier)


    @property
    def email(self):
        '''
        Gets the parent email address.
        @return: Email
        '''
        return self.__email

