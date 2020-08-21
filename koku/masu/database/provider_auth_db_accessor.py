#
# Copyright 2018 Red Hat, Inc.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""Accessor for Provider Authentication from koku database."""
from api.provider.models import ProviderAuthentication
from masu.database.koku_database_access import KokuDBAccess


class ProviderAuthDBAccessor(KokuDBAccess):
    """Class to interact with the koku database for Provider Authentication Data."""

    def __init__(self, auth_id=None, credentials=None):
        """
        Establish Provider Authentication database connection.

        Args:
            auth_id                      (string) the provider authentication unique database id
            credentials                  (dict) the credentials dictionary

        """
        super().__init__("public")
        self._auth_id = auth_id
        self._credentials = credentials
        self._table = ProviderAuthentication

    def _get_db_obj_query(self):
        """
        Return the sqlachemy query for the provider auth object.

        Args:
            None
        Returns:
            (django.db.query.QuerySet): QuerySet of objects matching the given filters

        """
        if self._auth_id and self._credentials:
            query = self._table.objects.filter(id=self._auth_id, credentials=self._credentials)
        elif self._auth_id:
            query = self._table.objects.filter(id=self._auth_id)
        elif self._credentials:
            query = self._table.objects.filter(credentials=self._credentials)
        else:
            query = self._table.objects.none()
        return query

    def get_auth_id(self):
        """
        Return the database id.

        Args:
            None
        Returns:
            (Integer): "1",

        """
        auth_obj = self._get_db_obj_query().first()
        return auth_obj.id if auth_obj else None

    def get_uuid(self):
        """
        Return the provider uuid.

        Args:
            None
        Returns:
            (String): "UUID v4",
                    example: "edf94475-235e-4b64-ba18-0b81f2de9c9e"

        """
        obj = self._get_db_obj_query().first()
        return obj.uuid

    def get_credentials(self):
        """
        Return the provider resource name.

        Args:
            None
        Returns:
            (dtring): "Provider Resource Name.  i.e. AWS: RoleARN",
                    example: {"role_arn": "arn:aws:iam::111111111111:role/CostManagement"}

        """
        obj = self._get_db_obj_query().first()
        return obj.credentials
