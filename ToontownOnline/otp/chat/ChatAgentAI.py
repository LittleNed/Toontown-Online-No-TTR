from direct.directnotify import DirectNotifyGlobal
# TODO: OTP should not depend on Toontown... Hrrm.
from toontown.chat.TTWhiteList import TTWhiteList

class ChatAgentAI:
    notify = DirectNotifyGlobal.directNotify.newCategory("ChatAgentAI")

    def announceGenerate(self):
        pass

    def chatMessage(self, todo0):
        pass

    def setWhiteList(self, todo0):
        pass