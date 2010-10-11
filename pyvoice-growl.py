from repeattimer import RepeatTimer
from pyvoice import GoogleVoice
from Growl import GrowlNotifier
from Growl import Image as GrowlImage

def notify():
    unread_messages = gv.get_unread_messages()
    for msg in unread_messages:
	growlifier.notify(noteType="update",
	    title="New GV Message!",
	    description=("%s- %s" % (msg.elapsedTimeSincePlaced, msg.phoneNumber)))

icon_path = "txt.icon.png"
if (__name__ == "__main__"):
    growl_icon = GrowlImage.imageFromPath(icon_path)

    growlifier = GrowlNotifier(applicationName="Google Voice",
	notifications=['update'],
	applicationIcon=growl_icon)
    growlifier.register()


    gv = GoogleVoice("alex.spinnler@gmail.com",
	"laner8")

    #check for new messages, and update with new Growl alert every 10 minutes
    timer = RepeatTimer(interval=600, function=notify)
    timer.run()


