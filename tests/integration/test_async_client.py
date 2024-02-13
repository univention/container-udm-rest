# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import random

import pytest

from univention.admin.rest.async_client import (
    UDM,
    NotFound,
    PatchDocument,
    UnprocessableEntity,
    _NoRelation,
)


def random_string():
    return "test-{:08X}".format(random.getrandbits(2**5))


@pytest.mark.asyncio()
async def test_create_modify_move_remove(random_string, ucr):
    uri = "http://localhost/univention/udm/"
    async with UDM.http(uri, "Administrator", "univention") as udm:
        module = await udm.get("users/user")
        cn = await udm.get("container/cn")
        obj = await module.new()
        obj.properties["username"] = username = random_string()
        obj.properties["lastname"] = lastname = random_string()
        obj.properties["firstname"] = firstname = random_string()
        obj.properties["description"] = description = random_string()
        with pytest.raises(UnprocessableEntity):
            await obj.save()
        obj.properties["password"] = random_string()
        await obj.save()

        obj = await module.get(obj.dn)

        assert obj.properties["username"] == username
        assert obj.properties["lastname"] == lastname
        assert obj.properties["firstname"] == firstname
        assert obj.properties["description"] == description

        async for obj2 in module.search(filter="username=%s" % obj.properties["username"], opened=False):
            assert obj2.dn == obj.dn
        async for obj2 in module.search(filter="username=%s" % obj.properties["username"], opened=True):
            assert obj2.dn == obj.dn

        assert isinstance(obj.options, dict)
        assert isinstance(obj.policies, dict)
        assert isinstance(obj.position, str)
        assert isinstance(obj.uri, str)
        assert obj.superordinate is None

        assert isinstance(await obj.generate_service_specific_password("radius"), str)
        obj.etag = None
        obj.last_modified = None
        await obj.reload()
        # TODO: test move and rename

        # test that the user is and only is in group Domain Users
        with pytest.raises(AssertionError):
            for group in obj.objects.groups:
                grp = await group.open()
                assert grp.properties["name"] != "Domain Users"

        container = await cn.new()
        container.properties["name"] = random_string()
        await container.save()

        container2 = await cn.new()
        container2.properties["name"] = random_string()
        await container2.save()

        await obj.move(container.dn)
        assert container.dn in obj.dn

        await container.move(container2.dn)
        assert container2.dn in container.dn

        obj.hal.clear()
        obj.representation["dn"] = "uid=%s,%s" % (
            obj.properties["username"],
            container.dn,
        )
        await obj.reload()
        obj.properties["description"] = "muhahaha"
        await obj.save()

        await obj.delete()


@pytest.mark.asyncio()
async def test_json_patch(random_string, ucr):
    uri = "http://localhost/univention/udm/"
    async with UDM.http(uri, "Administrator", "univention") as udm:
        module = await udm.get("users/user")
        obj = await module.new()
        patch = PatchDocument()
        username = random_string()
        lastname = random_string()
        firstname = random_string()
        description = random_string()
        patch.replace(["properties", "username"], username)
        patch.replace(["properties", "lastname"], lastname)
        patch.replace(["properties", "firstname"], firstname)
        patch.replace(["properties", "password"], random_string())
        patch.replace(["properties", "description"], description)
        await obj.json_patch(patch.patch)
        assert obj.properties["username"] == username
        # assert obj.properties['lastname'] == lastname
        assert obj.properties["firstname"] == firstname
        assert obj.properties["description"] == description

        patch = PatchDocument()
        firstname = random_string()
        patch.add(["properties", "firstname"], firstname)  # not multivalue, but let's try
        patch.remove(["properties", "description"], description)
        await obj.json_patch(patch.patch)
        assert obj.properties["username"] == username
        # assert obj.properties['lastname'] == lastname
        # assert obj.properties['firstname'] == firstname
        assert obj.properties["description"] == description


@pytest.mark.asyncio()
async def test_various_api_methods(random_string, ucr):
    uri = "http://localhost/univention/udm/"
    async with UDM.http(uri, "Administrator", "univention") as udm:
        assert (await udm.get_ldap_base()) == ucr["ldap/base"]
        mod = await udm.get("container/dc")
        with pytest.raises(_NoRelation):
            await mod.new()
        assert (await (await udm.get("users/user")).new()).uri is None

        obj = await udm.obj_by_dn(ucr["ldap/base"])
        assert obj
        obj2 = await udm.obj_by_uuid(obj.representation["uuid"])
        obj3 = await udm.get_object("container/dc", ucr["ldap/base"])
        obj4 = await mod.get_by_entry_uuid(obj.representation["uuid"])

        assert obj.dn == obj2.dn == obj3.dn == obj4.dn

        await obj.reload()
        assert obj.dn == obj2.dn

        assert repr(udm).startswith("UDM(uri=")
        assert repr(mod).startswith("Module(uri=")
        assert repr(obj).startswith("Object(module=")
        async for shallow_obj in mod.search(opened=False):
            assert repr(shallow_obj).startswith("ShallowObject(dn=")

        assert (await udm.get("users/nothing")) is None

        assert await mod.get_layout()
        assert await mod.get_properties()
        assert await mod.get_property_choices("dnsForwardZone")
        with pytest.raises(_NoRelation):
            await mod.policy_result("policies/nothing", ucr["ldap/base"])
        assert isinstance(await mod.policy_result("policies/umc", ucr["ldap/base"]), dict)

        assert await obj.get_layout()
        assert await obj.get_properties()
        assert await obj.get_property_choices("dnsForwardZone")
        assert isinstance(await obj.policy_result("policies/umc"), dict)

        report_types = await (await udm.get("users/user")).get_report_types()
        assert len(report_types) == 2
        await (await udm.get("users/user")).create_report(report_types[0], ["uid=Administrator,cn=users,%(ldap/base)s" % ucr])

        superordinate = (await (await udm.get("dns/forward_zone")).search().__anext__()).dn
        ptr = await (await udm.get("dns/host_record")).search(superordinate=superordinate, opened=True).__anext__()
        assert ptr.dn
        ptr.superordinate = superordinate

        with pytest.raises(NotFound):
            await mod.get("cn=users,%(ldap/base)s" % ucr)
        with pytest.raises(UnprocessableEntity):
            await mod.get("cn=notexists,%(ldap/base)s" % ucr)
        with pytest.raises(NotFound):
            await mod.get_by_entry_uuid("6d925222-6706-48c5-bf33-86ef00610b3f")
