from math import fsum
from xml.dom.minidom import Document
from datetime import datetime, date




INVOICE_DUE = "due"
INVOICE_PAID = "paid"
INVOICE_CANCELED = "canceled"
RATE_TYPE_FIXED = "fixed"
RATE_TYPE_PERCENTAGE = "percentage"




class XMLiElement(object):
    '''
    Represents an XMLi element.
    '''
    def _create_text_node(self, root, name, value, cdata=False):
        '''
        Creates and adds a text node
        @param root:Element Root element
        @param name:str Tag name
        @param value:object Text value
        @param cdata:bool A value indicating whether to use CDATA or not.
        @return:Node
        '''
        tag = root.createElement(name)
        if cdata:
            tag.appendChild(root.ownerDocument.createCDATASection(value))
        else:
            tag.appendChild(root.ownerDocument.createTextNode(value))

        return tag


    def _create_attribute(self, root, name, value):
        '''
        Creates and adds an attribute.
        @param root:Element Root element.
        @param name:str Attribute name.
        @param value:object Attribute value.
        '''
        attribute = root.createAttribute(name)
        attribute.value = value
        return attribute


    def to_xml(self):
        '''
        Returns a DOM element containing the XML representation of the XMLi
        element.
        @return: Element
        '''
        raise NotImplementedError()


    def to_string(self, prettify=False, **kwargs):
        '''
        Returns a string representation of the XMLi element.
        @return: str
        '''
        printArgs = {"encoding":"UTF-8"}
        if not prettify:
            printArgs.update({"indent":"", "newl": ""})

        return self.to_xml(**kwargs).toprettyprint(**printArgs)


    def __str__(self):
        '''
        Returns a string representation of the XMLi element.
        @return: str
        '''
        return self.to_string()




class ExtensibleXMLiElement(XMLiElement):
    '''
    Represents an XMLi element that can be extended with its own set of 
    custom tags.
    '''
    def __init__(self, **kwargs):
        '''
        Initializes a new instance of the ExtensibleXMLiElement class.
        '''
        super(ExtensibleXMLiElement, self).__init__(**kwargs)
        self.__custom_elements = {}


    def __getitem__(self, namespace):
        '''
        Gets the items of a specific namespace.
        @param namespace:XMLNamespace
        @return: dict
        '''
        if namespace not in self.__custom_elements:
            self.__custom_elements[namespace] = {}

        return self.__custom_elements[namespace]


    def __delitem(self, namespace):
        '''
        Deletes the items of a specific namespace.
        @param namespace:XMLNamespace
        @return: dict
        '''
        if namespace not in self.__custom_elements:
            del self.__custom_elements[namespace]


    def __createElementNS(self, root, uri, tag):
        '''
        Creates and returns an element with a qualified name and a name space
        @param root:Element Parent element
        @param uri:str Namespace URI
        @param tag:str Tag name.
        '''
        return root.appendChild(root.ownerDocument.createElementNS(uri, tag))


    def to_xml(self, root):
        '''
        Returns a DOM element contaning the XML representation of the
        ExtensibleXMLiElement
        @param root:Element Root XML element.
        @return: Element
        '''
        custom = root.appendChild(root.ownerDocument.createElement("custom"))

        for uri, tags in self.__custom_elements:
            for name, value in tags:
                item = self.__createElementNS(custom, uri, name)
                self._create_text_node(item, name, value, True)

        return root




class XMLiBuilder(XMLiElement):
    '''
    Encapsulates methods and tools to generate a valid XMLi.
    '''
    def __init__(self):
        '''
        Initializes a new instance of the XMLiBuilder class.
        '''
        self.__invoices = {}


    def to_xml(self):
        '''
        Returns a DOM Document representing the invoice
        @return: Document
        '''
        doc = Document()
        root = doc.createElement("invoices")
        for invoice in self.__invoices:
            root.appendChild(invoice.to_xml())

        return doc




