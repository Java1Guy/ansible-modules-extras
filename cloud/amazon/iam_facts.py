#!/usr/bin/python
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: ecs_service_facts
short_description: list or describe services in ecs
description:
    - Lists or describes services in ecs.
version_added: "0.9"
options:
    details:
        description:
            - Set this to true if you want detailed information about the services.
        required: false
        default: 'false'
        choices: ['true', 'false']
        version_added: 1.9
    cluster:
        description:
            - The cluster ARNS in which to list the services.
        required: false
        default: 'default'
        version_added: 1.9
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Basic listing example
- ecs_task:
    cluster=test-cluster
    task_list=123456789012345678901234567890123456

# Basic example of deregistering task
- ecs_task:
    state: absent
    family: console-test-tdn
    revision: 1
'''

try:
    import json, os
    import boto
    import botocore
    # import module snippets
    from ansible.module_utils.basic import *
    from ansible.module_utils.ec2 import *
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

try:
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

def main():

    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        details={'required': False, 'choices': ['true', 'false'] },
        name={'required': False, 'type': 'str'}
    ))

    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)

    if not HAS_BOTO:
      module.fail_json(msg='boto is required.')

    if not HAS_BOTO3:
      module.fail_json(msg='boto3 is required.')

    region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)

    # ecs = boto3_conn(module, conn_type='client', resource='ecs', region=region, endpoint=ec2_url, **aws_connect_kwargs)

    ec2_url, access_key, secret_key, region = get_ec2_creds(module)
    aws_connect_params = dict(aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key)

    if not region:
        module.fail_json(msg="Region must be specified as a parameter, in EC2_REGION or AWS_REGION environment variables or in boto configuration file")

    show_details = False
    if 'details' in module.params and module.params['details'] == 'true':
        show_details = True

    try:
        iam = boto3.client('iam')
    except boto.exception.NoAuthHandlerFound, e:
        module.fail_json(msg=str(e))

    if show_details:
        # if 'service' not in module.params or not module.params['service']:
        #     module.fail_json(msg="service must be specified for ecs_service_facts")
        all_roles = iam.list_roles()
        for role in all_roles['Roles']:
            if role['RoleName'] == module.params['name']:
                ecs_facts = dict(Roles=[ role ])
                break
            ecs_facts = dict(Roles=[])
    else:
        ecs_facts = iam.list_roles()
    for role in ecs_facts['Roles']:
        del role['CreateDate']

    ecs_facts_result = dict(changed=False, roles=ecs_facts['Roles'])
    module.exit_json(**ecs_facts_result)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

if __name__ == '__main__':
    main()
