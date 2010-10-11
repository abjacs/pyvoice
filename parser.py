import xml.sax as sax
import xml.sax.handler
import simplejson

class XMLJsonHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
	self.json = []
	self.isJsonObject = 0

    def startElement(self, name, attributes):
	if (name == "json"):
	    self.buffer = ""
	    self.isJsonObject = 1

    def characters(self, data):
	if (self.isJsonObject):
	    self.buffer += data

    def endElement(self, name):
	if (name == "json"):
	    self.json.append(self.buffer);
	    self.isJsonObject = 0

class JsonParserFactory(object):
    @staticmethod
    def getParser(handler):
	parser = sax.make_parser()
	parser.setContentHandler(handler)

	return parser

class JsonParser(object):

    @staticmethod
    def getJson(raw_feed):
	jsonHandler = XMLJsonHandler()
	xmlParser = JsonParserFactory.getParser(jsonHandler)
	xmlParser.parse(raw_feed)

	return simplejson.loads(jsonHandler.json[0])