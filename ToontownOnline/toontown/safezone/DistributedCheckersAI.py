from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.distributed.ClockDelta import *
from direct.fsm import ClassicFSM, State
from direct.fsm import State
from direct.fsm import StateData
from direct.distributed.ClockDelta import *
from toontown.safezone import CheckersBoard

class DistributedCheckersAI(DistributedNodeAI):

    def __init__(self, air, parent, name, x, y, z, h, p, r):
        DistributedNodeAI.__init__(self, air)
        self.name = name
        self.air = air
        self.setPos(x, y, z)
        self.setHpr(h, p, r)
        self.myPos = (x, y, z)
        self.myHpr = (h, p, r)
        self.board = CheckersBoard.CheckersBoard()
        self.parent = self.air.doId2do[parent]
        self.parentDo = parent
        self.wantStart = []
        self.playersPlaying = []
        self.playersSitting = 0
        self.playersTurn = 1
        self.movesMade = 0
        self.playerNum = 1
        self.hasWon = False
        self.playersGamePos = [None, None]
        self.wantTimer = True
        self.timerEnd = 0
        self.turnEnd = 0
        self.playersObserving = []
        self.winLaffPoints = 20
        self.movesRequiredToWin = 10
        self.zoneId = self.air.allocateZone()
        self.generateOtpObject(air.districtId, self.zoneId, optionalFields=['setX',
         'setY',
         'setZ',
         'setH',
         'setP',
         'setR'])
        self.parent.setCheckersZoneId(self.zoneId)
        self.startingPositions = [[0,
          1,
          2,
          3,
          4,
          5,
          6,
          7,
          8,
          9,
          10,
          11], [20,
          21,
          22,
          23,
          24,
          25,
          26,
          27,
          28,
          29,
          30,
          31]]
        self.kingPositions = [[31,
          30,
          29,
          28], [0,
          1,
          2,
          3]]
        self.timerStart = None
        self.fsm = ClassicFSM.ClassicFSM('Checkers', [State.State('waitingToBegin', self.enterWaitingToBegin, self.exitWaitingToBegin, ['playing']), State.State('playing', self.enterPlaying, self.exitPlaying, ['gameOver']), State.State('gameOver', self.enterGameOver, self.exitGameOver, ['waitingToBegin'])], 'waitingToBegin', 'waitingToBegin')
        self.fsm.enterInitialState()
        return

    def announceGenerate(self):
        self.parent.setGameDoId(self.doId)

    def getTableDoId(self):
        return self.parentDo

    def delete(self):
        self.fsm.requestFinalState()
        self.board.delete()
        del self.fsm
        DistributedNodeAI.delete(self)

    def informGameOfPlayer(self):
        self.playersSitting += 1
        if self.playersSitting < 2:
            self.timerEnd = 0
        elif self.playersSitting == 2:
            self.timerEnd = globalClock.getRealTime() + 20
            self.parent.isAccepting = False
            self.parent.sendUpdate('setIsPlaying', [1])
        elif self.playersSitting > 2:
            pass
        self.sendUpdate('setTimer', [globalClockDelta.localToNetworkTime(self.timerEnd)])

    def informGameOfPlayerLeave(self):
        self.playersSitting -= 1
        if self.playersSitting < 2 and self.fsm.getCurrentState().getName() == 'waitingToBegin':
            self.timerEnd = 0
            self.parent.isAccepting = True
            self.parent.sendUpdate('setIsPlaying', [0])
        if self.playersSitting > 2 and self.fsm.getCurrentState().getName() == 'waitingToBegin':
            pass
        else:
            self.timerEnd = 0
        if self.timerEnd != 0:
            self.sendUpdate('setTimer', [globalClockDelta.localToNetworkTime(self.timerEnd)])
        else:
            self.sendUpdate('setTimer', [0])

    def setGameCountdownTime(self):
        self.timerEnd = globalClock.getRealTime() + 10

    def setTurnCountdownTime(self):
        self.turnEnd = globalClock.getRealTime() + 40

    def getTimer(self):
        if self.timerEnd != 0:
            return 0
        else:
            return 0

    def getTurnTimer(self):
        return globalClockDelta.localToNetworkTime(self.turnEnd)

    def requestTimer(self):
        avId = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(avId, 'setTimer', [globalClockDelta.localToNetworkTime(self.timerEnd)])

    def handlePlayerExit(self, avId):
        if avId in self.wantStart:
            self.wantStart.remove(avId)
        if self.fsm.getCurrentState().getName() == 'playing':
            gamePos = self.playersGamePos.index(avId)
            self.playersGamePos[gamePos] = None
            self.fsm.request('gameOver')
        return

    def handleEmptyGame(self):
        self.movesMade = 0
        self.playersTurn = 1
        self.playerNum = 1
        self.fsm.request('waitingToBegin')
        self.parent.isAccepting = True

    def requestWin(self):
        avId = self.air.getAvatarIdFromSender()

    def distributeLaffPoints(self):
        for x in self.parent.seats:
            if x != None:
                av = self.air.doId2do.get(x)
                av.toonUp(self.winLaffPoints)

        return

    def enterWaitingToBegin(self):
        self.setGameCountdownTime()
        self.parent.isAccepting = True

    def exitWaitingToBegin(self):
        self.turnEnd = 0

    def enterPlaying(self):
        self.parent.isAccepting = False
        for x in self.playersGamePos:
            if x != None:
                self.playersTurn = self.playersGamePos.index(x)
                self.d_sendTurn(self.playersTurn + 1)
                break

        self.setTurnCountdownTime()
        self.sendUpdate('setTurnTimer', [globalClockDelta.localToNetworkTime(self.turnEnd)])
        return

    def exitPlaying(self):
        pass

    def enterGameOver(self):
        self.timerEnd = 0
        isAccepting = True
        self.parent.handleGameOver()
        self.playersObserving = []
        self.playersTurn = 1
        self.playerNum = 1
        self.clearBoard()
        self.sendGameState([])
        self.movesMade = 0
        self.playersGamePos = [None,
         None,
         None,
         None,
         None,
         None]
        self.parent.isAccepting = True
        self.fsm.request('waitingToBegin')
        return

    def exitGameOver(self):
        pass

    def requestBegin(self):
        avId = self.air.getAvatarIdFromSender()
        if avId not in self.wantStart:
            self.wantStart.append(avId)
        numPlayers = 0
        for x in self.parent.seats:
            if x != None:
                numPlayers = numPlayers + 1

        if len(self.wantStart) == numPlayers and numPlayers >= 2:
            self.d_gameStart(avId)
            self.parent.sendIsPlaying()
        return

    def d_gameStart(self, avId):
        for x in self.playersObserving:
            self.sendUpdateToAvatarId(x, 'gameStart', [255])

        zz = 0
        numPlayers = 0
        for x in self.parent.seats:
            if x != None:
                numPlayers += 1
                self.playersPlaying.append(x)

        if numPlayers == 2:
            player1 = self.playersPlaying[0]
            self.sendUpdateToAvatarId(player1, 'gameStart', [1])
            self.playersGamePos[0] = player1
            for x in self.startingPositions[0]:
                self.board.setState(x, 1)

            player2 = self.playersPlaying[1]
            self.sendUpdateToAvatarId(player2, 'gameStart', [2])
            self.playersGamePos[1] = player2
            for x in self.startingPositions[1]:
                self.board.setState(x, 2)

        self.sendGameState([])
        self.wantStart = []
        self.fsm.request('playing')
        self.parent.getTableState()
        return

    def d_sendTurn(self, playersTurn):
        self.sendUpdate('sendTurn', [playersTurn])

    def advancePlayerTurn(self):
        if self.playersTurn == 0:
            self.playersTurn = 1
            self.playerNum = 2
        else:
            self.playerNum = 1
            self.playersTurn = 0

    def requestMove(self, moveList):
        if self.checkLegalMoves(moveList) == True:
            self.makeMove(moveList)
            self.advancePlayerTurn()
            self.d_sendTurn(self.playersTurn + 1)
            self.setTurnCountdownTime()
            self.sendUpdate('setTurnTimer', [globalClockDelta.localToNetworkTime(self.turnEnd)])
        else:
            avId = self.air.getAvatarIdFromSender()
            self.sendUpdateToAvatarId(avId, 'illegalMove', [])
            self.air.writeServerEvent('suspicious', avId, 'has requested an illegal move in Regular checkers - not possible')

    def checkLegalMoves(self, moveList):
        if self.board.squareList[moveList[0]].getState() >= 3:
            moveType = 'king'
        else:
            moveType = 'normal'
        if len(moveList) == 2:
            firstSquare = self.board.squareList[moveList[0]]
            secondSquare = self.board.squareList[moveList[1]]
            if self.checkLegalMove(firstSquare, secondSquare, moveType) == True:
                return True
            else:
                for x in range(len(moveList) - 1):
                    y = self.checkLegalJump(self.board.getSquare(moveList[x]), self.board.getSquare(moveList[x + 1]), moveType)
                    if y == False:
                        return False
                    else:
                        return True
                    return False

        elif len(moveList) > 2:
            for x in range(len(moveList) - 1):
                y = self.checkLegalJump(self.board.getSquare(moveList[x]), self.board.getSquare(moveList[x + 1]), moveType)
                if y == False:
                    return False

            return True

    def makeMove(self, moveList):
        for x in range(len(moveList) - 1):
            firstSquare = self.board.squareList[moveList[x]]
            secondSquare = self.board.squareList[moveList[x + 1]]
            if firstSquare.getNum() in secondSquare.getAdjacent():
                break
            index = firstSquare.jumps.index(secondSquare.getNum())
            self.board.squareList[firstSquare.getAdjacent()[index]].setState(0)

        haveMoved = False
        squareState = self.board.squareList[moveList[0]].getState()
        if squareState <= 2:
            piecetype = 'normal'
            if squareState == 1:
                playerNum = 1
            else:
                playerNum = 2
        else:
            piecetype = 'king'
            if squareState == 3:
                playerNum = 1
            else:
                playerNum = 2
        if piecetype == 'normal':
            lastElement = moveList[len(moveList) - 1]
            if playerNum == 1:
                if lastElement in self.kingPositions[0]:
                    self.board.squareList[moveList[0]].setState(0)
                    self.board.squareList[lastElement].setState(3)
                    haveMoved = True
                    self.sendGameState(moveList)
            elif lastElement in self.kingPositions[1]:
                self.board.squareList[moveList[0]].setState(0)
                self.board.squareList[lastElement].setState(4)
                haveMoved = True
                self.sendGameState(moveList)
        if haveMoved == False:
            spot1 = self.board.squareList[moveList[0]].getState()
            self.board.squareList[moveList[0]].setState(0)
            self.board.squareList[moveList[len(moveList) - 1]].setState(spot1)
            self.sendGameState(moveList)
        temp = self.playerNum
        self.playerNum = 1
        if self.hasWon == True:
            return
        if self.hasPeicesAndMoves(1, 3) == False:
            self.parent.announceWinner('Checkers', self.playersPlaying[1])
            self.fsm.request('gameOver')
            self.hasWon = True
            return
        self.playerNum = temp
        temp = self.playerNum
        self.playerNum = 2
        if self.hasPeicesAndMoves(2, 4) == False:
            self.parent.announceWinner('Checkers', self.playersPlaying[0])
            self.fsm.request('gameOver')
            self.hasWon = True
            return
        self.playerNum = temp

    def hasPeicesAndMoves(self, normalNum, kingNum):
        for x in self.board.squareList:
            if x.getState() == normalNum:
                if self.existsLegalMovesFrom(x.getNum(), 'normal') == True:
                    return True
                if self.existsLegalJumpsFrom(x.getNum(), 'normal') == True:
                    return True
            elif x.getState() == kingNum:
                if self.existsLegalMovesFrom(x.getNum(), 'king') == True:
                    return True
                if self.existsLegalJumpsFrom(x.getNum(), 'king') == True:
                    return True

        return False

    def getState(self):
        return self.fsm.getCurrentState().getName()

    def getName(self):
        return self.name

    def getGameState(self):
        return [self.board.getStates(), []]

    def sendGameState(self, moveList):
        gameState = self.board.getStates()
        self.sendUpdate('setGameState', [gameState, moveList])

    def clearBoard(self):
        for x in self.board.squareList:
            x.setState(0)

    def getPosHpr(self):
        return self.posHpr

    def existsLegalJumpsFrom--- This code section failed: ---

