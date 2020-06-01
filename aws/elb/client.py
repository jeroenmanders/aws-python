import boto3


class Client(object):

    _instance = None

    @staticmethod
    def get_instance():
        if Client._instance == None:
            Client._instance = Client()

        return Client._instance

    def __init__(self):
        self._client_v1 = None
        self._client_v2 = None

    def get_client_v1(self):
        if not self._client_v1:
            self._client_v1 = boto3.client('elb', region_name="us-east-1")

        return self._client_v1

    def get_client_v2(self):
        if not self._client_v2:
            self._client_v2 = boto3.client('elbv2', region_name="us-east-1")

        return self._client_v2
