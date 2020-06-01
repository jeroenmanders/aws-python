from .client import Client
from aws.aws_base_object import AwsBaseObject


class Ec2BaseObject(AwsBaseObject):

    def __init__(self):
        super().__init__()
        self.session = None
        self._client = None

    def get_client(self):
        if not self._client:
            self._client = self.session.client('ec2')

        return self._client
