from .client import Client
from aws.aws_base_object import AwsBaseObject


class LbBaseObject(AwsBaseObject):

    @staticmethod
    def get_client_v1(): # Classic load balancers
        return Client.get_instance().get_client_v1()

    @staticmethod
    def get_client_v2(): # Application and Network load balancers
        return Client.get_instance().get_client_v2()