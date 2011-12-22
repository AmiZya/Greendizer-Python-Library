from math import fsum
from xml.dom.minidom import Document
from datetime import datetime, date




CURRENCIES = ['AED', 'ALL', 'ANG', 'ARS', 'AUD', 'AWG', 'BBD', 'BDT', 'BGN',
              'BHD', 'BIF', 'BMD', 'BND', 'BOB', 'BRL', 'BTN', 'BWP', 'BYR',
              'BZD', 'CAD', 'CHF', 'CLP', 'CNY', 'COP', 'CRC', 'CUP', 'CVE',
              'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'ECS', 'EEK', 'EGP', 'ERN',
              'ETB', 'EUR', 'FJD', 'GBP', 'GHC', 'GIP', 'GMD', 'GNF', 'GTQ',
              'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'INR',
              'IQD', 'IRR', 'ISK', 'JMD', 'JOD', 'JPY', 'KES', 'KHR', 'KMF',
              'KPW', 'KRW', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD',
              'LSL', 'LTL', 'LVL', 'LYD', 'MAD', 'MDL', 'MKD', 'MLT', 'MMK',
              'MNT', 'MOP', 'MRO', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'NAD',
              'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEN', 'PGK',
              'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RUB', 'RWF', 'SAR',
              'SBD', 'SCR', 'SDG', 'SEK', 'SGD', 'SHP', 'SIT', 'SKK', 'SLL',
              'SOS', 'STD', 'SVC', 'SYP', 'SZL', 'THB', 'TND', 'TOP', 'TRY',
              'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'UYU', 'VEB', 'VND',
              'VUV', 'WST', 'XAF', 'XAG', 'XCD', 'XCP', 'XOF', 'XPD', 'XPF',
              'XPT', 'YER', 'ZAR', 'ZMK', 'ZWD']