0	LOAD_FAST         'peice'
3	LOAD_CONST        'king'
6	COMPARE_OP        '=='
9	JUMP_IF_FALSE     '276'

12	SETUP_LOOP        '269'
15	LOAD_GLOBAL       'range'
18	LOAD_CONST        4
21	CALL_FUNCTION_1   None
24	GET_ITER          None
25	FOR_ITER          '268'
28	STORE_FAST        'x'

31	LOAD_FAST         'self'
34	LOAD_ATTR         'board'
37	LOAD_ATTR         'squareList'
40	LOAD_FAST         'index'
43	BINARY_SUBSCR     None
44	LOAD_ATTR         'getAdjacent'
47	CALL_FUNCTION_0   None
50	LOAD_FAST         'x'
53	BINARY_SUBSCR     None
54	LOAD_CONST        None
57	COMPARE_OP        '!='
60	JUMP_IF_FALSE     '265'
63	LOAD_FAST         'self'
66	LOAD_ATTR         'board'
69	LOAD_ATTR         'squareList'
72	LOAD_FAST         'index'
75	BINARY_SUBSCR     None
76	LOAD_ATTR         'getJumps'
79	CALL_FUNCTION_0   None
82	LOAD_FAST         'x'
85	BINARY_SUBSCR     None
86	LOAD_CONST        None
89	COMPARE_OP        '!='
92_0	COME_FROM         '60'
92	JUMP_IF_FALSE     '265'

