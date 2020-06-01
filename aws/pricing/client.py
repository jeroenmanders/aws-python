import boto3

# See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/pricing.html
#  and https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/reading-an-offer.html#pps-defs
class Client(object):

    _instance = None

    @staticmethod
    def get_instance():
        if Client._instance == None:
            Client._instance = Client()

        return Client._instance

    def __init__(self):
        self._client = boto3.client('pricing', region_name="us-east-1")

    def get_client(self):
        return self._client
