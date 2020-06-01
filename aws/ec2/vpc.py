from .ec2_base_object import Ec2BaseObject
from pprint import pprint


class Vpc(Ec2BaseObject):

    packet_guid = "AWS-VPC"
    instances = {}

    @staticmethod
    def get_instance(vpc_name):
        if not vpc_name in Vpc.instances:
            vpc = Vpc(vpc_name=vpc_name)
            Vpc.instances[vpc_name] = vpc

        return Vpc.instances[vpc_name]

    def __init__(self, vpc_name=None):
        super().__init__()
        self.vpc_name = vpc_name

    def retrieve_from_aws(self, reload=False, fail_if_not_found=True):
        if self.loaded_from_aws and not reload:
            self.logger.info("Vpc '{}' already loaded from AWS and reload is not True".format(self.vpc_name))

        json = self.get_client().describe_vpcs(Filters=[self.get_name_filter(name=self.vpc_name) ])
        vpc_json = self.check_exactly_one_instance(json=json,
                                                   collection_name='Vpcs',
                                                   label="VPC '{}'".format(self.vpc_name),
                                                   fail_if_not_found=fail_if_not_found)

        self.vpc_id = vpc_json['VpcId']
        self.cidr_block = vpc_json['CidrBlock']
        self.is_default = vpc_json['IsDefault']
        self.state = vpc_json['State']
        self.loaded_from_aws = True
