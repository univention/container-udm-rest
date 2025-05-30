# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest

from univention.testing.helm.best_practice.image_configuration import ImageConfiguration


class TestImageConfiguration(ImageConfiguration):

    @pytest.mark.skip(reason="TODO: Allow to configure the local key per container")
    def test_image_registry_overrides_global_default_registry():
        pass

    @pytest.mark.skip(reason="TODO: Allow to configure the local key per container")
    def test_image_pull_policy_overrides_global_value():
        pass

    @pytest.mark.skip(reason="TODO: Allow to configure the local key per container")
    def test_image_pull_secrets_can_be_provided():
        pass

    @pytest.mark.skip(reason="TODO: Allow to configure the local key per container")
    def test_image_repository_can_be_configured():
        pass

    @pytest.mark.skip(reason="TODO: Allow to configure the local key per container")
    def test_image_tag_can_be_configured():
        pass

    @pytest.mark.skip(reason="TODO: Allow to configure the local key per container")
    def test_all_image_values_are_configured():
        pass
