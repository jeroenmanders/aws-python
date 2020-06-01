from .ec2_base_object import Ec2BaseObject
from ..pricing.client import Client as PricingClient
from pprint import pprint

#aws pricing get-attribute-values --service-code AmazonRDS --attribute-name instanceFamily

class Ec2Pricing(Ec2BaseObject):

    packet_guid = ""
    instance = None

    @staticmethod
    def get_instance():
        if not Ec2Pricing.instance:
            Ec2Pricing.instance = Ec2Pricing()

        return Ec2Pricing.instance

    def __init__(self):
        super().__init__()

    def get_ec2_price(self): #, tenancy, operatingSystem, preInstalledSw, instanceType, location):
        response = PricingClient.get_instance().get_client().get_products(
            ServiceCode='AmazonEC2',
            Filters = [
                {'Type' :'TERM_MATCH', 'Field':'operatingSystem', 'Value':'Windows'              },
                {'Type' :'TERM_MATCH', 'Field':'vcpu',            'Value':'64'                   },
                {'Type' :'TERM_MATCH', 'Field':'memory',          'Value':'256 GiB'              },
                {'Type' :'TERM_MATCH', 'Field':'preInstalledSw',  'Value':'SQL Ent'              },
                {'Type' :'TERM_MATCH', 'Field':'location',        'Value':'Asia Pacific (Mumbai)'}
            ],
            MaxResults=100
        )

        for price in response['PriceList']:
            pp = pprint.PrettyPrinter(indent=1, width=300)
            pp.pprint(json.loads(price))
            print()
