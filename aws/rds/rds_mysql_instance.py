from .rds_base_object import RdsBaseObject


class RdsMySqlInstance(RdsBaseObject):
    packet_guid = "AWS-RDS-MYSQL"
    instances = {}

    @staticmethod
    def get_instance(vpc, rds_name):
        if not rds_name in RdsMySqlInstance.instances:
            rds = RdsMySqlInstance(rds_name=rds_name)
            RdsMySqlInstance.instances[rds_name] = rds

        rds = RdsMySqlInstance.instances[rds_name]
        rds.vpc = vpc
        return rds

    def __init__(self, rds_name=None):
        super().__init__()
        self.rds_name = rds_name
        self.vpc = None
        self.dns_name = None
        self.canonical_hosted_zone_name_id = None
