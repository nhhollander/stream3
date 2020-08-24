
import re

##
# Authentication management class.
# This class deals with all the nitty gritty of making sure users are who they
# say they are, if that's even something that I care about.  I don't know, I'm
# mainly including this because I know if I don't someone's gonna start
# screwing with the server and causing problems.
class Auth:

    def __init__(self, config, core):
        self.config = config
        self.core = core

    ##
    # Attempt to authenticate a user, returns an authentication object on
    # success, and False if the authentication is not valid.
    def authenticate(self, name, key, user):
        if not key in self.config['auth']['keys']:
            # Invalid key
            print("Invalid key")
            return False
        keydata = self.config['auth']['keys'][key]
        if not re.match(keydata['namepattern'], name):
            # Invalid username
            print("Invalid username")
            return False
        return keydata