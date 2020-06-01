import boto3


class Client(object):

    def __init__(self, session):
        self._client = session.client('ec2')

    def get_client(self):
        return self._client
