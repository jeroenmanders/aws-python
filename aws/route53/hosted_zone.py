from .route53_base_object import Route53BaseObject
from pprint import pprint


class HostedZone(Route53BaseObject):

    packet_guid = "AWS-ROUTE53-HOSTED-ZONE"

    def __init__(self, zone_name=None, zone_id=None, vpc_id=None):
        assert zone_name or zone_id
        super().__init__()
        self.zone_name = zone_name
        if zone_name.endswith("."):
            self.zone_name_with_dot = zone_name
        else:
            self.zone_name_with_dot = "{}.".format(zone_name)
            
        self.zone_id = zone_id
        self.vpc_id = vpc_id
        self.private_zone = None

    def retrieve_from_aws(self, reload=False, fail_if_not_found=True):
        if self.loaded_from_aws and not reload:
            self.logger.info("Hosted zone '{}' already loaded from AWS and reload is not True".format(self.vpc_name))

        aws_zone_result = None
        if self.zone_id:
            self.logger.info("Retrieving hosted zone with id {}".format(self.zone_id))
            aws_zone_result = Route53BaseObject.get_client().get_hosted_zone(Id=id)
            if fail_if_not_found and not hosted_zone:
                self.logger.fatal("Hosted zone with id '{}' not found.".format(self.zone_id))
        else:
            
            self.logger.info("Retrieving hosted zone with name {}".format(self.zone_name_with_dot))
            hosted_zones = Route53BaseObject.get_client().list_hosted_zones_by_name(DNSName=self.zone_name_with_dot)
            if hosted_zones['IsTruncated']:
                self.logger.fatal("There are more hosted zone results then retrieved in one batch, but paging is not enabled.")

            for hosted_zone in hosted_zones['HostedZones']:
                hosted_zone_name = hosted_zone['Name']
                hosted_zone_id = hosted_zone['Id']
                is_private = hosted_zone['Config']['PrivateZone']

                if self.vpc_id: # we're looking for a private zone
                    if is_private and hosted_zone_name == self.zone_name_with_dot:
                        self.logger.info("Retrieving details of zone {}".format(hosted_zone_id))
                        zone_details = Route53BaseObject.get_client().get_hosted_zone(hosted_zone_id)
                        for zone_vpc in zone_details['GetHostedZoneResponse']['VPCs']:
                            pprint(zone_vpc)
                            if zone_vpc['VPCId'] == self.vpc_id:
                                aws_zone_result = hosted_zone_name
                                break

                        if aws_zone_result:
                            break
                else:
                    if not is_private and hosted_zone_name == self.zone_name_with_dot:
                        aws_zone_result = hosted_zone
                        break

            if fail_if_not_found and not aws_zone_result:
                self.logger.fatal("Hosted zone with name '{}' not found.".format(self.zone_name_with_dot))

        self.zone_id = aws_zone_result['Id']
        self.name = aws_zone_result['Name']
        self.private_zone = aws_zone_result['Config']['PrivateZone']
        return True
