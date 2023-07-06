import os
import sys

import yaml

from typing import Dict, List

from univention.admin.rest.client import UDM

udm_api_url = os.environ["UDM_API_URL"]
udm_api_user = os.environ["UDM_API_USER"]
udm_api_password = os.environ["UDM_API_PASSWORD"]
# udm_api_url = "http://localhost:9979/udm/"
# udm_api_user = "Administrator"
# udm_api_password = "univention"
udm = UDM.http(udm_api_url, udm_api_user, udm_api_password)

ldap_base = udm.get_ldap_base()

with open(sys.argv[1], "r") as input_file:
    actions = list(yaml.safe_load_all(input_file))


def main(actions):
    for action in actions:
        process_action(action)


def recursively_format_properties(data, **kwargs):
    if isinstance(data, dict):
        return {key: recursively_format_properties(value, **kwargs) for key, value in data.items()}
    elif isinstance(data, list):
        return [recursively_format_properties(item, **kwargs) for item in data]
    elif isinstance(data, str):
        return data.format(**kwargs)
    else:
        return data


def process_action(data):
    if data["action"] == "create":
        module = data["module"]
        position = f'{data["position"]}{ldap_base}'
        properties = recursively_format_properties(data["properties"], ldap_base=ldap_base)

        ensure_udm_object(module, position, properties)


def ensure_udm_object(module, position, properties):
    print(f"Ensuring udm object {module}, {position}, {properties.get('name')}")
    module_obj = udm.get(module)
    obj = module_obj.new(position=position)
    obj.properties.update(properties)
    try:
        obj.save()
    except Exception as e:
        if 'Object exists' not in e.error_details['message']:
            breakpoint()
            print(e)


if __name__ == "__main__":
    main(actions)