95	LOAD_FAST         'self'
98	LOAD_ATTR         'board'
101	LOAD_ATTR         'squareList'
104	LOAD_FAST         'self'
107	LOAD_ATTR         'board'
110	LOAD_ATTR         'squareList'
113	LOAD_FAST         'index'
116	BINARY_SUBSCR     None
117	LOAD_ATTR         'getAdjacent'
120	CALL_FUNCTION_0   None
123	LOAD_FAST         'x'
126	BINARY_SUBSCR     None
127	BINARY_SUBSCR     None
128	STORE_FAST        'adj'

131	LOAD_FAST         'self'
134	LOAD_ATTR         'board'
137	LOAD_ATTR         'squareList'
140	LOAD_FAST         'self'
143	LOAD_ATTR         'board'
146	LOAD_ATTR         'squareList'
149	LOAD_FAST         'index'
152	BINARY_SUBSCR     None
153	LOAD_ATTR         'getJumps'
156	CALL_FUNCTION_0   None
159	LOAD_FAST         'x'
162	BINARY_SUBSCR     None
163	BINARY_SUBSCR     None
164	STORE_FAST        'jump'

167	LOAD_FAST         'adj'
170	LOAD_ATTR         'getState'
173	CALL_FUNCTION_0   None
176	LOAD_CONST        0
179	COMPARE_OP        '=='
182	JUMP_IF_FALSE     '188'

