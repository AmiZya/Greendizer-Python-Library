import os.path
import base64
from greendizer.resources.buyers import Buyer
from greendizer.resources.sellers import Seller




DEBUG = False




class Client(object):
    '''
    Represents a Greendizer API client
    '''

    def __init__(self, user, access_token=None, email=None, password=None):
        '''
        Initializes a new instance of the Client class.
        Either provide an email/password, or a valid access_token
        @param user:User User resource
        @param email:str Email
        @param password:str Password
        @param access_token:str OAuth access token
        '''
        self.__authorization_header = None
        self._user = user
        self._email = email
        self._password = password
        self._access_token = access_token
        self._generate_authorization_header()


    @property
    def email_address(self):
        '''
        Gets the email address of the user
        @return: str
        '''
        return self._email


    @property
    def user(self):
        '''
        Gets the current user
        @return: User
        '''
        return self._user


    def _generate_authorization_header(self):
        '''
        Generates an HTTP authorization header depending
        on the authentication method set at the instance
        initialization.
        '''
        if self._email and self._password:
            encoded = base64.encodestring("%s:%s" % (self._email,
                                                     self._password))

            self.__authorization_header = "BASIC " + encoded.strip("\n")
        else:
            self.__authorization_header = "BEARER " + self._access_token


    def sign_request(self, request):
        '''
        Signs a request to make it pass security.
        @param request:greendizer.http.Request
        @return: greendizer.http.Request
        '''
        request["Authorization"] = self.__authorization_header
        return request




class BuyerClient(Client):
    '''
    Represents a buyer oriented client of the Greendizer API
    '''
    def __init__(self, oauth_token=None, email=None, password=None):
        '''
        Initializes a new instance of the BuyerClient class
        '''
        super(BuyerClient, self).__init__(Buyer(self), oauth_token, email,
                                          password)

    @property
    def buyer(self):
        '''
        Gets the current buyer
        @return: Buyer
        '''
        return self.user




class SellerClient(Client):
    '''
    Represents a seller oriented client of the Greendizer API
    '''
    def __init__(self, oauth_token=None, email=None, password=None):
        '''
        Initializes a new instance of the SellerClient class
        '''
        self.__private_key = None
        self.__public_key = None
        super(SellerClient, self).__init__(Seller(self), oauth_token, email,
                                           password)


    @property
    def keys(self):
        '''
        Gets the private key that will be used to sign the XMLi sent from
        this computer.
        @return: str
        '''
        if self.__private_key and self.__public_key:
            return (self.__private_key, self.__public_key)

        return None, None


    @property
    def seller(self):
        '''
        Gets the current seller
        @return: Seller
        '''
        return self.user


    def import_keys(self, private, public, passphrase=None):
        '''
        Imports the private and public keys that will be used to sign
        invoices.
        @param private:file File-like object or stream
        @param public:file File-like object or stream
        @param passphrase:str Optional pass phrase to decrypt the private key.
        '''
        try:
            from Crypto.PublicKey import RSA
        except ImportError:
            raise ImportError('PyCrypto 2.5 module is required to enable ' \
                              'XMLi signing. Please visit:\n' \
                              'http://pycrypto.sourceforge.net/')

        self.__private_key = RSA.importKey(private.read(),
                                           passphrase=passphrase)
        self.__public_key = RSA.importKey(public.read())
