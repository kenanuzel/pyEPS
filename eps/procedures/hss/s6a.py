from eps.messages.s6a import authenticationInformationAnswer


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
        if endToEndId in self.outstandingRequests:
            pass
        else:
            self.outstandingRequests[endToEndId] = {"imsi": message["imsi"], "visitedPlmnId": message["visitedPlmnId"]}
            if message["visitedPlmnId"] not in self.plmnList:
                self.procedureCompletionCallback(self.Failure, message["imsi"])
                self.ioService.sendMessage(source, *authenticationInformationAnswer(5004, [], endToEndId))
            elif message["imsi"] not in self.knownIMSIs:
                self.ioService.sendMessage(source, *authenticationInformationAnswer(5001, [], endToEndId))
                self.procedureCompletionCallback(self.Failure, message["imsi"])
            else:
                self.ioService.sendMessage(source, *authenticationInformationAnswer(2001, [], endToEndId))
                self.procedureCompletionCallback(self.Success, message["imsi"])