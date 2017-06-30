from google.appengine.api import memcache
from google.appengine.ext import ndb

from logic.Logic import Authenticate

class User(ndb.Model):
	password = ndb.StringProperty(required=True)
	salt = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)
	phone = ndb.IntegerProperty(required=True)
	mobile_log_in=ndb.BooleanProperty(default=False)
	# favourites = db.StringArrayProperty()
	bike_owned=ndb.KeyProperty(kind='Bike')
	
	@classmethod
	def by_id(cls, uid):
	        return cls.get_by_id(uid)
	@classmethod
	def by_email(cls,query):
		#return db.GqlQuery('SELECT * FROM User WHERE username = :query',query=query)
		return cls.query(cls.email==query)

	@classmethod
	def login(cls, email, pw):
        	u = cls.by_email(email)
	        if u and Authenticate.check_user(u.get(),pw):
			return u.get()

	@classmethod               
	def register(cls,pw,email,phone):	
	    	q= cls.by_email(email)
	        user = q.get()
	        # check if datastore if this username exist
	        if user:
	        	return None
	        else:
	            # register it this username is new
	        	hash_pw=Authenticate.hash_function(pw,salt="")
	        	salt=hash_pw.split('|')[1][:12]
	        	user=cls(password=hash_pw.split('|')[0],salt=salt,email=email,phone=long(phone))
	        	user.put()
	        	return user

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class ChatRoom(ndb.Model):

	chat_id = ndb.StringProperty(required=True)
	text_index = ndb.IntegerProperty(default=0)
	first_name = ndb.StringProperty(default="")
	last_name = ndb.StringProperty(default="")
	username = ndb.StringProperty(default="")
	date_added = ndb.StringProperty(default="")
	date_deleted = ndb.StringProperty(default="")

	@classmethod
	def register(cls,chat_id,first_name,last_name,username,date_added):
		chat = cls.query(cls.chat_id==chat_id).fetch()
		if not chat:
			chat = cls(chat_id=chat_id,first_name=first_name,last_name=last_name,username=username,date_added=date_added)
			chat.put()
			return True
		else:
			return False

	@classmethod
	def delete_chat(cls,chat_id,date_deleted):
		chat = cls.query(cls.chat_id==chat_id).fetch()
		if chat:
			for c in chat:
				# if not c.date_deleted:
				c.date_deleted=date_deleted
				c.put()
		else:
			return