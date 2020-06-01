import os
from .lb_base_object import LbBaseObject
from aws.route53.alias_record_set import AliasRecordset
from pprint import pprint


class Alb(LbBaseObject):

    packet_guid = "AWS-APPLICATION-LOAD-BALANCER"
    instances = {}

    @staticmethod
    def get_instance(vpc, load_balancer_name):
        if not load_balancer_name in ElbClassic.instances:
            alb = Alb(load_balancer_name=load_balancer_name)
            Alb.instances[load_balancer_name] = alb

        alb = Alb.instances[load_balancer_name]
        alb.vpc = vpc
        return alb

    def __init__(self, load_balancer_name=None, alb_hostname=None):
        super().__init__()
        self.load_balancer_name = load_balancer_name
        self.alb_hostname = alb_hostname
        self.vpc = None
        self.dns_name = None
        self.canonical_hosted_zone_name_id = None
        self.route53_zone_name = os.getenv("route53_zone_name")

    def retrieve_from_aws(self, reload=False, fail_if_not_found=True, use_tag_name=None):
        assert self.load_balancer_name
        if self.loaded_from_aws and not reload:
            self.logger.info("Application load balancer '{}' already loaded from AWS and reload is not True".format(self.load_balancer_name))

        if use_tag_name:
            load_balancer_names = []
            load_balancers_by_name = {}
            alb_json = None
            json = Alb.get_client_v2().describe_load_balancers()
            for alb_json in json['LoadBalancers']:
                if alb_json['VpcId'] == self.vpc.vpc_id:
                    load_balancer_names.append(alb_json['LoadBalancerName'])
                    load_balancers_by_name[alb_json['LoadBalancerName']] = alb_json

            if len(load_balancer_names) > 0:
                self.logger.info("{} load balancers found in VPC. Retrieving tags.".format(len(load_balancer_names)))
                tags_response = Alb.get_client_v2().describe_tags(LoadBalancerNames=load_balancer_names)
                for result in tags_response['TagDescriptions']:
                    for tag in result['Tags']:
                        if tag['Key'] == "Name":
                            if tag['Value'] == self.load_balancer_name:
                                alb_json = load_balancers_by_name[result['LoadBalancerName']]
                                break

                    if alb_json:
                        break

            if not alb_json:
                self.logger.fatal("Load balancer with tag '{}'='{}' not found in VPC '{}'"
                                  .format("Name", self.load_balancer_name, self.vpc.vpc_id))
        else:
            json = Alb.get_client_v2().describe_load_balancers(Names=[ self.load_balancer_name ])
            alb_json = self.check_exactly_one_instance(json=json,
                                                       collection_name='LoadBalancers',
                                                       label="Application Load Balancer '{}'".format(self.load_balancer_name),
                                                       fail_if_not_found=fail_if_not_found)

        self.dns_name = alb_json['DNSName']
        self.aws_name = alb_json['LoadBalancerName']
        self.arn = alb_json['LoadBalancerArn']
        self.type = alb_json['Type']
        self.canonical_hosted_zone_name_id = alb_json['CanonicalHostedZoneId']
        self.loaded_from_aws = True

    def ensure_dns(self):
        assert self.alb_hostname
        assert self.dns_name
        assert self.canonical_hosted_zone_name_id
        assert self.route53_zone_name

        record_set = AliasRecordset(hostname=self.alb_hostname, zone_name=self.route53_zone_name,
                                    alias_target_object=self)
        record_set.ensure()
        return record_set

    def delete_dns(self):
        assert self.alb_hostname
        assert self.route53_zone_name
        record_set = AliasRecordset(hostname=self.alb_hostname, zone_name=self.route53_zone_name,
                                    alias_target_object=self)
        record_set.delete()
