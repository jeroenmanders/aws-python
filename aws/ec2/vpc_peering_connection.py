from .ec2_base_object import Ec2BaseObject


class VpcPeeringConnection(Ec2BaseObject):
    packet_guid = "AWS-VPC-PEERING-CONNECTION"
    instances = {}

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.peering_connection_id = None
        self.status_code = None
        self.status_message = None
        self.is_requestor = None

        self.this_account_id = None
        self.this_vpc_id = None
        self.this_region = None
        self.this_cidr_block = None

        self.other_vpc_id = None
        self.other_cidr_block = None
        self.other_region = None
        self.other_account_id = None

        self.subnet_rules = {}

    def add_subnet_rule(self, subnet_id, inbound_port):
        if not subnet_id in self.subnet_rules:
            self.subnet_rules['subnet_id'] = []

        self.subnet_rules['subnet_id'].append(inbound_port)

    def retrieve_from_aws(self, reload=False, fail_if_not_found=True):
        if self.loaded_from_aws and not reload:
            self.logger.info("Vpc '{}' already loaded from AWS and reload is not True".format(self.vpc_name))

        response_json = self.get_client().describe_vpc_peering_connections(
            DryRun=False,
            Filters=[
                {'Name': "requester-vpc-info.vpc-id", 'Values': [self.this_vpc_id]},
                {'Name': "accepter-vpc-info.vpc-id", 'Values': [self.other_vpc_id]}
            ]
        )
        peering_connection_json = self.check_exactly_one_instance(json=response_json,
                                                                  collection_name='VpcPeeringConnections',
                                                                  label="VPC peering connection '{}'".format(self.name),
                                                                  fail_if_not_found=fail_if_not_found)

        if peering_connection_json:
            self.load_from_aws_response(peering_connection_json=peering_connection_json)
            return True
        else:
            return False

    def load_from_aws_response(self, peering_connection_json):
        if self.this_vpc_id == peering_connection_json['RequesterVpcInfo']['VpcId']:
            self.logger.info("This VPC is the requester")
            self.is_requestor = True
            this_info = peering_connection_json['RequesterVpcInfo']
            other_info = peering_connection_json['AccepterVpcInfo']
        else:
            self.logger.info("This VPC is the accepter")
            self.is_requestor = False
            this_info = peering_connection_json['AccepterVpcInfo']
            other_info = peering_connection_json['RequesterVpcInfo']

        print(peering_connection_json)
        self.peering_connection_id = peering_connection_json['VpcPeeringConnectionId']
        self.this_cidr_block = this_info['CidrBlock']
        self.this_account_id = this_info['OwnerId']
        self.this_region = this_info['Region']

        #self.other_cidr_block = other_info['CidrBlock']
        self.other_account_id = other_info['OwnerId']
        self.other_region = other_info['Region']
        self.other_vpc_id = other_info['VpcId']

        self.status_code = peering_connection_json['Status']['Code']
        self.status_message = peering_connection_json['Status']['Message']

        self.set_tags_json(tags_json=peering_connection_json['Tags'])

    def ensure(self):
        if self.retrieve_from_aws(reload=True, fail_if_not_found=False):
            self.logger.info("Peering connection found. Status: {} - {}".format(self.status_code, self.status_message))
        else:
            self.logger.info("No peering connection found. Creating it")
            response = self.get_client().create_vpc_peering_connection(
                DryRun=False,
                VpcId=self.this_vpc_id,
                PeerOwnerId=self.other_account_id,
                PeerVpcId=self.other_vpc_id,
                PeerRegion=self.other_region
            )

            peering_connection_json = response["VpcPeeringConnection"]
            print(peering_connection_json)
            self.load_from_aws_response(peering_connection_json)

        response = self.get_client().create_tags(
            DryRun=False,
            Resources=[ self.peering_connection_id ],
            Tags=[{ 'Key': 'Name', 'Value': self.name }]
        )

        if self.status_code == 'initiating-request':
            self.logger.info("Waiting for peering connection initiation to complete")
            waiter = self.get_client().get_waiter('vpc_peering_connection_exists')
            waiter.wait(VpcPeeringConnectionIds = [ self.peering_connection_id])


        self.logger.info("Checking peering connection status {} - {}".format(self.status_code, self.status_message))
        if self.status_code in ['active','pending-acceptance']:
            if not self.is_requestor and self.status_code == 'pending-acceptance':
                self.logger.info("Acception this peering request")
                response = self.get_client().accept_vpc_peering_connection(
                    DryRun=False,
                    VpcPeeringConnectionId = self.peering_connection_id
                )

            self.logger.info("Ready to configure routing and ACLs.")
            self.configure_routes()
        elif self.status_code in ['deleted', 'rejected', 'failed', 'expired']:
            raise Exception('This peering request is in an unsupported state')


    def configure_routes(self):
        #use         self.subnet_rules = {} here
        pass
        """
        route_tables = peering_stack_config.get('source_routes')
        for route_table_key, route_table_config in source_route_tables.iteritems():
            cidr_blocks = route_table_config.get('cidr_blocks')
            for cidr_block in cidr_blocks:
                self.create_route_vpc_to_vpc_peer(
                    vpc_id=peering_conn.requester_vpc_info['VpcId'],
                    target_vpc_cidr=cidr_block,
                    peering_conn_id=peering_conn.id,
                    route_table_ids=[route_table_config['route_table_id']]
                )
        """