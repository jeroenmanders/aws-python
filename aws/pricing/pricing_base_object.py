from .client import Client
from aws.aws_base_object import AwsBaseObject


class PricingBaseObject(AwsBaseObject):

    @staticmethod
    def get_client():
        return Client.get_instance().get_client()
