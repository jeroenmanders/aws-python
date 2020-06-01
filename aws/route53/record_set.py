from .route53_base_object import Route53BaseObject
from .hosted_zone import HostedZone
from pprint import pprint


class RecordSet(Route53BaseObject):
    
    def __init__(self, hostname, record_type, ttl=300, hosted_zone=None, zone_name=None, vpc_id=None):
        assert hosted_zone or zone_name
        super().__init__()
        self.hostname = hostname
        if hostname.endswith("."):
            self.hostname_with_dot = hostname
        else:
            self.hostname_with_dot = "{}.".format(hostname)

        self.record_type = record_type
        self.ttl = ttl
        self.hosted_zone = hosted_zone
        self.zone_name = zone_name
        self.vpc_id = vpc_id
        self.aws_record_set_json = None
        if hosted_zone:
            self.full_hostname_with_dot = "{}{}".format(self.hostname_with_dot, self.hosted_zone.zone_name_with_dot)
        else:
            if zone_name.endswith("."):
                zone_name_with_dot = zone_name
            else:
                zone_name_with_dot = "{}.".format(zone_name)

            self.full_hostname_with_dot = "{}{}".format(self.hostname_with_dot, zone_name_with_dot)

    def retrieve_from_aws(self, reload=False):
        if self.loaded_from_aws and not reload:
            self.logger.info("Route53 record set '{}' already loaded from AWS and reload is not True"
                             .format(self.hostname))

        if not self.hosted_zone:
            self.hosted_zone = HostedZone(zone_name=self.zone_name)
            self.hosted_zone.retrieve_from_aws()

        if self.vpc_id:
            raise NotImplementedError("Private resource record sets are not supported yet.")
        else:
            paginator = self.get_client().get_paginator('list_resource_record_sets')
            page_iterator = paginator.paginate(HostedZoneId=self.hosted_zone.zone_id)

            for page in page_iterator:
                for record_set in page['ResourceRecordSets']:
                    if record_set['Name'] == self.full_hostname_with_dot:
                        if record_set['Type'] == self.record_type:
                            self.logger.info("Found!")
                            self.aws_record_set_json = record_set
                        else:
                            self.logger.fatal("Route53 record {} found, but it's type '{}' is different from '{}'"
                                              .format(self.full_hostname_with_dot, record_set['Type'], self.record_type))

        self.loaded_from_aws = True
