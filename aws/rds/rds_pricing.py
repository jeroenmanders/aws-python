import json

from .rds_base_object import RdsBaseObject
from ..pricing.client import Client as PricingClient


# aws pricing get-attribute-values --service-code AmazonRDS --attribute-name instanceFamily

class RdsPricing(RdsBaseObject):
    packet_guid = ""
    instance = None
    price_cache = {}

    @staticmethod
    def get_instance():
        if not RdsPricing.instance:
            RdsPricing.instance = RdsPricing()

        return RdsPricing.instance

    def __init__(self):
        super().__init__()
        self.price_on_demand_per_hour = None

    def get_rds_price(self, instance_type, db_engine, multi_az=False):
        assert instance_type and db_engine
        multi_az_string = "Multi-AZ" if multi_az else "Single-AZ"
        location = "US East (N. Virginia)"
        cache_key = "{}.{}.{}.{}".format(instance_type, multi_az_string, location, db_engine)
        if cache_key in RdsPricing.price_cache:
            self.price_on_demand_per_hour = RdsPricing.price_cache[cache_key]
            return True

        self.logger.debug(
            "Retrieving RDS pricing for {} '{}' {} {}".format(instance_type, multi_az_string, location, db_engine))

        response = PricingClient.get_instance().get_client().get_products(
            ServiceCode='AmazonRDS',
            Filters=[
                {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
                {'Type': 'TERM_MATCH', 'Field': 'deploymentOption', 'Value': multi_az_string},
                {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': location},
                {'Type': 'TERM_MATCH', 'Field': 'databaseEngine', 'Value': db_engine}
            ],
            MaxResults=100
        )

        price_list = response['PriceList']
        if len(response['PriceList']) == 0:
            return False, "No price could be loaded"
        elif len(response['PriceList']) > 1:
            return False, "Multiple prices loaded"

        price_item = json.loads(price_list[0])
        terms = price_item["terms"]
        attribute_name = list(terms["OnDemand"])[0]
        term = terms["OnDemand"][attribute_name]

        attribute_name = list(term["priceDimensions"])[0]
        price_dimension = term["priceDimensions"][attribute_name]
        self.price_on_demand_per_hour = price_dimension['pricePerUnit']["USD"]
        RdsPricing.price_cache[cache_key] = self.price_on_demand_per_hour
        return True
