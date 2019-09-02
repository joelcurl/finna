from pykeepass import PyKeePass

class KeepassCredentials:
    def __init__(self, keepass_file, password):
        self.creds = PyKeePass(keepass_file, password)
    
    def username(self, entry_title):
        return self.entry(entry_title).username

    def password(self, entry_title):
        return self.entry(entry_title).password

    def entry(self, entry_title):
        return self.creds.find_entries(title=entry_title, recursive=True, first=True)

#import os
#kpc = KeepassCredentials(os.environ['CREDS_PATH'], os.environ['CREDS_PASS'])
#print(kpc.username('Voya'))
#print(kpc.password('Voya'))

