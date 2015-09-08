#!/usr/bin/python
#
# This is a free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This Ansible library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: ec2_vpc_facts
short_description: Gather facts about VPCs in AWS
description:
    - Gather facts about VPCs in AWS
version_added: "2.0"
author: "Mark Chance (@java1guy)"
options:
  vpc_id:
    description:
      - The ID of the VPC
    required: false
    default: null
extends_documentation_fragment: aws
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Gather facts about all VPCs
- ec2_vpc_facts:

# Gather facts about a particular VPC
- ec2_vpc_facts:
    vpc_id: vpc-xxxxxxx

# Gather facts about a particular subnet
- ec2_vpc_facts:
    options: subnets
    vpc_id: vpc-xxxxxxx

'''
try:
    import json
    import boto
    import botocore
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

def list_vpcs(ec2, vpc_id):
    try:
        args = dict()
        if vpc_id:
            args["VpcIds"] = [ vpc_id ]
        all_vpc = ec2.describe_vpcs(**args)
    except boto.exception.BotoServerError as e:
        module.fail_json(msg=str(e))
    return all_vpc


def list_subnets(ec2, vpc_id):
    try:
        all_vpc = ec2.describe_subnets( Filters=
        	[{ 'Name': "vpc-id", 'Values': [ vpc_id] } ])
    except boto.exception.BotoServerError as e:
        module.fail_json(msg=str(e))
    return all_vpc

# Could add any of the describe_* from https://boto3.readthedocs.org/en/latest/reference/services/ec2.html
def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            vpc_id=dict(required=False, type='str', default=None ),
            options=dict(required=False, choices=['vpcs', 'subnets'], default='vpcs' ),
        )
    )
    
    module = AnsibleModule(argument_spec=argument_spec)
    # Validate Requirements
    if not HAS_BOTO:
      module.fail_json(msg='boto is required.')

    if not HAS_BOTO3:
      module.fail_json(msg='boto3 is required.')

    try:
        # self.ecs = boto3.client('ecs')
        region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
        if not region:
            module.fail_json(msg="Region must be specified as a parameter, in EC2_REGION or AWS_REGION environment variables or in boto configuration file")
        ec2 = boto3_conn(module, conn_type='client', resource='ec2', region=region, endpoint=ec2_url, **aws_connect_kwargs)
    except boto.exception.NoAuthHandlerFound, e:
        self.module.fail_json(msg=str(e))
    
    results = dict()
    if module.params['options'] == 'vpcs':
        vpc_id = module.params.get("vpc_id") if "vpc_id" in module.params and module.params.get("vpc_id") is not None else None
        all_vpc = list_vpcs(ec2, vpc_id)
        results['vpcs'] = all_vpc["Vpcs"]
    if module.params['options'] == 'subnets':
        vpc_id = module.params.get("vpc_id") if "vpc_id" in module.params and module.params.get("vpc_id") is not None else None
        all_vpc = list_subnets(ec2, vpc_id)
        results['subnets'] = all_vpc["Subnets"]

    module.exit_json(**results)

from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

# this is magic, see lib/ansible/module_common.py
#<<INCLUDE_ANSIBLE_MODULE_COMMON>>

main()
