from .record_set import RecordSet
from pprint import pprint


class AliasRecordset(RecordSet):

    packet_guid = "AWS-ROUTE53-ALIAS-RECORD-SET"

    def __init__(self, hostname, alias_target_object, ttl=300, hosted_zone=None,
                 zone_name=None, vpc_id=None):

        assert hasattr(alias_target_object, "canonical_hosted_zone_name_id")
        assert hasattr(alias_target_object, "dns_name")

        super().__init__(hostname=hostname, record_type="A", ttl=ttl, hosted_zone=hosted_zone, zone_name=zone_name,
                         vpc_id=vpc_id)

        self.alias_target_object = alias_target_object
        self.alias_target_zone_id = alias_target_object.canonical_hosted_zone_name_id
        self.alias_target_dns_name = alias_target_object.dns_name
        self.dualstack_dns_name = "dualstack.{}".format(self.alias_target_dns_name)

    def delete(self):
        self.retrieve_from_aws()
        if not self.aws_record_set_json:
            self.logger.warn("Dns entry not found. Aborting delete")
            return

        self.logger.warn("Deleting dns entry. Original record:")
        pprint(self.aws_record_set_json)

        response = self.get_client().change_resource_record_sets(
            HostedZoneId=self.hosted_zone.zone_id,
            ChangeBatch={
                'Comment': 'Infraxys - Delete ELB dns entry',
                'Changes': [
                    {
                        'Action': 'DELETE',
                        'ResourceRecordSet': {
                            'Name': self.full_hostname_with_dot,
                            'Type': 'A',
                            'AliasTarget': {
                                'HostedZoneId': self.alias_target_zone_id,
                                'DNSName': self.dualstack_dns_name,
                                'EvaluateTargetHealth': False
                            }
                        }
                    },
                ]
            }
        )

    def ensure(self):
        self.retrieve_from_aws()
        if self.aws_record_set_json:
            self.logger.warn("Record will be updated. Original record:")
            pprint(self.aws_record_set_json)

        if not self.alias_target_zone_id:
            self.logger.info("No target zone specified for the alias, so using the same one.")
            self.alias_target_zone_id = self.hosted_zone.zone_id

        self.logger.info("Ensuring A-record alias {} points to {}"
                         .format(self.full_hostname_with_dot, self.dualstack_dns_name))

        response = self.get_client().change_resource_record_sets(
            HostedZoneId=self.hosted_zone.zone_id,
            ChangeBatch={
                'Comment': 'Infraxys - Create/Update ELB dns entry',
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': self.full_hostname_with_dot,
                            'Type': 'A',
                            'AliasTarget': {
                                'HostedZoneId': self.alias_target_zone_id,
                                'DNSName': self.dualstack_dns_name,
                                'EvaluateTargetHealth': False
                            }
                        }
                    },
                ]
            }
        )