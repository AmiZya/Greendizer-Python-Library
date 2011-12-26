import unittest
from greendizer import SellerClient
from greendizer.xmli import (XMLiBuilder, Invoice, Group, Line, Discount, Tax,
                             Address)


class XMLiTestCase(unittest.TestCase):

    def setUp(self):
        self.__seller = SellerClient(email="jimi.hendrix@greendizer.com",
                             password="password").seller


    def test_generate_xmli(self):

        invoice = Invoice(name="My Invoice", description="Christmas time",
                          currency="EUR", status="paid", terms="No terms")

        invoice["sfr:https://www.fender.com/"]["points"] = "15 points"

        invoice.buyer.name = "Mohamed Attahri"
        invoice.buyer.email = "mohamed@attahri.com"
        invoice.buyer.address = Address(country="FR", city="Paris",
                                        zipcode="75015",
                                        street_address="15, rue de Chambery")


        invoice.shipping.recipient = invoice.buyer


        builder = XMLiBuilder()
        builder.invoices.append(invoice)

        group = Group(name="Main")
        invoice.groups.append(group)

        discount = Discount(name="Refund", description="-50", rate="50",
                  rate_type="fixed")

        tax = Tax(name="VAT", description="VAT 19.6", rate="19.6",
                  rate_type="percentage")

        for i in range(0, 10):
            line = Line(name="EX250 JH-%s" % i, quantity=i, unit_price=3 * i)
            group.lines.append(line)
            line.discounts.append(discount)
            line.taxes.append(tax)

        self.__seller.emails[self.__seller.client.email_address].invoices.send(builder)



