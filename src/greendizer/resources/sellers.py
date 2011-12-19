from greendizer.base import is_empty_or_none, extract_id_from_uri
from greendizer.http import Request
from greendizer.dal import Resource, Node
from greendizer.resources import (User, EmailBase, InvoiceBase, ThreadBase,
                                  InvoiceNodeBase, ThreadNodeBase)


class Seller(User):
    '''
    Represents a seller user
    '''
    def __init__(self, **kwargs):
        '''
        Initializes a new instance of the Seller class.
        '''
        super(Seller, self).__init__(**kwargs)
        self.__threadNode = ThreadNode(self)
        self.__emailNode = EmailNode(self)
        self.__buyerNode = BuyerNode(self)


    @property
    def uri(self):
        '''
        Gets the URI of the seller.
        @return: str
        '''
        return "sellers/me/"


    @property
    def emails(self):
        '''
        Gets access to the seller's registered email addresses.
        @return: EmailNode
        '''
        return self.__emailNode


    @property
    def threads(self):
        '''
        Gets access to the conversation threads.
        @return: ThreadNode
        '''
        return self.__threadNode


    @property
    def buyers(self):
        '''
        Gets access to the seller's customers.
        @return: BuyerNode
        '''
        return self.__buyerNode




class EmailNode(Node):
    '''
    Represents an API node giving access to emails.
    '''
    def __init__(self, seller):
        '''
        Initializes a new instance of the EmailNode class.
        @param seller:Seller Currently authenticated seller.
        '''
        self.__seller = seller
        super(EmailNode, self).__init__(seller.client, seller.uri + "emails/",
                                        Email)


    def get_resource_by_id(self, identifier):
        '''
        Gets an email by its ID.
        @param identifier:str ID of the email address.
        @return: Email
        '''
        return self.resource_class(self.__seller.client, identifier)




class Email(EmailBase):
    '''
    Represents an email address.
    '''
    def __init__(self, **kwargs):
        '''
        Initializes a new instance of the Email class.
        '''
        super(Email, self).__init__(**kwargs)
        self.__invoiceNode = InvoiceNode(self)


    @property
    def invoices(self):
        '''
        Gets access to the invoices sent with the current email address.
        @return: greendizer.dal.Node
        '''
        return self.__invoiceNode




class InvoiceNode(InvoiceNodeBase):
    '''
    Represents an API node giving access to the invoices sent by the currently
    authenticated seller.
    '''
    def __init__(self, email):
        '''
        Initializes a new instance of the InvoiceNode class.
        @param email:Email instance.
        '''
        super(InvoiceNode, self).__init__(email, Invoice)


    def send(self, xmli):
        '''
        Sends an invoice
        @param xmli:str Invoice XML representation.
        @return: InvoiceReport
        '''
        if is_empty_or_none(xmli):
            raise ValueError("Invalid XMLi")

        request = Request(self.__seller.client, method="POST",
                          content_type="application/xml", uri=self.uri,
                          data=xmli)

        response = request.get_response()
        if response.get_status_code() == 202: #Accepted
            return InvoiceReport(self.client,
                                 extract_id_from_uri(response["Location"]))




class Invoice(InvoiceBase):
    '''
    Represents an invoice.
    '''
    @property
    def custom_id(self):
        '''
        Gets the custom ID set in the initial XMLi
        @return: str
        '''
        return self._get_attribute("customId")


    def cancel(self):
        '''
        Marks the invoice as canceled.
        '''
        self._register_update("canceled", True)
        self.update()




class InvoiceReportNode(Node):
    '''
    Represents an API node giving access to invoice reports.
    '''
    def __init__(self, email):
        '''
        Initializes a new instance of the InvoiceReportNode class.
        @param email:Email Email instance.
        '''
        self.__email = email
        super(InvoiceReportNode, self).__init__(email.client,
                                                email.uri + "invoices/reports/",
                                                InvoiceReport)


    def get_resource_by_id(self, identifier):
        '''
        Gets an invoice report by its ID.
        @param identifier:str ID of the invoice report.
        @return: InvoiceReport
        '''
        return self.resource_class(self.__email, identifier)




