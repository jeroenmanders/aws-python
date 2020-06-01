import boto3

class Client(object):

    _instance = None

    @staticmethod
    def get_instance():
        if Client._instance == None:
            Client._instance = Client()

        return Client._instance

    def __init__(self):
        self._client = boto3.client('rds')

    def get_client(self):
        return self._client