185	JUMP_ABSOLUTE     '265'

188	LOAD_FAST         'adj'
191	LOAD_ATTR         'getState'
194	CALL_FUNCTION_0   None
197	LOAD_FAST         'self'
200	LOAD_ATTR         'playerNum'
203	COMPARE_OP        '=='
206	JUMP_IF_TRUE      '234'
209	LOAD_FAST         'adj'
212	LOAD_ATTR         'getState'
215	CALL_FUNCTION_0   None
218	LOAD_FAST         'self'
221	LOAD_ATTR         'playerNum'
224	LOAD_CONST        2
227	BINARY_ADD        None
228	COMPARE_OP        '=='
231_0	COME_FROM         '206'
231	JUMP_IF_FALSE     '237'

234	JUMP_ABSOLUTE     '265'

237	LOAD_FAST         'jump'
240	LOAD_ATTR         'getState'
243	CALL_FUNCTION_0   None
246	LOAD_CONST        0
249	COMPARE_OP        '=='
252	JUMP_IF_FALSE     '262'

255	LOAD_GLOBAL       'True'
258	RETURN_END_IF     None
259	JUMP_ABSOLUTE     '265'

262	CONTINUE          '25'
265	JUMP_BACK         '25'
268	POP_BLOCK         None
269_0	COME_FROM         '12'

269	LOAD_GLOBAL       'False'
272	RETURN_VALUE      None
273	JUMP_FORWARD      '606'

276	LOAD_FAST         'peice'
279	LOAD_CONST        'normal'
282	COMPARE_OP        '=='
285	JUMP_IF_FALSE     '606'