INVOICE_DUE = "due"
INVOICE_PAID = "paid"
INVOICE_CANCELED = "canceled"
RATE_TYPE_FIXED = "fixed"
RATE_TYPE_PERCENTAGE = "percentage"
COUNTRIES = ["AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR",
             "AM", "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY", "BE",
             "BZ", "BJ", "BM", "BT", "BO", "BA", "BW", "BV", "BR", "IO", "BN",
             "BG", "BF", "BI", "KH", "CM", "CA", "CV", "KY", "CF", "TD", "CL",
             "CN", "CX", "CC", "CO", "KM", "CG", "CD", "CK", "CR", "CI", "HR",
             "CU", "CY", "CZ", "DK", "DJ", "DM", "DO", "EC", "EG", "SV", "GQ",
             "ER", "EE", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF",
             "GA", "GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD", "GP", "GU",
             "GT", "GG", "GN", "GW", "GY", "HT", "HM", "HN", "HK", "HU", "IS",
             "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP", "JE",
             "JO", "KZ", "KE", "KI", "KW", "KG", "LA", "LV", "LB", "LS", "LR",
             "LY", "LI", "LT", "LU", "MO", "MK", "MG", "MW", "MY", "MV", "ML",
             "MT", "MH", "MQ", "MR", "MU", "YT", "MX", "FM", "MD", "MC", "MN",
             "ME", "MS", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "AN", "NC",
             "NZ", "NI", "NE", "NG", "NU", "NF", "MP", "KP", "NO", "OM", "PK",
             "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR",
             "QA", "RE", "RO", "RU", "RW", "SH", "KN", "LC", "PM", "VC", "WS",
             "SM", "ST", "SA", "SN", "RS", "CS", "SC", "SL", "SG", "SK", "SI",
             "SB", "SO", "ZA", "GS", "KR", "ES", "LK", "SD", "SR", "SJ", "SZ",
             "SE", "CH", "SY", "TW", "TJ", "TZ", "TH", "TL", "TG", "TK", "TO",
             "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "US",
             "UM", "UY", "UZ", "VU", "VA", "VE", "VN", "VG", "VI", "WF", "YE",
             "ZM", "ZW"]




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
    __date = None
    __due_date = None


    def __init__(self, name=None, description=None, currency=None, status="paid",
                 date=datetime.now(), due_date=date.today(), custom_id=None,
                 terms=None):
        '''
        Initializes a new instance of the Invoice class.
        @param name:str Invoice name.
        @param description:str Invoice description.
        @param currency:str Currency
        @param status:str Invoice status.
        @param date:datetime Invoice date.
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


    def __set_name(self, value):
        '''
        Sets the name of the invoice.
        @param value:str
        '''
        if not value or not len(value):
            raise ValueError("Invalid invoice name")

        self.__name = value


    def __set_status(self, value):
        '''
        Sets the status of the invoice.
        @param value:str
        '''
        if value not in [INVOICE_DUE, INVOICE_PAID, INVOICE_CANCELED]:
            raise ValueError("Invalid invoice status")

        self.__status = value


    def __set_date(self, value):
        '''
        Sets the invoice date.
        @param value:datetime
        '''
        if value > datetime.now():
            raise ValueError("Date cannot be in the future.")

        if self.__due_date and value > self.__due_date:
            raise ValueError("Date cannot be posterior to the due date.")

        self.__date = value


    def __set_due_date(self, value):
        '''
        Sets the due date of the invoice.
        @param value:date
        '''
        if self.__date and value < self.__date:
            raise ValueError("Due date cannot be anterior to the invoice date.")

        self.__due_date = value


    def __set_currency(self, value):
        '''
        Sets the currency of the invoice.
        @param value:str
        '''
        if value not in CURRENCIES:
            raise ValueError("Invalid currency")

        self.__currency = value


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


    name = property(lambda self: self.__name, __set_name)
    status = property(lambda self: self.__status, __set_status)
    currency = property(lambda self: self.__currency, __set_currency)
    date = property(lambda self: self.__date, __set_date)
    due_date = property(lambda self: self.__due_date, __set_due_date)


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
        self._create_text_node(root, "date", self.date.isoformat())
        self._create_text_node(root, "dueDate", self.due_date.isoformat())
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


    def __set_name(self, value):
        '''
        Sets the group's name.
        @param value:str
        '''
        if not value or not len(value):
            raise ValueError("Invalid group name.")

        self.__name = value


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


    name = property(lambda self: self.__name, __set_name)


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
                 date=datetime.now(), unit_price=0, gin=None, gtin=None,
                 sscc=None):
        '''
        Initializes a new instance of the Line class.
        '''
        self.name = name
        self.description = description
        self.quantity = quantity
        self.date = date
        self.unit_price = unit_price
        self.unit = unit
        self.gin = gin
        self.gtin = gtin
        self.sscc = sscc
        self.__taxes = []
        self.__discounts = []


    def __set_name(self, value):
        '''
        Sets the line's product or service name.
        @param value:str
        '''
        if not value or not len(value):
            raise ValueError("Invalid product or service name")

        self.__name = value


    def __set_unit(self, value):
        '''
        Sets the unit of the line.
        @param value:str
        '''
        if not value or not len(value):
            raise ValueError("Invalid unit.")

        self.__unit = value


    def __set_quantity(self, value):
        '''
        Sets the quantity
        @param value:str
        '''
        try:
            self.__quantity = float(value)
        except ValueError:
            raise ValueError("Quantity must be a number")


    def __set_unit_price(self, value):
        '''
        Sets the unit price
        @param value:str
        '''
        try:
            self.__unit_price = float(value)
        except ValueError:
            raise ValueError("Unit Price must be a number")


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


    name = property(lambda self: self.__name, __set_name)
    unit = property(lambda self: self.__unit, __set_unit)
    quantity = property(lambda self: self.__quantity, __set_quantity)
    unit_price = property(lambda self: self.__unit_price, __set_unit_price)


    def to_xml(self):
        '''
        Returns a DOM representation of the line.
        @return: Element
        '''
        doc = Document()
        root = doc.createElement("line")
        self._create_text_node(root, "date", self.date.isoformat())
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


    def __set_name(self, value):
        '''
        Sets the name of the treatment.
        @param value:str
        '''
        if not value or not len(value):
            raise ValueError("Invalid name.")

        self.__name = value


    def __set_rate_type(self, value):
        '''
        Sets the rate type.
        @param value:str
        '''
        if value not in [RATE_TYPE_FIXED, RATE_TYPE_PERCENTAGE]:
            raise ValueError("Invalid rate type.")

        self.__rate_type = value


    def __set_rate(self, value):
        '''
        Sets the rate.
        @param value:float
        '''
        try:
            self.__rate = float(value)
        except ValueError:
            raise ValueError("Invalid value.")


    name = property(lambda self: self.__name, __set_name)
    rate = property(lambda self: self.__rate, __set_rate)
    rate_type = property(lambda self: self.__rate_type, __set_rate_type)


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
            else:
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


    def __set_country(self, value):
        '''
        Sets the country
        @param value:str
        '''
        if value not in COUNTRIES:
            raise ValueError("Invalid country code.")

        self.__country = value


    country = property(lambda self: self.__country, __set_country)


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

