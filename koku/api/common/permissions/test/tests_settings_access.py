#
# Copyright 2020 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Tests for Settings Access Permissions."""
from unittest.mock import Mock

from django.test import TestCase

from api.common.permissions.settings_access import SettingsAccessPermission
from api.iam.models import User


class SettingsAccessPermissionTest(TestCase):
    """Test the settings access permission."""

    def test_has_perm_admin(self):
        """Test that an admin user can execute."""
        user = Mock(spec=User, admin=True)
        req = Mock(user=user)
        accessPerm = SettingsAccessPermission()
        result = accessPerm.has_permission(request=req, view=None)
        self.assertTrue(result)

    def test_has_perm_with_access_on_get(self):
        """Test that a user read."""
        user = Mock(spec=User, admin=False)
        req = Mock(user=user, method="GET")
        accessPerm = SettingsAccessPermission()
        result = accessPerm.has_permission(request=req, view=None)
        self.assertTrue(result)

    def test_has_perm_with_no_access_on_post(self):
        """Test that a user cannot execute POST."""
        user = Mock(spec=User, admin=False)
        req = Mock(user=user, method="POST", META={"PATH_INFO": "http://localhost/api/v1/settings/"})
        accessPerm = SettingsAccessPermission()
        result = accessPerm.has_permission(request=req, view=None)
        self.assertFalse(result)