class Invoice(ExtensibleXMLiElement):
    '''
    Represents an Invoice object in the XMLi.
    '''
    def __init__(self, name=None, description="", currency=None, status="paid",
                 date=date.today(), due_date=date.today(), custom_id=None,
                 terms=None):
        '''
        Initializes a new instance of the Invoice class.
        @param name:str Invoice name.
        @param description:str Invoice description.
        @param currency:str Currency
        @param status:str Invoice status.
        @param date:date Invoice date.
        @param due_date:date Invoice's due date.
        '''
        self.name = name
        self.description = description
        self.currency = currency
        self.status = status
        self.date = date
        self.due_date = due_date
        self.custom_id = custom_id
        self.terms = terms
        self.__groups = []


    @property
    def total_discounts(self):
        '''
        Gets the total amount of discounts of the invoice.
        @return: float
        '''
        return fsum([group.total_discounts for group in self.__groups])


    @property
    def total_taxes(self):
        '''
        Gets the total amount of taxes of the invoice.
        @return: float
        '''
        return fsum([group.total_taxes for group in self.__groups])


    @property
    def total(self):
        '''
        Gets the total of the invoice.
        @return: float
        '''
        return fsum([group.total for group in self.__groups])


    def to_xml(self):
        '''
        Returns a DOM element containing the XML representation of the invoice
        @return:Element
        '''
        doc = Document()
        root = doc.createElement("invoice")
        self._create_text_node(root, "name", self.name, True)
        self._create_text_node(root, "description", self.description, True)
        self._create_text_node(root, "currency", self.currency)
        self._create_text_node(root, "status", self.status)
        self._create_text_node(root, "date", self.date)
        self._create_text_node(root, "dueDate", self.due_date)
        self._create_text_node(root, "customId", self.custom_id, True)
        self._create_text_node(root, "terms", self.terms, True)
        self._create_text_node(root, "total", self.total)

        body = root.createElement("body")
        for group in self.__groups:
            body.appendChild(group.to_xml())

        #Adding custom elements
        super(Invoice, self).to_xml(body)

        root.unlink()
        return root




class Group(ExtensibleXMLiElement):
    '''
    Represents a group of lines in the XMLi.
    '''
    def __init__(self, name=None, description=""):
        '''
        Initializes a new instance of the Group class.
        @param name:str Group name.
        @param description:str Group description.
        '''
        self.name = name
        self.description = description
        self.__lines = []


    @property
    def total_discounts(self):
        '''
        Gets the total amount of discounts of the group.
        @return: float
        '''
        return fsum([line.total_discounts for line in self.__lines])


    @property
    def total_taxes(self):
        '''
        Gets the total amount of taxes of the group.
        @return: float
        '''
        return fsum([line.total_taxes for line in self.__lines])


    @property
    def total(self):
        '''
        Gets the total of the group.
        @return: float
        '''
        return fsum([line.total for line in self.__lines])


    def to_xml(self):
        '''
        Returns a DOM representation of the group.
        @return: Element
        '''
        doc = Document()
        root = doc.createElement("group")
        for line in self.__lines:
            root.appendChild(line.to_xml())
        super(Group, self).to_xml(root)
        root.unlink()
        return root




class Line(ExtensibleXMLiElement):
    '''
    Represents an invoice body line.
    '''
    def __init__(self, name=None, description="", unit=None, quantity=0,
                 unit_price=0, gin=None, gtin=None, sscc=None):
        '''
        Initializes a new instance of the Line class.
        '''
        self.name = name
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.unit = unit
        self.gin = gin
        self.gtin = gtin
        self.sscc = sscc
        self.__taxes = []
        self.__discounts = []


    @property
    def gross(self):
        '''
        Gets the gross total
        @return: float
        '''
        return self.unit_price * self.quantity


    @property
    def total_discounts(self):
        '''
        Gets the total amount of discounts applied to the current line.
        @return: float
        '''
        return fsum([ d.compute(self.gross) for d in self.__discounts ])


    @property
    def total_taxes(self):
        '''
        Gets the total amount of taxes applied to the current line.
        @return: float
        '''
        base = self.gross - self.discounts
        return fsum([ t.compute(base) for t in self.__taxes ])


    @property
    def total(self):
        '''
        Gets the total of the line.
        @return: float
        '''
        return self.gross + self.total_taxes - self.total_discounts


    def to_xml(self):
        '''
        Returns a DOM representation of the line.
        @return: Element
        '''
        doc = Document()
        root = doc.createElement("line")
        self._create_text_node(root, "name", self.name, True)
        self._create_text_node(root, "description", self.description, True)
        self._create_text_node(root, "quantity", self.quantity)
        self._create_text_node(root, "unitPrice", self.unit_price)
        self._create_text_node(root, "unit", self.unit)
        self._create_text_node(root, "gin", self.gin)
        self._create_text_node(root, "gtin", self.gtin)
        self._create_text_node(root, "sscc", self.sscc)

        for treatment in (self.__taxes + self.__discounts):
            root.appendChild(treatment.to_xml())

        super(Line, self).to_xml(root)

        root.unlink()
        return root




