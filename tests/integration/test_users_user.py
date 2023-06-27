"""
Module providing integration tests for the UDM users/user objects.
"""
import random
import urllib.parse

# 3rd-party
import requests


def test_users_user_post(session: requests.Session, udm_url: str):
    url_users = urllib.parse.urljoin(udm_url, "users/user/")
    username = "test-{:08X}".format(random.getrandbits(2**5))

    conn = session.post(
        url_users,
        json={
            "properties": {
                "username": username,
                "lastname": "Smith",
                "password": "univention",
            },
        },
    )

    assert conn.status_code == requests.codes.created
    post_result = conn.json()
    new_dn = post_result["dn"]
    new_uuid = post_result["uuid"]

    conn = session.get(f"{url_users}{new_dn}")
    assert conn.status_code == requests.codes.ok
    object = conn.json()
    assert object["dn"] == new_dn
    assert object["uuid"] == new_uuid
    assert object["properties"]["lastname"] == "Smith"
    assert object["properties"]["username"] == username
