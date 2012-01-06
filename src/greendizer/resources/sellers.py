import hashlib
from datetime import timedelta
from greendizer.base import Address, is_empty_or_none, extract_id_from_uri
from greendizer.http import Request
from greendizer.dal import Resource, Node
from greendizer.resources import (User, EmailBase, InvoiceBase, ThreadBase,
                                  MessageBase, HistoryBase, InvoiceNodeBase,
                                  ThreadNodeBase, MessageNodeBase)




class Seller(User):
    '''
    Represents a seller user
    '''
    def __init__(self, client):
        '''
        Initializes a new instance of the Seller class.
        '''
        super(Seller, self).__init__(client)
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


    def get(self, identifier, default=None, **kwargs):
        '''
        Gets an email by its ID.
        @param identifier:str ID of the email address.
        @return: Email
        '''
        return super(EmailNode, self).get(self.__seller, identifier,
                                          default=default, **kwargs)




class Email(EmailBase):
    '''
    Represents an email address.
    '''
    def __init__(self, *args, **kwargs):
        '''
        Initializes a new instance of the Email class.
        '''
        super(Email, self).__init__(*args, **kwargs)
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


    @property
    def outbox(self):
        '''
        Gets a collection to manipulate the invoices in the outbox.
        @return: Collection
        '''
        return self.search(query="location==0")


    def send(self, xmli, signature=True):
        '''
        Sends an invoice
        @param xmli:str Invoice XML representation.
        @return: InvoiceReport
        '''
        xmli = unicode(xmli)
        if is_empty_or_none(xmli):
            raise ValueError("Invalid XMLi")

        if signature and self.email.client.private_key:
            import xmldsig
            try:
                from Crypto.PublicKey import RSA
                from Crypto import Random
            except ImportError:
                raise ImportError('Pycrypto module is required to enable ' \
                                  'XMLi signing. Please visit:\n' \
                                  'http://pycrypto.sourceforge.net/')

            rsa_private = RSA.importKey(self.email.client.private_key)
            rgn = Random.new().read
            xmli = xmldsig.sign(xmli, lambda x: rsa_private.sign(x, rgn)[0],
                                '', 1024)

            #TODO: Remove this testing section 
#            import os.path
#            content = open(os.path.expanduser("~/Greendizer/pubkey.pem")).read()
#            rsa_public = RSA.importKey(content)
#            rgn = Random.new().read
#            print xmldsig.verify(xmli, lambda x: rsa_public.encrypt(x, rgn)[0],
#                                 1024)

        try:
            # 'getsizeof' method is only available for Python 2.6 and higher.
            from os import sys
            if sys.getsizeof(xmli) > 500 * 1024:
                raise ValueError("XMLi's size is limited to 500kb.")
        except AttributeError:
            pass

        request = Request(self.email.client, method="POST",
                          content_type="application/xml", uri=self._uri,
                          data=xmli)

        response = request.get_response()
        if response.status_code == 202: #Accepted
            return InvoiceReport(self.email,
                                 extract_id_from_uri(response["Location"]))




