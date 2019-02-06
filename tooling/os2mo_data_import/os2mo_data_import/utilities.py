# -- coding: utf-8 --

from os2mo_data_import.mora_data_types import *
from os2mo_data_import.mox_data_types import *

import json
from urllib.parse import urljoin
from requests import Session, HTTPError
from uuid import uuid4


class ImportUtility(object):

    def __init__(self, system_name, end_marker, mox_base, mora_base,
                 store_integration_data=False, dry_run=False):

        # Import Params
        self.system_name = system_name
        self.end_marker = end_marker
        self.store_integration_data = store_integration_data


        # Service endpoint base
        self.mox_base = mox_base
        self.mora_base = mora_base

        # Session
        self.session = Session()

        # Placeholder for UUID import
        self.organisation_uuid = None

        # Existing UUIDS
        # TODO: More elegant version of this please
        self.existing_uuids = []

        # UUID map
        self.inserted_organisation = {}
        self.inserted_facet_map = {}
        self.inserted_klasse_map = {}
        self.inserted_itsystem_map = {}
        self.inserted_org_unit_map = {}
        self.inserted_employee_map = {}

        # Deprecated
        self.dry_run = dry_run

    def import_organisation(self, reference, organisation):
        """
        Convert organisation to OIO formatted post data
        and import into the MOX datastore.

        :param org_export:
        Data objected returned by the export() method (dict)

        :returns:
        Inserted UUID (str)
        """

        if not isinstance(organisation, Organisation):
            raise TypeError("Not of type Organisation")

        resource = "organisation/organisation"

        payload = organisation.build()

        integration_data = self._integration_data(
            resource=resource,
            reference=reference,
            payload=payload
        )

        organisation_uuid = integration_data.get('uuid', None)

        self.organisation_uuid = self.insert_mox_data(
            resource=resource,
            data=integration_data,
            uuid=organisation_uuid
        )

        # Global validity
        self.date_from = organisation.date_from
        self.date_to = organisation.date_to

        return self.organisation_uuid

    def import_klassifikation(self, reference, klassifikation):
        if not isinstance(klassifikation, Klassifikation):
            raise TypeError("Not of type Klassifikation")

        resource = "klassifikation/klassifikation"

        klassifikation.organisation_uuid = self.organisation_uuid

        payload = klassifikation.build()

        integration_data = self._integration_data(
            resource=resource,
            reference=reference,
            payload=payload
        )

        klassifikation_uuid = integration_data.get('uuid', None)

        self.klassifikation_uuid = self.insert_mox_data(
            resource=resource,
            data=integration_data,
            uuid=klassifikation_uuid
        )

        return self.klassifikation_uuid

    def import_facet(self, reference, facet):
        """
        Generate and insert a facet object
        This is the parent of all the klasse type objects.

        :param reference:
            Reference to the user defined identifier (str)

        :param klasse:
            Facet type data object (dict)

        :returns:
            Inserted UUID (str)
        """

        if not isinstance(facet, Facet):
            raise TypeError("Not of type Facet")

        resource = "klassifikation/facet"

        facet.organisation_uuid = self.organisation_uuid
        facet.klassifikation_uuid = self.klassifikation_uuid

        # NEED TO BE FIXED
        facet.date_from = self.date_from
        facet.date_to = self.date_to

        payload = facet.build()

        integration_data = self._integration_data(
            resource=resource,
            reference=reference,
            payload=payload
        )

        facet_uuid = integration_data.get('uuid', None)

        self.inserted_facet_map[reference] = self.insert_mox_data(
            resource=resource,
            data=integration_data,
            uuid=facet_uuid
        )

        return self.inserted_facet_map[reference]

    def import_klasse(self, reference, klasse):
        """
        Insert a klasse object

        :param reference:
        Reference to the user defined identifier (str)

        :param klasse:
        Klasse type data object (dict)

        :returns:
        Inserted UUID (str)
        """

        if not isinstance(klasse, Klasse):
            raise TypeError("Not of type Facet")

        uuid = klasse.uuid
        facet_ref = klasse.facet_type_ref

        facet_uuid = self.inserted_facet_map.get(facet_ref)

        if not facet_uuid:
            print(klasse)
            error_message = "Facet ref: {ref} does not exist".format(
                ref=facet_ref
            )
            raise KeyError(error_message)

        resource = "klassifikation/klasse"

        klasse.organisation_uuid = self.organisation_uuid
        klasse.facet_uuid = facet_uuid
        klasse.date_from = self.date_from
        klasse.date_to = self.date_to

        payload = klasse.build()

        integration_data = self._integration_data(
            resource=resource,
            reference=reference,
            payload=payload
        )

        if 'uuid' in integration_data:
            klasse_uuid = integration_data['uuid']
            assert(uuid is None or klasse_uuid == uuid)
        else:
            if uuid is None:
                klasse_uuid = None
            else:
                klasse_uuid = uuid[0] # Internal representation is a 1-element tuple

        import_uuid = self.insert_mox_data(
            resource="klassifikation/klasse",
            data=integration_data,
            uuid=klasse_uuid
        )

        assert(uuid is None or import_uuid == klasse_uuid)
        self.inserted_klasse_map[reference] = import_uuid

        return self.inserted_klasse_map[reference]

    def import_itsystem(self, reference, itsystem):
        """
        Insert an itsystem object

        :param itsystem:
        Itsystem data object (dict)

        :returns:
        Inserted UUID (str)
        """

        if not isinstance(itsystem, Itsystem):
            raise TypeError("Not of type Itsystem")

        resource = 'organisation/itsystem'

        itsystem.organisation_uuid = self.organisation_uuid
        itsystem.date_from = self.date_from
        itsystem.date_to = self.date_to

        payload = itsystem.build()

        integration_data = self._integration_data(
            resource=resource,
            reference=reference,
            payload=payload
        )

        if 'uuid' in integration_data:
            itsystem_uuid = integration_data['uuid']
        else:
            itsystem_uuid = None

        self.inserted_itsystem_map[reference] = self.insert_mox_data(
            resource=resource,
            data=integration_data,
            uuid=itsystem_uuid
        )

        return self.inserted_itsystem_map[reference]

    def import_org_unit(self, reference, organisation_unit, details=[]):
        """
        Insert primary and optional data for an organisation unit

        Optional data objects are relational objects which
        belong to the organisation unit, such as an address type

        :param reference:
        Reference to the user defined identifier (str)

        :param organisation_unit_data:
        Organisation Unit primary data object (dict)

        :param optional_data:
        Organisation Unit optional data object (dict)

        :returns:
        Inserted UUID (str)
        """

        if not isinstance(organisation_unit, OrganisationUnitType):
            raise TypeError("Not of type OrganisationUnitType")

        if reference in self.inserted_org_unit_map:
            print("The organisation unit has already been inserted")
            return False

        resource = 'organisation/organisationenhed'

        # payload = self.build_mo_payload(organisation_unit_data)
        parent_ref = organisation_unit.parent_ref
        if parent_ref:
            parent_uuid = self.inserted_org_unit_map.get(parent_ref)
            organisation_unit.parent_uuid = parent_uuid

        if not organisation_unit.parent_uuid:
            organisation_unit.parent_uuid = self.organisation_uuid

        type_ref_uuid = self.inserted_klasse_map.get(
            organisation_unit.type_ref
        )

        organisation_unit.type_ref_uuid = type_ref_uuid

        # Build details (if any)
        for detail in details:

            date_from = detail.date_from

            if not date_from:
                date_from = organisation_unit.date_from

            build_detail = self.build_detail(
                detail=detail,
                date_from=date_from,
                date_to=organisation_unit.date_to
            )

            if not build_detail:
                continue

            organisation_unit.details.append(build_detail)


        payload = organisation_unit.build()

        integration_data = self._integration_data(
            resource=resource,
            reference=reference,
            payload=payload,
            encode_integration=False
        )

        uuid = self.insert_mora_data(
            resource="service/ou/create",
            data=integration_data
        )

        if 'uuid' in integration_data:
            assert (uuid == integration_data['uuid'])
        if not uuid:
            raise ConnectionError("Something went wrong")

        # Add to the inserted map
        self.inserted_org_unit_map[reference] = uuid

        return uuid

    def import_employee(self, reference, employee, details=[]):
        if not isinstance(employee, EmployeeType):
            raise TypeError("Not of type EmployeeType")

        # Build details (if any)
        for detail in details:
            date_from = detail.date_from

            if not date_from:
                date_from = self.date_from

            build_payload = self.build_detail(
                detail=detail,
                date_from=date_from,
                date_to=employee.date_to
            )

            if not build_payload:
                continue

            employee.details.append(build_payload)

        employee.org_uuid = self.organisation_uuid
        payload = employee.build()

        mox_resource = 'organisation/bruger'

        integration_data = self._integration_data(
            resource=mox_resource,
            reference=reference,
            payload=payload,
            encode_integration=False
        )

        # We unconditionally create or update the user, this should
        # ensure that we alwas updated with correct current information.
        mora_resource = "service/e/create"
        uuid = self.insert_mora_data(
            resource=mora_resource,
            data=integration_data
        )

        if 'uuid' in integration_data:
            assert (uuid == integration_data['uuid'])

        # Add uuid to the inserted employee map
        self.inserted_employee_map[reference] = uuid

        return uuid

    def build_detail(self, detail, date_from, date_to):

        # Waiting for removal of scope requirement
        # Validation fails when attempting to insert "leave"
        # as detail during employee creation
        blacklist = [
            "address",
            "leave"
        ]

        if detail.type_id in blacklist:
            return

        # Set validity
        detail.date_from = date_from
        detail.date_to = date_to

        common_attributes = [
            ("type_ref", "type_ref_uuid"),
            ("job_function_ref", "job_function_uuid"),
            ("address_type_ref", "address_type_uuid"),
            ("manager_level_ref", "manager_level_uuid")
        ]

        for check_value, set_value in common_attributes:
            if not hasattr(detail, check_value):
                continue

            uuid = self.inserted_klasse_map.get(
                getattr(detail, check_value)
            )

            setattr(detail, set_value, uuid)

        # Uncommon attributes
        if hasattr(detail, "org_unit_ref"):
            detail.org_unit_uuid = self.inserted_org_unit_map.get(
                detail.org_unit_ref
            )

        if hasattr(detail, "organisation_uuid"):
            detail.organisation_uuid = self.organisation_uuid

        if hasattr(detail, "itsystem_ref"):
            detail.itsystem_uuid = self.inserted_itsystem_map.get(
                detail.itsystem_ref
            )

        if hasattr(detail, "responsibilities"):
            detail.responsibilities = [
                self.inserted_klasse_map[reference]
                for reference in detail.responsibility_list
            ]

        return detail.build()

    def _integration_data(self, resource, reference, payload={},
                          encode_integration=True):
        """
        Update the payload with integration data. Checks if an object with this
        integration data already exists. In this case the uuid of the exisiting
        object is put into the payload. If a supplied uuid is inconsistent with
        the uuid found from integration data, an exception is raised.

        :param resource:
        LoRa resource URL.

        :param referece:
        Unique label that will be stored in the integration data to identify the
        object on re-import.

        :param payload:
        The supplied payload will be updated with values for integration and uuid
        (if the integration data was found from an earlier import). For MO objects,
        payload will typically be pre-populated and will then be ready for import
        when returned. For MOX objects, the initial payload
        will typically be empty, and the returned values can be fed to the relevant
        adapter.

        :param encode_integration:
        If True, the integration data will be returned in json-encoded form.

        :return:
        The original payload updated with integration data and object uuid, if the
        object was already imported.
        """
        # TODO: We need to have a list of all objects with integration data to
        # be able to make a list of objects that has disappeared
        if self.store_integration_data:

            service = urljoin(self.mox_base, resource)
            query_params = {
                "integrationsdata": "%{}%"
            }

            # integration_data = {self.system_name: reference + self.system_name}

            integration_data = {
                self.system_name: "{reference}{end}".format(
                    reference=reference,
                    end=self.end_marker
                )
            }

            integration_data_as_json = json.dumps(integration_data)[1:-1]

            # Call repr to ensure escaping consistent with the payload from request
            response = self.session.get(url=service, params=query_params)
            response = response.json()['results'][0]

            if len(response) == 0:
                pass

            elif len(response) == 1:
                uuid = response[0]
                self.existing_uuids.append(uuid)
                if 'uuid' in payload:
                    assert (uuid == payload['uuid'])
                else:
                    payload['uuid'] = uuid

                # Get the entire integration data string, we need to be polite
                # towards the existing content:

                # Scope issue
                egenskaber = None

                object_url = '{}/{}'.format(service, uuid)
                object_data = self.session.get(object_url)
                object_data = object_data.json()[uuid]
                attributter = object_data[0]['registreringer'][0]['attributter']
                for key in attributter.keys():
                    if key.find('egenskaber') > 0:
                        egenskaber = attributter[key][0]

                integration_data = json.loads(egenskaber['integrationsdata'])

            else:
                raise ValueError('Inconsistent integration data!')

            if encode_integration:
                payload['integration_data'] = json.dumps(integration_data)
            else:
                payload['integration_data'] = integration_data

        return payload

    def insert_mox_data(self, resource, data, uuid=None):

        service_url = urljoin(
            base=self.mox_base,
            url=resource
        )

        if uuid:
            update_url = urljoin(service_url, uuid)
            response = self.session.put(
                url=update_url,
                json=data
            )

            if response.status_code != 200:
                # DEBUG
                # TODO: Implement logging
                print("============ ERROR ===========")
                print(resource)
                print(
                    json.dumps(data, indent=2)
                )

                raise HTTPError("Inserting mox data failed")

        else:
            response = self.session.post(
                url=service_url,
                json=data
            )

            if response.status_code != 201:
                # DEBUG
                # TODO: Implement logging
                print("============ ERROR ===========")
                print(resource)
                print(
                    json.dumps(data, indent=2)
                )

                raise HTTPError("Inserting mox data failed")

        response_data = response.json()

        return response_data["uuid"]


    def insert_mora_data(self, resource, data, uuid=None):

        # TESTING
        if self.dry_run:
            uuid = uuid4()
            return str(uuid)

        params = {
            "force": 1
        }

        service_url = urljoin(
            base=self.mora_base,
            url=resource
        )

        response = self.session.post(
            url=service_url,
            json=data,
            params=params
        )

        response_data = response.json()

        if response.status_code != 201:

            # DEBUG
            # TODO: Implement logging
            print("============ ERROR ===========")
            print(resource)
            print(
                json.dumps(data, indent=2)
            )

            raise HTTPError("Inserting mora data failed")

        response_data = response.json()

        # Returns a string rather than a json object
        # Example: "0fd6a479-8569-42dd-9614-4aacb611306e"
        return response_data
