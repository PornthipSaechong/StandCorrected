import webapp2
from chatter import Chatter, Messages, Data
import logging


config = {
  'webapp2_extras.auth': {
    'user_model': 'models.User',
    'user_attributes': ['name']
  },
  'webapp2_extras.sessions': {
    'secret_key': 'YOUR_SECRET_KEY'
  }
}


app = webapp2.WSGIApplication([
  (r'/?$', Chatter),
  (r'/messages?$', Messages),
  (r'/data', Data)



], debug=True, config = config)