class Invoice(InvoiceBase):
    '''
    Represents an invoice.
    '''
    def __init__(self, *args, **kwargs):
        '''
        Initializes a new instance of the Invoice class.
        '''
        super(Invoice, self).__init__(*args, **kwargs)
        self.__buyer_address = None
        self.__buyer_delivery_address = None


    @property
    def custom_id(self):
        '''
        Gets the custom ID set in the initial XMLi
        @return: str
        '''
        return self._get_attribute("customId")


    @property
    def buyer_name(self):
        '''
        Gets the buyer's name as specified on the invoice.
        @return: str
        '''
        return (self._get_attribute("buyer") or {}).get("name", None)


    @property
    def buyer_email(self):
        '''
        Gets the buyer's name as specified on the invoice.
        @return: str
        '''
        return (self._get_attribute("buyer") or {}).get("email", None)


    @property
    def buyer_address(self):
        '''
        Gets the delivery address of the buyer.
        @return: Address
        '''
        address = (self._get_attribute("buyer") or {}).get("address", None)
        if not self.__buyer_address and address:
            self.__buyer_address = Address(address)

        return self.__buyer_address


    @property
    def buyer_delivery_address(self):
        '''
        Gets the delivery address of the buyer.
        @return: Address
        '''
        address = (self._get_attribute("buyer") or {}).get("delivery", None)
        if not self.__buyer_delivery_address and address:
            self.__buyer_delivery_address = Address(address)

        return self.__buyer_delivery_address


    @property
    def buyer(self):
        '''
        Gets the buyer.
        @return: Buyer
        '''
        buyer_uri = (self._get_attribute("buyer") or {}).get("uri", None)
        return self.client.seller.buyers[extract_id_from_uri(buyer_uri)]


    def cancel(self):
        '''
        Cancels the invoice.
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


    def get(self, identifier, default=None, **kwargs):
        '''
        Gets an invoice report by its ID.
        @param identifier:str ID of the invoice report.
        @return: InvoiceReport
        '''
        return super(InvoiceReportNode, self).get(self.__email, identifier,
                                                  default=default, **kwargs)




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


    @property
    def state(self):
        '''
        Gets a value indicating the stage of processing.
        @return: int
        '''
        return self._get_attribute("state") or 0


    @property
    def ip_address(self):
        '''
        Gets the IP Address of the machine which sent the request.
        @return: str
        '''
        return self._get_attribute("ipAddress")


    @property
    def hash(self):
        '''
        Gets the computed hash of the invoices received.
        @return: str
        '''
        return self._get_attribute("hash")


    @property
    def error(self):
        '''
        Gets a description of the error encountered if any.
        @return: str
        '''
        return self._get_attribute("error")


    @property
    def start(self):
        '''
        Gets the date and time on which the processing started.
        @return: datetime
        '''
        return self._get_date_attribute("startTime")


    @property
    def end(self):
        '''
        Gets the date and time on which the processing ended.
        @return: datetime
        '''
        return (self.start
                + timedelta(milliseconds=self._get_attribute("elapsedTime")))


    @property
    def invoices_count(self):
        '''
        Gets the number of invoices being processed.
        @return: int
        '''
        return self._get_attribute("invoicesCount")




class MessageNode(MessageNodeBase):
    '''
    Represents an API node giving access to messages.
    '''
    def __init__(self, thread):
        '''
        Initializes a new instance of the MessageNode class.
        @param thread: Thread  Thread instance
        '''
        super(MessageNode, self).__init__(thread, Message)





class Message(MessageBase):
    '''
    Represents a conversation thread message.
    '''
    @property
    def buyer(self):
        '''
        Gets the buyer.
        @return: Buyer
        '''
        if not self.is_from_current_user:
            buyer_id = extract_id_from_uri(self._get_attribute("buyerURI"))
            return self.thread.seller.buyers[buyer_id]




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
                                         seller.uri + "threads/",
                                         Thread)


    def get(self, identifier, default=None, **kwargs):
        '''
        Gets a thread by its ID.
        @param identifier:str ID of the thread.
        @return: Thread.
        '''
        return super(ThreadNode, self).get(self.__seller, identifier,
                                           default=default, **kwargs)


    @property
    def seller(self):
        '''
        Gets the current user
        @return: Seller
        '''
        return self.__seller




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
        self.__messageNode = MessageNode(self)


    @property
    def uri(self):
        '''
        Returns the URI of the resource.
        @return: str
        '''
        return "%sthreads/%s/" % (self.__seller.uri, self.id)


    @property
    def messages(self):
        '''
        Gets access to the messages of the thread.
        @return: MessageNode
        '''
        return self.__messageNode




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


    def get(self, identifier, default=None, **kwargs):
        '''
        Gets a buyer by its ID.
        @param identifier:ID of the buyer.
        @return: Buyer
        '''
        return super(BuyerNode, self).get(self.__seller, identifier,
                                          default=default, **kwargs)




class Buyer(HistoryBase):
    '''
    Represents a customer of the seller.
    '''
    def __init__(self, seller, identifier):
        '''
        Initializes a new instance of the Buyer class.
        '''
        self.__seller = seller
        self.__address = None
        self.__delivery_address = None
        super(Buyer, self).__init__(seller.client, identifier)


    @property
    def seller(self):
        '''
        Gets the currently authenticated seller.
        @return: Seller
        '''
        return self.__seller


    @property
    def address(self):
        '''
        Gets the address of the buyer.
        @return: Address
        '''
        if not self.__address and self._get_attribute("address"):
            self.__address = Address(self._get_attribute("address"))

        return self.__address


    @property
    def delivery_address(self):
        '''
        Gets the delivery address of the buyer.
        @return: Address
        '''
        if not self.__delivery_address and self._get_attribute("delivery"):
            self.__delivery_address = Address(self._get_attribute("delivery"))

        return self.__delivery_address


    @property
    def name(self):
        '''
        Gets the name of the buyer.
        @return: str
        '''
        return self._get_attribute("name")


    @property
    def uri(self):
        '''
        Gets the URI of the resource.
        @return: str
        '''
        return "%sbuyers/%s/" % (self.__seller.uri, self.id)
