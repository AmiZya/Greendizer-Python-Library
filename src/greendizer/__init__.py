import base64
from greendizer.resources.buyers import Buyer
from greendizer.resources.sellers import Seller



class Client(object):
    '''
    Represents a Greendizer API client
    '''

    def __init__(self, user, email=None, password=None, access_token=None):
        '''
        Initializes a new instance of the Client class.
        Either provide an email/password, or a valid access_token
        @param user:User User resource
        @param email:str Email
        @param password:str Password
        @param access_token:str OAuth access token
        '''
        self._user = user
        self.__email = email
        self.__password = password
        self.__access_token = access_token


    @property
    def email(self):
        '''
        Gets the email address of the user
        @return: str
        '''
        return self.__email


    @property
    def user(self):
        '''
        Gets the current user
        @return: User
        '''
        return self._user


    def generate_authorization_header(self):
        '''
        Generates an HTTP authorization header depending
        on the authentication method set at the instance
        initialization.
        '''
        if self.__email and self.__password:
            return base64.encode("%s:%s" % (self.__email, self.__password))

        return "BEARER " + self.__access_token




class BuyerClient(Client):
    '''
    Represents a buyer oriented client of the Greendizer API
    '''
    def __init__(self, email=None, password=None, oauth_token=None):
        '''
        Initializes a new instance of the BuyerClient class
        '''
        super(BuyerClient, self).__init__(Buyer(self), email, password,
                                          oauth_token)

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
    def __init__(self, email=None, password=None, oauth_token=None):
        '''
        Initializes a new instance of the SellerClient class
        '''
        super(SellerClient, self).__init__(Seller(self), email, password,
                                          oauth_token)


    @property
    def seller(self):
        '''
        Gets the current seller
        @return: Seller
        '''
        return self.user

