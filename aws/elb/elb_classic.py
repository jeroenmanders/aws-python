from .lb_base_object import LbBaseObject
from pprint import pprint


class ElbClassic(LbBaseObject):

    packet_guid = "AWS-ELB-CLASSIC"
    instances = {}

    @staticmethod
    def get_instance(vpc, elb_name):
        if not elb_name in ElbClassic.instances:
            elb = ElbClassic(elb_name=elb_name)
            ElbClassic.instances[elb_name] = elb

        elb = ElbClassic.instances[elb_name]
        elb.vpc = vpc
        return elb

    def __init__(self, elb_name=None):
        super().__init__()
        self.elb_name = elb_name
        self.vpc = None
        self.dns_name = None
        self.canonical_hosted_zone_name_id = None

    def retrieve_from_aws(self, reload=False, fail_if_not_found=True, use_tag_name=None):
        assert self.elb_name
        if self.loaded_from_aws and not reload:
            self.logger.info("Classic ELB '{}' already loaded from AWS and reload is not True".format(self.elb_name))

        if use_tag_name:
            load_balancer_names = []
            load_balancers_by_name = {}
            elb_json = None
            json = self.get_client_v1().describe_load_balancers()
            for elb_json in json['LoadBalancerDescriptions']:
                if elb_json['VPCId'] == self.vpc.vpc_id:
                    load_balancer_names.append(elb_json['LoadBalancerName'])
                    load_balancers_by_name[elb_json['LoadBalancerName']] = elb_json

            if len(load_balancer_names) > 0:
                self.logger.info("{} load balancers found in VPC. Retrieving tags.".format(len(load_balancer_names)))
                tags_response = self.get_client_v1().describe_tags(LoadBalancerNames=load_balancer_names)
                for result in tags_response['TagDescriptions']:
                    for tag in result['Tags']:
                        if tag['Key'] == "Name":
                            if tag['Value'] == self.elb_name:
                                elb_json = load_balancers_by_name[result['LoadBalancerName']]
                                break

                    if elb_json:
                        break

            if not elb_json:
                self.logger.fatal("Load balancer with tag '{}'='{}' not found in VPC '{}'"
                                  .format("Name", self.elb_name, self.vpc.vpc_id))
        else:
            json = self.get_client_v1().describe_load_balancers(LoadBalancerNames=[self.elb_name])

            elb_json = self.check_exactly_one_instance(json=json,
                                                       collection_name='LoadBalancerDescriptions',
                                                       label="Classic ELB '{}'".format(self.elb_name),
                                                       fail_if_not_found=fail_if_not_found)

        self.dns_name = elb_json['DNSName']
        self.aws_name = elb_json['LoadBalancerName']
        self.canonical_hosted_zone_name_id = elb_json['CanonicalHostedZoneNameID']
        self.loaded_from_aws = True