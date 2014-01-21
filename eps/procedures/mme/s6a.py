from eps.messages.s6a import authenticationInformationRequest


class AuthenticationInformationRetrievalProcedureHandler(object):

    Success, Failure = range(2)

    def __init__(self, hssAddress, ioService, responseTimeoutT3, procedureCompletionCallback):
        self.hssAddress = hssAddress
        self.ioService = ioService
        self.procedureCompletionCallback = procedureCompletionCallback
        self.nextEndToEndId = 0
        self.outstandingRequests = {}
        self.responseTimeoutT3 = responseTimeoutT3
        self.waitForResponseTimer = {}
        self.timeoutCounter = 0

    def execute(self, imsi, visitedPlmnId):
        self.waitForResponseTimer[self.nextEndToEndId] = self.ioService.createTimer(self.responseTimeoutT3,
                                                                           self.__onResponseTimeout__, self.nextEndToEndId)
        self.waitForResponseTimer[self.nextEndToEndId].start()
        self.ioService.sendMessage(self.hssAddress, *authenticationInformationRequest(imsi, visitedPlmnId, 
                                                                                      self.nextEndToEndId))
        self.outstandingRequests[self.nextEndToEndId] = {"imsi": imsi, "visitedPlmnId": visitedPlmnId}        
        self.nextEndToEndId += 1
        
    def __onResponseTimeout__(self, endToEndId):
            self.procedureCompletionCallback(self.Failure)
            del self.outstandingRequests[endToEndId]
            self.timeoutCounter += 1

    def handleIncomingMessage(self, source, interface, channelInfo, message):
        endToEndId = channelInfo["endToEndId"]
        self.waitForResponseTimer[endToEndId].cancel()
        if endToEndId in self.outstandingRequests:
            authContext = self.outstandingRequests[endToEndId]
            if message["resultCode"] == 2001:
                authContext["authenticationInfo"] = message["authenticationInfo"]
                self.procedureCompletionCallback(self.Success, authContext)
            else:
                self.procedureCompletionCallback(self.Failure)
            del self.outstandingRequests[endToEndId]
        