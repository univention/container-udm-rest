#!/usr/bin/env python3

import os
import sys

import yaml
from jinja2 import Environment, Template, StrictUndefined

from univention.admin.rest.client import UDM


udm_api_url = os.environ["UDM_API_URL"]
udm_api_user = os.environ["UDM_API_USER"]
udm_api_password = os.environ["UDM_API_PASSWORD"]
udm = UDM.http(udm_api_url, udm_api_user, udm_api_password)

ldap_base = udm.get_ldap_base()


def main():
    input_filename = sys.argv[1]

    with open(input_filename, "r") as input_file:
        content = input_file.read()

    if is_template(input_filename):
        content = render_template(content)

    actions = list(yaml.safe_load_all(content))

    for action in actions:
        process_action(action)


def is_template(filename):
    return filename.endswith(".j2")


def render_template(content):
    template = Template(
        content,
        undefined=StrictUndefined)
    parameters = {
        "ldap_base": ldap_base,
    }
    return template.render(parameters)


def process_action(data):
    print(data)
    if data["action"] == "create":
        ensure_udm_object(
            module=data["module"],
            position=data["position"],
            properties=data["properties"],
        )


def ensure_udm_object(module, position, properties):
    print(f"Ensuring udm object {module}, {position}, {properties.get('name')}")
    module_obj = udm.get(module)
    obj = module_obj.new(position=position)
    obj.properties.update(properties)
    try:
        obj.save()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
