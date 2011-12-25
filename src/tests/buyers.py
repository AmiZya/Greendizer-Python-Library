#import unittest
#import random
#from datetime import datetime, date
#from greendizer import BuyerClient
#
#
#
#STATIC_URL = u"http://greendizer-local-public.s3.amazonaws.com/"
#INVOICE_ID = "11"
#
#
#
#class BuyerTestCase(unittest.TestCase):
#
#    def setUp(self):
#        client = BuyerClient(email="jimi.hendrix@greendizer.com",
#                             password="password")
#        self.__buyer = client.buyer
#
#
#
#
#    def test_first_name(self):
#        self.assertEqual(self.__buyer.first_name, "Jimi")
#
#    def test_last_name(self):
#        self.assertEqual(self.__buyer.last_name, "Hendrix")
#
#    def test_full_name(self):
#        self.assertEqual(self.__buyer.full_name, "Jimi Hendrix")
#
#    def test_birthday(self):
#        self.assertEqual(self.__buyer.birthday, date(1942, 2, 18))
#
#    def test_avatar_url(self):
#        self.assertEqual(self.__buyer.avatar_url,
#                         (STATIC_URL + "avatars/p%s.png?%s" %
#                          (self.__buyer.id, self.__buyer.etag.timestamp)))
#
#
#
#
#    def test_settings_language(self):
#        self.assertEqual(self.__buyer.settings.language, "en")
#
#    def test_settings_region(self):
#        self.assertEqual(self.__buyer.settings.region, "en-US")
#
#    def test_settings_currency(self):
#        self.assertEqual(self.__buyer.settings.currency, "USD")
#
#
#
#
#    def test_company_name(self):
#        self.assertEqual(self.__buyer.company.name, "Hendrixino")
#
#    def test_company_description(self):
#        self.assertEqual(self.__buyer.company.description, None)
#
#    def test_company_small_logo_url(self):
#        if not self.__buyer.company.exists:
#            self.assertTrue(True)
#
#        suffix = "c%s.16.png?%s" % (self.__buyer.company.id,
#                                self.__buyer.company.etag.timestamp)
#
#        self.assertEqual(self.__buyer.company.small_logo_url,
#                         (STATIC_URL + "companies/" + suffix))
#
#    def test_company_large_logo_url(self):
#        if not self.__buyer.company.exists:
#            self.assertTrue(True)
#
#        suffix = "c%s.128.png?%s" % (self.__buyer.company.id,
#                                     self.__buyer.company.etag.timestamp)
#
#        self.assertEqual(self.__buyer.company.large_logo_url,
#                         (STATIC_URL + "companies/" + suffix))
#
#
#
#
#    def test_email_label(self):
#        label = self.__buyer.emails[self.__buyer.client.email_address].label
#        self.assertEqual(label, "Work")
#
#
#
#
#    def test_invoice_existence(self):
#        email = self.__buyer.emails[self.__buyer.client.email_address]
#        self.assertTrue(INVOICE_ID in email.invoices)
#
#
#    def test_invoice_inexistence(self):
#        email = self.__buyer.emails[self.__buyer.client.email_address]
#        self.assertTrue("99999999" not in email.invoices)
#
#
#    def test_invoice_fallback(self):
#        email = self.__buyer.emails[self.__buyer.client.email_address]
#        self.assertTrue(email.invoices.get("999999999") == None)
