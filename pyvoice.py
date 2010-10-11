import urllib
import urllib2
import re
from parser import *

class GoogleVoice(object):
    #set class attributes
    Login_Url = "https://www.google.com/accounts/Login"
    Authenticate_Url = "https://www.google.com/accounts/ServiceLoginAuth"
    GV_HomePage_Url = "https://www.google.com/voice/"

    SMS_URL = "https://www.google.com/voice/inbox/recent/sms/"
    RECENT_URL = "https://www.google.com/voice/inbox/recent/"

    #Google Client login data
    Source = "pyvoicesms-0.1"
    Service = "grandcentral"
    #could also be HOSTED or HOSTED_OR_GOOGLE
    AccountType = "Google"

    #user credents
    Username = "alex.spinnler@gmail.com"
    Password = "laner8"

    #create login url
    Login_Data = {
	"accountType": AccountType,
	"Email" : Username,
	"Passwd" : Password,
	"service" : Service,
	"source" : Source,
    }

    headers = {
	'Content-type': 'application/x-www-form-urlencoded;charset=utf-8',
	'User-Agent': Source
    }

    def __init__(self, name, pw):
	self.name = name
	self.pw = pw
	self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
	self.auth_data = {
	    "accountType": GoogleVoice.AccountType,
	    "Email" : self.name,
	    "Passwd" : self.pw,
	    "service" : GoogleVoice.Service,
	    "source" : GoogleVoice.Source,
	}

	self.rnrse = None

	self._setup()

    def _setup(self):
	#self.opener is declared in __init__
	#login, and grab rnrse authentication token
	# create and opener, and add an http cookie process handler
	#self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())

	# this installs our opener as the global default opener
	# now we can go our merry way using urlopen() and it will use our newly installed opener....
	urllib2.install_opener(self.opener)

	#grab GALX from Google login page
	login_page_contents = self.opener.open(GoogleVoice.Login_Url).read()

	# Find GALX value
	galx_match_obj = re.search(r'name="GALX"\s*value="([^"]+)"', login_page_contents, re.IGNORECASE)
	galx_value = galx_match_obj.group(1) if galx_match_obj.group(1) is not None else ''

	#
	##
	###
	# works up to here...
	###
	##
	#

	#update data we're going to post to Google Login with GALX credents
	GoogleVoice.Login_Data.update({'GALX': galx_value})

	#login via authentication URL
	self.auth_data = GoogleVoice.Login_Data
	self.opener.open(GoogleVoice.Authenticate_Url, urllib.urlencode(self.auth_data))

	#if we have logged in, then we can go to our GV home page
	gv_home_page = self.opener.open(GoogleVoice.GV_HomePage_Url).read()

	#now we need to grab the rnrsee token
	#that Google uses to validate requests to the Google Voice API....
	#how fucking merry that is.....
	# Find _rnr_se value
	#don't know why we use group(1), and I don't care to know at this moment
	self.rnrse = re.search('name="_rnr_se".*?value="(.*?)"', gv_home_page).group(1)

	#we should check to see if rnrse is None and throw an exception
	#since this means our login was unsuccessful

    #return collection of Messages
    ##
    #this doesn't actually return ALL messages
    #it just returns the 10 most recent from the inbox
    ##
    def get_all_messages(self):
	messages = []
	messages_feed = self._get_msg_feed()


	messages_feed = messages_feed['messages']
	for key in messages_feed.keys():
	    msg = messages_feed[key]
	    msg = Message(msg['displayStartDateTime'],
			msg['relativeStartTime'],
			msg['displayNumber'],
			msg['isRead']
			);
	    messages.append(msg)
	return messages

    #return collection of Messages with isRead = 0
    def get_unread_messages(self):
	all_messages = self.get_all_messages()
	unread_messages = [msg for msg in all_messages if msg.isRead == 0]
	return unread_messages


    def _get_msg_feed(self):
	raw_msg_feed = self.opener.open(GoogleVoice.RECENT_URL)
	jsonData = JsonParser.getJson(raw_msg_feed)
	return jsonData

    def _get_sms_feed(self):
	raw_sms_feed = self.opener.open(GoogleVoice.SMS_URL)
	jsonData = JsonParser.getJson(raw_sms_feed)
	return jsonData


class Message(object):
    def __init__(self, startDateTime, timeSincePlaced, phoneNumber, isRead):
	self.startDateTime = startDateTime
	self.elapsedTimeSincePlaced = timeSincePlaced
	#Python's version of ternary statement- use 'Unknown' if phoneNumber is empty...
	self.phoneNumber = phoneNumber if len(phoneNumber) > 0 else 'Unknown'
	self.isRead = isRead