#!/usr/bin/env python3

import logging
import os
import sys

import yaml
from jinja2 import Template, StrictUndefined

from univention.admin.rest.client import UDM


log = logging.getLogger("app")


class App:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)

        udm_api_url = os.environ["UDM_API_URL"]
        log.info("Connecting to UDM API at URL %s", udm_api_url)
        udm_api_user = os.environ["UDM_API_USER"]
        udm_api_password = os.environ["UDM_API_PASSWORD"]
        self.udm = UDM.http(udm_api_url, udm_api_user, udm_api_password)

    def run(self):
        input_filename = sys.argv[1]
        log.info("Processing file %s", input_filename)

        with open(input_filename, "r") as input_file:
            content = input_file.read()

        if is_template(input_filename):
            log.info("Rendering file as Jinja2 template")
            context = {
                "ldap_base": self.udm.get_ldap_base(),
            }
            content = render_template(content, context)

        actions = list(yaml.safe_load_all(content))

        for action in actions:
            self.process_action(action)

    def process_action(self, data):
        if data["action"] == "create":
            self.ensure_udm_object(
                module=data["module"],
                position=data["position"],
                properties=data["properties"],
            )
        else:
            raise NotImplementedError(f"Action {data['action']} not supported.")

    def ensure_udm_object(self, module, position, properties):
        log.info(f"Ensuring udm object {module}, {position}, {properties.get('name')}")
        module_obj = self.udm.get(module)
        obj = module_obj.new(position=position)
        obj.properties.update(properties)
        try:
            obj.save()
        except Exception:
            log.exception("Exception while trying to save the object")


def is_template(filename):
    return filename.endswith(".j2")


def render_template(content, context):
    template = Template(content, undefined=StrictUndefined)
    return template.render(context)


if __name__ == "__main__":
    app = App()
    app.run()