288	LOAD_FAST         'self'
291	LOAD_ATTR         'playerNum'
294	LOAD_CONST        1
297	COMPARE_OP        '=='
300	JUMP_IF_FALSE     '318'

303	LOAD_CONST        1
306	LOAD_CONST        2
309	BUILD_LIST_2      None
312	STORE_FAST        'moveForward'
315	JUMP_FORWARD      '348'

318	LOAD_FAST         'self'
321	LOAD_ATTR         'playerNum'
324	LOAD_CONST        2
327	COMPARE_OP        '=='
330	JUMP_IF_FALSE     '348'

333	LOAD_CONST        0
336	LOAD_CONST        3
339	BUILD_LIST_2      None
342	STORE_FAST        'moveForward'
345	JUMP_FORWARD      '348'
348_0	COME_FROM         '315'
348_1	COME_FROM         '345'

348	SETUP_LOOP        '599'
351	LOAD_FAST         'moveForward'
354	GET_ITER          None
355	FOR_ITER          '598'
358	STORE_FAST        'x'

361	LOAD_FAST         'self'
364	LOAD_ATTR         'board'
367	LOAD_ATTR         'squareList'
370	LOAD_FAST         'index'
373	BINARY_SUBSCR     None
374	LOAD_ATTR         'getAdjacent'
377	CALL_FUNCTION_0   None
380	LOAD_FAST         'x'
383	BINARY_SUBSCR     None
384	LOAD_CONST        None
387	COMPARE_OP        '!='
390	JUMP_IF_FALSE     '595'
393	LOAD_FAST         'self'
396	LOAD_ATTR         'board'
399	LOAD_ATTR         'squareList'
402	LOAD_FAST         'index'
405	BINARY_SUBSCR     None
406	LOAD_ATTR         'getJumps'
409	CALL_FUNCTION_0   None
412	LOAD_FAST         'x'
415	BINARY_SUBSCR     None
416	LOAD_CONST        None
419	COMPARE_OP        '!='
422_0	COME_FROM         '390'
422	JUMP_IF_FALSE     '595'

425	LOAD_FAST         'self'
428	LOAD_ATTR         'board'
431	LOAD_ATTR         'squareList'
434	LOAD_FAST         'self'
437	LOAD_ATTR         'board'
440	LOAD_ATTR         'squareList'
443	LOAD_FAST         'index'
446	BINARY_SUBSCR     None
447	LOAD_ATTR         'getAdjacent'
450	CALL_FUNCTION_0   None
453	LOAD_FAST         'x'
456	BINARY_SUBSCR     None
457	BINARY_SUBSCR     None
458	STORE_FAST        'adj'

461	LOAD_FAST         'self'
464	LOAD_ATTR         'board'
467	LOAD_ATTR         'squareList'
470	LOAD_FAST         'self'
473	LOAD_ATTR         'board'
476	LOAD_ATTR         'squareList'
479	LOAD_FAST         'index'
482	BINARY_SUBSCR     None
483	LOAD_ATTR         'getJumps'
486	CALL_FUNCTION_0   None
489	LOAD_FAST         'x'
492	BINARY_SUBSCR     None
493	BINARY_SUBSCR     None
494	STORE_FAST        'jump'

497	LOAD_FAST         'adj'
500	LOAD_ATTR         'getState'
503	CALL_FUNCTION_0   None
506	LOAD_CONST        0
509	COMPARE_OP        '=='
512	JUMP_IF_FALSE     '518'

515	JUMP_ABSOLUTE     '595'

518	LOAD_FAST         'adj'
521	LOAD_ATTR         'getState'
524	CALL_FUNCTION_0   None
527	LOAD_FAST         'self'
530	LOAD_ATTR         'playerNum'
533	COMPARE_OP        '=='
536	JUMP_IF_TRUE      '564'
539	LOAD_FAST         'adj'
542	LOAD_ATTR         'getState'
545	CALL_FUNCTION_0   None
548	LOAD_FAST         'self'
551	LOAD_ATTR         'playerNum'
554	LOAD_CONST        2
557	BINARY_ADD        None
558	COMPARE_OP        '=='
561_0	COME_FROM         '536'
561	JUMP_IF_FALSE     '567'

564	JUMP_ABSOLUTE     '595'

