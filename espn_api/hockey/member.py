class Member(object):
    
    def __init__(self, data):
        self.id = data['id']
        self.display_name = data['displayName']
        self.first_name =  data['firstName']
        self.last_name = data['lastName']
        self.full_name = self.first_name + ' ' + self.last_name
        
