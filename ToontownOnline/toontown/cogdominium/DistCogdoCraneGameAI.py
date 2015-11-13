from direct.directnotify.DirectNotifyGlobal import directNotify
from toontown.cogdominium.DistCogdoLevelGameAI import DistCogdoLevelGameAI
from toontown.cogdominium.DistCogdoCraneAI import DistCogdoCraneAI
from toontown.cogdominium import CogdoCraneGameConsts as GameConsts
from toontown.cogdominium.CogdoCraneGameBase import CogdoCraneGameBase

class DistCogdoCraneGameAI(DistCogdoLevelGameAI, CogdoCraneGameBase):
    notify = directNotify.newCategory('DistCogdoCraneGameAI')

    def __init__(self, air, interior):
        DistCogdoLevelGameAI.__init__(self, air, interior)
        self._cranes = [None] * self.MaxPlayers
        return

    def enterLoaded(self):
        DistCogdoLevelGameAI.enterLoaded(self)
        for i in xrange(self.MaxPlayers):
            crane = DistCogdoCraneAI(self.air, self, i)
            crane.generateWithRequired(self.zoneId)
            self._cranes[i] = crane

    def exitLoaded(self):
        for i in xrange(self.MaxPlayers):
            if self._cranes[i]:
                self._cranes[i].requestDelete()
                self._cranes[i] = None

        DistCogdoLevelGameAI.exitLoaded(self)
        return

    def enterGame(self):
        DistCogdoLevelGameAI.enterGame(self)
        for i in xrange(self.getNumPlayers()):
            self._cranes[i].request('Controlled', self.getToonIds()[i])

        self._scheduleGameDone()

    def _scheduleGameDone(self):
        timeLeft = GameConsts.Settings.GameDuration.get() - (globalClock.getRealTime() - self.getStartTime())
        if timeLeft > 0:
            self._gameDoneEvent = taskMgr.doMethodLater(timeLeft, self._gameDoneDL, self.uniqueName('boardroomGameDone'))
        else:
            self._gameDoneDL()

    def exitGame(self):
        taskMgr.remove(self._gameDoneEvent)
        self._gameDoneEvent = None
        return

    def _gameDoneDL(self, task = None):
        self._handleGameFinished()
        return task.done

    def enterFinish(self):
        DistCogdoLevelGameAI.enterFinish(self)
        self._finishDoneEvent = taskMgr.doMethodLater(10.0, self._finishDoneDL, self.uniqueName('boardroomFinishDone'))

    def exitFinish(self):
        taskMgr.remove(self._finishDoneEvent)
        self._finishDoneEvent = None
        return

    def _finishDoneDL(self, task):
        self.announceGameDone()
        return task.done

    if __dev__:

        def _handleGameDurationChanged(self, gameDuration):
            if hasattr(self, '_gameDoneEvent') and self._gameDoneEvent != None:
                taskMgr.remove(self._gameDoneEvent)
                self._scheduleGameDone()
            return