567	LOAD_FAST         'jump'
570	LOAD_ATTR         'getState'
573	CALL_FUNCTION_0   None
576	LOAD_CONST        0
579	COMPARE_OP        '=='
582	JUMP_IF_FALSE     '592'

585	LOAD_GLOBAL       'True'
588	RETURN_VALUE      None
589	JUMP_ABSOLUTE     '595'
592	JUMP_BACK         '355'
595	JUMP_BACK         '355'
598	POP_BLOCK         None
599_0	COME_FROM         '348'

599	LOAD_GLOBAL       'False'
602	RETURN_VALUE      None
603	JUMP_FORWARD      '606'
606_0	COME_FROM         '273'
606_1	COME_FROM         '603'
606	LOAD_CONST        None
609	RETURN_VALUE      None

Syntax error at or near `CONTINUE' token at offset 262

    def existsLegalMovesFrom(self, index, peice):
        if peice == 'king':
            for x in self.board.squareList[index].getAdjacent():
                if x != None:
                    if self.board.squareList[x].getState() == 0:
                        return True

            return False
        elif peice == 'normal':
            if self.playerNum == 1:
                moveForward = [1, 2]
            elif self.playerNum == 2:
                moveForward = [0, 3]
            for x in moveForward:
                if self.board.squareList[index].getAdjacent()[x] != None:
                    adj = self.board.squareList[self.board.squareList[index].getAdjacent()[x]]
                    if adj.getState() == 0:
                        return True

            return False
        return

    def existsLegalJumpsFrom(self, index, peice):
        if peice == 'king':
            for x in range(4):
                if self.board.squareList[index].getAdjacent()[x] != None and self.board.squareList[index].getJumps()[x] != None:
                    adj = self.board.squareList[self.board.squareList[index].getAdjacent()[x]]
                    jump = self.board.squareList[self.board.squareList[index].getJumps()[x]]
                    if adj.getState() == 0:
                        pass
                    elif adj.getState() == self.playerNum or adj.getState() == self.playerNum + 2:
                        pass
                    elif jump.getState() == 0:
                        return True

            return False
        elif peice == 'normal':
            if self.playerNum == 1:
                moveForward = [1, 2]
            elif self.playerNum == 2:
                moveForward = [0, 3]
            for x in moveForward:
                if self.board.squareList[index].getAdjacent()[x] != None and self.board.squareList[index].getJumps()[x] != None:
                    adj = self.board.squareList[self.board.squareList[index].getAdjacent()[x]]
                    jump = self.board.squareList[self.board.squareList[index].getJumps()[x]]
                    if adj.getState() == 0:
                        pass
                    elif adj.getState() == self.playerNum or adj.getState() == self.playerNum + 2:
                        pass
                    elif jump.getState() == 0:
                        return True

            return False
        return

    def checkLegalMove(self, firstSquare, secondSquare, peice):
        if self.playerNum == 1:
            moveForward = [1, 2]
        else:
            moveForward = [0, 3]
        if peice == 'king':
            for x in range(4):
                if firstSquare.getAdjacent()[x] != None:
                    if self.board.squareList[firstSquare.getAdjacent()[x]].getState() == 0:
                        return True

            return False
        elif peice == 'normal':
            for x in moveForward:
                if firstSquare.getAdjacent()[x] != None:
                    if self.board.squareList[firstSquare.getAdjacent()[x]].getState() == 0:
                        return True

            return False
        return

    def checkLegalJump(self, firstSquare, secondSquare, peice):
        if self.playerNum == 1:
            moveForward = [1, 2]
            opposingPeices = [2, 4]
        else:
            moveForward = [0, 3]
            opposingPeices = [1, 3]
        if peice == 'king':
            if secondSquare.getNum() in firstSquare.getJumps():
                index = firstSquare.getJumps().index(secondSquare.getNum())
                if self.board.squareList[firstSquare.getAdjacent()[index]].getState() in opposingPeices:
                    return True
                else:
                    return False
        elif peice == 'normal':
            if secondSquare.getNum() in firstSquare.getJumps():
                index = firstSquare.getJumps().index(secondSquare.getNum())
                if index in moveForward:
                    if self.board.squareList[firstSquare.getAdjacent()[index]].getState() in opposingPeices:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
# VERIFICATION FAILED