class InvoiceReport(Resource):
    '''
    Represents an invoice delivery report.
    '''
    def __init__(self, email, identifier):
        '''
        Initializes a new instance of the InvoiceReport class.
        @param email:Email Email instance.
        @param identifier:str ID of the report.
        '''
        self.__email = email
        super(InvoiceReport, self).__init__(email.client, identifier)


    @property
    def email(self):
        '''
        Email address from which the invoices were sent.
        @return: Email
        '''
        return self.__email


    @property
    def uri(self):
        '''
        Returns the URI of the resource.
        @return: str
        '''
        return "%sinvoices/reports/%s/" % (self.__email.uri, self.id)




class ThreadNode(ThreadNodeBase):
    '''
    Represents a node giving access to conversation threads from a seller's
    perspective.
    '''
    def __init__(self, seller):
        '''
        Initializes a new instance of the SellersThreadNode class.
        @param seller:Seller Current seller instance.
        '''
        self.__seller = seller
        super(ThreadNode, self).__init__(seller.client,
                                         seller.uri + "emails/",
                                         Thread)

    @property
    def seller(self):
        '''
        Gets the current user
        @return: Seller
        '''
        return self.__seller


    def open_thread(self, recipient, subject, message):
        '''
        Opens a new thread.
        @param recipient:str ID of the recipient
        @param subject:str Subject of the thread
        @param message:str Message
        '''
        if is_empty_or_none(recipient):
            raise ValueError("Invalid recipient")

        if is_empty_or_none(subject):
            raise ValueError("Invalid subject")

        if is_empty_or_none(message):
            raise ValueError("Invalid message")

        data = {"recipient":recipient, "subject":subject, "message":message}
        request = Request(self.__seller.get_client(), method="POST",
                          uri=self.get_uri(), data=data)

        response = request.get_response()
        if response.get_status_code() == 201:
            thread_id = extract_id_from_uri(response["Location"])
            thread = self.resource_class(self.__seller, thread_id)
            thread.sync(response.data, response["Etag"])




class Thread(ThreadBase):
    '''
    Represents a conversation thread.
    '''
    def __init__(self, seller, identifier):
        '''
        Initializes a new instance of the Thread class.
        @param seller:Seller Seller instance.
        @param identifier:str ID of the thread.
        '''
        self.__seller = seller
        super(Thread, self).__init__(seller.client, identifier)


    @property
    def uri(self):
        '''
        Returns the URI of the resource.
        @return: str
        '''
        return "%sthreads/%s/" % (self.__seller.uri, self.id)




class BuyerNode(Node):
    '''
    Represents an API node giving access to info about the customers.
    '''
    def __init__(self, seller):
        '''
        Initializes a new instance of the BuyerNode class.
        @param seller:Seller Currently authenticated seller.
        '''
        self.__seller = seller
        super(BuyerNode, self).__init__(seller, seller.uri + "buyers/", Buyer)


    def get_resource_by_id(self, identifier):
        '''
        Gets a buyer by its ID.
        @param identifier:ID of the buyer.
        @return: Buyer
        '''
        return self.resource_class(self.__seller, identifier)




class Buyer(Resource):
    '''
    Represents a customer of the seller.
    '''
    def __init__(self, seller, identifier):
        '''
        Initializes a new instance of the Buyer class.
        '''
        self.__seller = seller
        super(Buyer, self).__init__(seller.client, identifier)


    @property
    def seller(self):
        '''
        Gets the currently authenticated seller.
        @return: Seller
        '''
        return self.__seller


    @property
    def uri(self):
        '''
        Gets the URI of the resource.
        @return: str
        '''
        return "%buyers/%s/" % (self.__seller.uri, self.id)


