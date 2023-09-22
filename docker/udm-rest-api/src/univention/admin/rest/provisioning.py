import json
import os
import urllib.parse
import urllib.request

from concurrent.futures import ThreadPoolExecutor
from ldap.controls.readentry import PostReadControl, PreReadControl
from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPRequest
import tornado.gen

from univention.admin.rest.object import get_representation
import univention.admin.uldap
from univention.management.console.log import MODULE
from univention.management.console.modules.udm.udm_ldap import UDM_Module


class accessWithProvisioning(univention.admin.uldap.access):

    # Thread pool for submitting to the provisioning service.
    pool = ThreadPoolExecutor(max_workers=1)

    def _get_module(self, object_type):
        module = UDM_Module(object_type, ldap_connection=self, ldap_position=None)
        if not module or not module.module:
            raise ModuleNotFound
        return module

    @tornado.gen.coroutine
    def send_to_provisioning(self, items):
        base_url = os.getenv("PROVISIONING_URL", "http://host.docker.internal:7777")
        realm = os.getenv("PROVISIONING_REALM", "udm")
        if not base_url:
            return

        url = urllib.parse.urljoin(base_url, "/v1/message/")
        MODULE.debug(f"Sending to provisioning dispatcher at {url}")

        for topic, old_object, new_object in items:
            data = {
                "realm": realm,
                "topic": topic,
                "body": {
                    "old": old_object,
                    "new": new_object,
                }
            }

            request = HTTPRequest(url=url, method="POST",
                              body=json.dumps(data).encode("utf-8"),
                              headers={"content-type", "application/json"})
            try:
                client = AsyncHTTPClient()
                response = yield client.fetch(request, raise_error=True)
                MODULE.info(f"Message sent to provisioning service (response: {response.status}, {response.reason}).")
            except HTTPError as err:
                MODULE.error(f"Could not send to provisioning service: {err}")
            except Exception as ex:
                MODULE.error(f"Could not send to provisioning service: {ex}")

    def _handle_control_responses(self, responses):
        def _get_control(response, ctrl_type):
            for control in response.get('ctrls', []):
                if control.controlType == ctrl_type:
                    return control

        def _ldap_to_udm(raw):
            if raw is None:
                return None

            object_types = raw.entry.get("univentionObjectType", [])
            if not isinstance(object_types, list) or len(object_types) < 1:
                MODULE.warn("ReadControl response is missing `univentionObjectType`!")
                return None

            try:
                object_type = object_types[0].decode('utf-8')
                module = self._get_module(object_type)
                obj = module.module.object(co=None, lo=self,
                                           position=None, dn=raw.dn,
                                           superordinate=None,
                                           attributes=raw.entry)
                obj.open()
                return get_representation(module, obj, ['*'], self, False)
            except ModuleNotFound:
                MODULE.error("ReadControl response has object type %r, but the module was not found!" % object_type)
                return None

        if isinstance(responses, dict):
            responses = [responses]

        publish = []
        for response in responses:
            # extract control response and rebuild UDM representation
            topic = "n/a"
            pre = _ldap_to_udm(_get_control(response, PreReadControl.controlType))
            post = _ldap_to_udm(_get_control(response, PostReadControl.controlType))

            if pre:
                topic = pre["objectType"]
                MODULE.debug("UDM before change")
                for key, value in sorted(pre.items(), key = lambda i: i[0]):
                    MODULE.debug(f"  {key}: {value}")
            if post:
                topic = post["objectType"]
                MODULE.debug("UDM after change")
                for key, value in sorted(post.items(), key = lambda i: i[0]):
                    MODULE.debug(f"  {key}: {value}")

            if pre or post:
                publish.append((topic, pre, post))
            else:
                MODULE.debug("No control responses for UDM objects were returned.")

        if publish:
            # Collect all events into a list and publish that from inside *one* future,
            # thus ensuring that all events are published in the order as they occurred.

            tornado.ioloop.IOLoop.current().add_future(
                self.send_to_provisioning(publish),
                callback=lambda _future: None)

    def _extract_responses(self, func, response_name, *args, **kwargs):
        # Note: the original call must not pass `serverctrls` and/or `response` via `args`!

        # either re-use the given response dict, or provide our own
        if response_name not in kwargs:
            kwargs[response_name] = [] if response_name == "responses" else {}
        ctrl_response = kwargs.get(response_name)

        kwargs["serverctrls"] = [
            # strip the caller's Pre-/PostReadControls from the `serverctrls`
            control for control in kwargs.get("serverctrls", [])
            if control.controlType not in [ PreReadControl.controlType, PostReadControl.controlType ]
        ] + [
            # always add our all-inclusive Pre-/PostReadControls
            PreReadControl(False, ['*', '+']),
            PostReadControl(False, ['*', '+'])
        ]

        response = func(*args, **kwargs)
        self._handle_control_responses(ctrl_response)
        return response

    def add(self, *args, **kwargs):
        return self._extract_responses(super().add, "response", *args, **kwargs)

    def modify(self, *args, **kwargs):
        # If the DN and properties of the object are changed, this calls
        # ldap.rename_ext_s and ldap.modify_ext_s, yielding two responses.
        return self._extract_responses(super().modify, "responses", *args, **kwargs)

    def rename(self, *args, **kwargs):
        return self._extract_responses(super().rename, "response", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._extract_responses(super().delete, "response", *args, **kwargs)


class ModuleNotFound(Exception):
    pass
