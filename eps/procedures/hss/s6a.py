from eps.messages.s6a import authenticationInformationAnswer
import time

class AuthenticationInformationRetrievalProcedureHandler(object):

    Success, Failure = range(2)

    def __init__(self, ioService, procedureCompletionCallback):
        self.ioService = ioService
        self.procedureCompletionCallback = procedureCompletionCallback
        self.nextEndToEndId = 0
        self.outstandingRequests = {}
        self.plmnList = ["28603"]
        self.knownIMSIs = []

    def handleIncomingMessage(self, source, interface, channelInfo, message):
        endToEndId = channelInfo["endToEndId"]
        time.sleep(0.1)
        self.outstandingRequests[endToEndId] = {"imsi": message["imsi"], "visitedPlmnId": message["visitedPlmnId"]}
        if message["visitedPlmnId"] not in self.plmnList:
            self.ioService.sendMessage(source, *authenticationInformationAnswer(5004, [], endToEndId))
            self.procedureCompletionCallback(self.Failure, message["imsi"])
        elif message["imsi"] not in self.knownIMSIs:
            self.ioService.sendMessage(source, *authenticationInformationAnswer(5001, [], endToEndId))
            self.procedureCompletionCallback(self.Failure, message["imsi"])
        else:
            self.ioService.sendMessage(source, *authenticationInformationAnswer(2001, [], endToEndId))
            self.procedureCompletionCallback(self.Success, message["imsi"])
        del self.outstandingRequests[endToEndId]
