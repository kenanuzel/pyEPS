import unittest
import time
import random

from eps.utils.io import IoService, localhost
from eps.procedures.mme.s6a import AuthenticationInformationRetrievalProcedureHandler as MmeAuthProcedureHandler
from eps.procedures.hss.s6a import AuthenticationInformationRetrievalProcedureHandler as HssAuthProcedureHandler


class TestS1SetupProcedureHandler(unittest.TestCase):

    def setUp(self):
        self.hssIoService = IoService("hss", 9000)
        self.hssIoService.start()
        self.mmeIoService = IoService("mme", 9001)
        self.mmeIoService.start()
        self.mmeSuccessCount, self.hssSuccessCount = 0, 0

    def tearDown(self):
        self.hssIoService.stop()
        self.mmeIoService.stop()

    def __mmeAuthCompleteCallback__(self, result, authContext=None):
        if result == MmeAuthProcedureHandler.Success:
            self.mmeSuccessCount += 1
            

    def __hssAuthCompleteCallback__(self, result, imsi):
        if result == HssAuthProcedureHandler.Success:
            self.hssSuccessCount += 1

    def test_nAuthInfoRetrievalProcedureSuccess(self):
        n = 100
        visitedPlmnId = "28603"
        mmeAuthProcHandler = MmeAuthProcedureHandler((localhost(), 9000), self.mmeIoService, self.__mmeAuthCompleteCallback__)
        self.mmeIoService.addIncomingMessageCallback(mmeAuthProcHandler.handleIncomingMessage)
        hssAuthProcHandler = HssAuthProcedureHandler(self.hssIoService, self.__hssAuthCompleteCallback__)
        self.hssIoService.addIncomingMessageCallback(hssAuthProcHandler.handleIncomingMessage)
        for _ in range(n):
            randomImsi = visitedPlmnId + "".join([str(random.randrange(0, 10)) for __ in range(10)])
            hssAuthProcHandler.knownIMSIs.append(randomImsi)
            mmeAuthProcHandler.execute(randomImsi, visitedPlmnId)
            time.sleep(0.1)
        time.sleep(1.0)
        self.assertEqual(self.mmeSuccessCount, n)
        self.assertEqual(self.hssSuccessCount, n)
        
    def test_roamingNotAllowedError(self):
        visitedPlmnId = "47836"
        imsi = "286031595270296"
        mmeAuthProcHandler = MmeAuthProcedureHandler((localhost(), 9000), self.mmeIoService, self.__mmeAuthCompleteCallback__)
        self.mmeIoService.addIncomingMessageCallback(mmeAuthProcHandler.handleIncomingMessage)
        hssAuthProcHandler = HssAuthProcedureHandler(self.hssIoService, self.__hssAuthCompleteCallback__)
        self.hssIoService.addIncomingMessageCallback(hssAuthProcHandler.handleIncomingMessage)
        mmeAuthProcHandler.execute(imsi, visitedPlmnId)
        self.assertEqual(self.mmeSuccessCount,0)
        
    def test_unknownImsiError(self):
        n = 10
        visitedPlmnId = "28603"
        imsi = "286056548201466"
        mmeAuthProcHandler = MmeAuthProcedureHandler((localhost(), 9000), self.mmeIoService, self.__mmeAuthCompleteCallback__)
        self.mmeIoService.addIncomingMessageCallback(mmeAuthProcHandler.handleIncomingMessage)
        hssAuthProcHandler = HssAuthProcedureHandler(self.hssIoService, self.__hssAuthCompleteCallback__)
        self.hssIoService.addIncomingMessageCallback(hssAuthProcHandler.handleIncomingMessage)
        for _ in range(n):
            randomImsi = visitedPlmnId + "".join([str(random.randrange(0, 10)) for __ in range(10)])
            hssAuthProcHandler.knownIMSIs.append(randomImsi)
        mmeAuthProcHandler.execute(imsi, visitedPlmnId)
        self.assertEqual(self.mmeSuccessCount,0)