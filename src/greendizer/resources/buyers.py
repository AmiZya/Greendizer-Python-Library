from greendizer.resources import User



class Buyer(User):
    '''
    Represents a buyer user
    '''

    @property
    def uri(self):
        '''
        Gets the URI of the resource
        @return: str
        '''
        return "buyers/me/"