class Treatment(XMLiElement):
    '''
    Represents a line treatment.
    '''
    def __init__(self, name=None, rate=0, rate_type=RATE_TYPE_FIXED,
                 interval=None):
        '''
        Initializes a new instance of the Treatment class.
        @param name:str Treatment name.
        @param rate:float Rate level
        @param rate_type:str Rate type
        '''
        self.name = name
        self.rate = rate
        self.rate_type = rate_type


    def compute(self, base):
        '''
        Computes the amount of the treatment.
        @param base:float Gross
        @return: float
        '''
        if base <= 0:
            return 0

        if self.rate_type == RATE_TYPE_FIXED:
            if not self.interval or base < self.interval.lower:
                return self.rate

            return 0

        if not self.interval:
            return base * self.rate / 100

        if base > self.interval.lower:
            return ((min(base, self.interval.upper) - self.interval.lower)
                    * self.rate / 100)

        return 0


    def to_xml(self, name):
        '''
        Returns a DOM representation of the line treatment.
        @return: Element
        '''
        doc = Document()
        root = doc.createElement(name)
        self._create_attribute(root, "type", self.rate_type)
        self._create_attribute(root, "name", self.name)
        self._create_attribute(root, "base", self.interval)
        root.appendChild(doc.createTextNode(self.rate))
        root.unlink()
        return root




class Tax(Treatment):
    '''
    Represents a tax.
    '''
    def to_xml(self):
        '''
        Returns a DOM representation of the tax.
        @return: Element
        '''
        return super(Tax, self).to_xml("tax")


    def to_string(self):
        '''
        Returns a string representation of the tax.
        @return: str
        '''
        return super(Tax, self).to_string("tax")




class Discount(Treatment):
    '''
    Represents a discount.
    '''
    def compute(self, base):
        '''
        Returns the value of the discount.
        @param base:float Computation base.
        @return: float
        '''
        return min(base, super(Discount, self).compute(base))


    def to_xml(self):
        '''
        Returns a DOM representation of the discount.
        @return: Element
        '''
        return super(Discount, self).to_xml("discount")


    def to_string(self):
        '''
        Returns a string representation of the discount.
        @return: str
        '''
        return super(Discount, self).to_string("discount")




class Address(XMLiElement):
    '''
    Represents a postal address
    '''
    def __init__(self, number=None, street=None, city=None, zipcode=None,
                 state=None, country=None):
        '''
        Initializes a new instance of the Address class.
        @param number:str Street number
        @param street:str Street name
        @param city:str City
        @param zipcode:str Zipcode
        @param state:str State
        @param country:str Country
        '''
        self.number = number
        self.street = street
        self.city = city
        self.zipcode = zipcode
        self.state = state
        self.country = country


    def to_xml(self, name="address"):
        '''
        Returns a DOM Element containing the XML representation of the
        address.
        @return:Element 
        '''
        doc = Document()
        root = doc.createElement(name)
        self._create_text_node(root, "number", self.number)
        self._create_text_node(root, "street", self.street, True)
        self._create_text_node(root, "city", self.city, True)
        self._create_text_node(root, "zipcode", self.zipcode)
        self._create_text_node(root, "state", self.state, True)
        self._create_text_node(root, "country", self.country)
        root.unlink()
        return root
