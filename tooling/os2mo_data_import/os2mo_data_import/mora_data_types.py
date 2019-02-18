#
# Copyright (c) Magenta ApS
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#


class MoType():
    """
    Base class for all Mo (MORA) type objects

    :param uuid:
    The object uuid (str/uuid)
    This can be set to forcefully import the object with its current uuid.
    If the object already exists in the database, it is updated/overridden.

    :param type_id:
    Type identifier for "detail" objects (str)
    A detail object can be one of the following types:
        address, association, role, itsystem, engagement, manager

    :param date_from:
    Start date e.g. "1900-01-01" (str)

    :param date_to:
    End date e.g. "1900-01-01" (str)
    """

    insert_data = True

    def __init__(self):
        self.type_id = None

        self.payload = {}

        self.date_from = None
        self.date_to = None

        # Streamline
        # Force uuid on objects
        self.uuid = None

        # Compatibility:
        # Write details after unit or employee is stored
        self.person_uuid = None
        self.org_unit_uuid = None

    def _build_payload(self):
        """
        Create a POST data payload for os2mo (mora)

        As a minimum the date_from and date_to attributes must be set.
        Additionally must each set the type_id attribute.
        Optionally a person_uuid and org_unit_uuid can be set
        on "detail" class objects which belong to either
        an organisation unit or a employee.

        :return: Returns a POST data payload (Type: dict)
        """

        if not isinstance(self.payload, dict):
            raise TypeError("Cannot build non-dict types")

        if self.uuid:
            self.payload["uuid"] = self.uuid

        # Add type:
        if self.type_id:
            self.payload["type"] = self.type_id

        if self.person_uuid:
            self.payload["person"] = {
                "uuid": self.person_uuid
            }

        if self.org_unit_uuid:
            self.payload["org_unit"] = {
                "uuid": self.org_unit_uuid
            }

        # Add validity:
        self.payload["validity"] = {
            "from": self.date_from,
            "to": self.date_to
        }

        return self.payload

    def __repr__(self):
        return str(self.__dict__)


class AddressType(MoType):
    """
    Address type detail which belongs to eit

    :param value:
    The address value (str)
    Example:
        The value can be a phone number:
        value: 11223344

        or a reference to a DAR object:
        value: 62B99146-BA66-4563-B15E-A4F4B9000B58

    :param type_ref:
    Reference to the Klasse object that contains the scope (str)

    The os2mo representation of the values depends on its scope.
    The type_ref refers to a scope by referencing the Klasse object that contains
    the scope.

    For more information, please see mox_data_types:Klasse.

    :param visibility:
    Visibility toggle of whether the value is displayed (bool)

    :param uuid:
    The object uuid (str/uuid)

    :param date_from:
    Start date e.g. "1900-01-01" (str)

    :param date_to:
    End date e.g. "1900-01-01" (str)
    """

    def __init__(self, value, type_ref, date_from,
                 date_to=None, uuid=None, visibility=None):
        super().__init__()

        self.type_id = "address"

        self.uuid = uuid

        self.value = value
        self.type_ref = type_ref
        self.type_ref_uuid = None

        self.visibility_ref = visibility
        self.visibility_ref_uuid = None

        self.organisation_uuid = None

        # SPECIAL
        self.address_type_meta = None

        self.date_from = date_from
        self.date_to = date_to

    def build(self):
        """
        Apply class specific attributes before calling
        the underlying _build method to create the POST data payload.

        :return: POST data payload (dict)
        """

        if not self.organisation_uuid:
            raise ValueError("Organisation UUID is missing")

        self.payload = {
            "value": self.value,
            "org": {
                "uuid": self.organisation_uuid
            },
            "address_type": {
                "uuid": self.type_ref_uuid
            }
        }
        if self.visibility_ref:
            self.payload['visibility'] = {'uuid': self.visibility_ref_uuid}
        return self._build_payload()


class EngagementType(MoType):
    """
    Engagement type detail.
    This detail describes the current employment.

    :param org_unit_ref:
    Reference to the parent organisation unit of the employment (str)

    :param engagement_type_ref:
    Reference to the type of employment (str)
    Examples: "Full time", "Part time", "External", "Internal" etc.

    :param job_function_ref:
    Reference job function definition aka "job title" (str)
    Examples: "Bridge officer", "Science assistant", "Space dock cleaner" etc.

    :param uuid:
    The object uuid (str/uuid)

    :param date_from:
    Start date e.g. "1900-01-01" (str)

    :param date_to:
    End date e.g. "1900-01-01" (str)
    """

    def __init__(self, org_unit_ref, job_function_ref, engagement_type_ref,
                 date_from, date_to=None, uuid=None):
        super().__init__()

        self.type_id = "engagement"

        self.uuid = uuid
        self.org_unit_ref = org_unit_ref
        self.org_unit_uuid = None

        self.type_ref = engagement_type_ref
        self.type_ref_uuid = None

        self.job_function_ref = job_function_ref
        self.job_function_uuid = None

        self.date_from = date_from
        self.date_to = date_to

    def build(self):
        """
        Apply class specific attributes before calling
        the underlying _build method to create the POST data payload.

        :return: POST data payload (dict)
        """

        # Reference the parent org unit uuid
        if not self.org_unit_uuid:
            raise ReferenceError("Reference to parent org unit is missing")

        self.payload["org_unit"] = {
              "uuid": self.org_unit_uuid
        }

        # Reference the job function uuid
        if not self.job_function_uuid:
            raise ReferenceError("Reference to job function is missing")

        self.payload["job_function"] = {
            "uuid": self.job_function_uuid
        }

        # Reference the engagement type uuid
        if not self.type_ref_uuid:
            raise ReferenceError("Reference to engagenment type is missing")

        self.payload["engagement_type"] = {
            "uuid": self.type_ref_uuid
        }

        return self._build_payload()


class AssociationType(MoType):
    """
    Engagement type detail.
    This detail describes the current employment.

    :param org_unit_ref:
    Reference to the parent organisation unit of the employment (str)

    :param engagement_type_ref:
    Reference to the type of employment (str)
    Examples: "Full time", "Part time", "External", "Internal" etc.

    :param job_function_ref:
    Reference job function definition aka "job title" (str)
    Examples: "Bridge officer", "Science assistant", "Space dock cleaner" etc.

    :param association_type_ref:
    Reference to the association
    that the employee has with the organisation unit (str)
    There are several ways to define an association,
    for example it could be that an employee is associated with
    any given projects/tasks within the organisation unit.

    Example:
        Employee: Luke Skywalker
        Organisation unit: Republic
        Engagement: Jedi/Rebel scum
        Association: Affairs on the moon of Endor

    :param address_uuid:
    The (uuid) identifier of a DAR address object (str/uuid)

    :param address_type_ref:
    Reference to the address type (str)
    NOTE: this can only be a reference to a Klasse object with the scope: DAR.

    :param uuid:
    The object uuid (str/uuid)

    :param date_from:
    Start date e.g. "1900-01-01" (str)

    :param date_to:
    End date e.g. "1900-01-01" (str)
    """

    def __init__(self, association_type_ref, org_unit_ref, job_function_ref,
                 date_from, date_to=None, address_uuid=None, address_type_ref=None,
                 uuid=None):
        super().__init__()

        self.type_id = "association"

        self.uuid = uuid

        self.org_unit_ref = org_unit_ref
        self.org_unit_uuid = None

        self.job_function_ref = job_function_ref
        self.job_function_uuid = None

        self.type_ref = association_type_ref
        self.type_ref_uuid = None

        self.address_uuid = address_uuid

        # Workaround for address_type_ref
        self.address_type_ref = (address_type_ref or "AdressePostEmployee")
        self.address_type_uuid = None

        self.date_from = date_from
        self.date_to = date_to

    def build(self):
        """
        Apply class specific attributes before calling
        the underlying _build method to create the POST data payload.

        :return: POST data payload (dict)
        """

        if not self.org_unit_uuid:
            raise ReferenceError("Reference to org_unit_uuid is missing")

        if not self.job_function_uuid:
            raise ReferenceError("Reference to job_function_uuid is missing")

        if not self.type_ref_uuid:
            raise ReferenceError("Reference to association_type_uuid is missing")

        self.payload = {
            "org_unit": {
                "uuid": self.org_unit_uuid
            },
            "job_function": {
                "uuid": self.job_function_uuid
            },
            "association_type": {
                "uuid": self.type_ref_uuid
            }
        }

        if self.address_uuid:
            self.payload["address"] = {
                "uuid": self.address_uuid,
                "address_type": {
                    "uuid": self.address_type_uuid
                }
            }

        return self._build_payload()


class ItsystemType(MoType):
    """
    Creates a detail object that describes the connection
    with an existing it system.

    :param: itsystem_ref:
    Reference to the it system type (str)

    :param uuid:
    The object uuid (str/uuid)

    :param date_from:
    Start date e.g. "1900-01-01" (str)

    :param date_to:
    End date e.g. "1900-01-01" (str)
    """

    def __init__(self, user_key, itsystem_ref, date_from, date_to=None, uuid=None):
        super().__init__()

        self.type_id = "it"

        self.uuid = uuid

        self.user_key = user_key
        self.itsystem_ref = itsystem_ref
        self.itsystem_uuid = None

        self.date_from = date_from
        self.date_to = date_to

    def build(self):
        """
        Apply class specific attributes before calling
        the underlying _build method to create the POST data payload.

        :return: POST data payload (dict)
        """

        if not self.itsystem_uuid:
            raise ReferenceError("UUID of itsystem type is missing")

        self.payload = {
            "user_key": self.user_key,
            "itsystem": {
                "uuid": self.itsystem_uuid
            }
        }

        return self._build_payload()


class LeaveType(MoType):
    """
    Leave type detail describes a period of leave of absence
    of an associated employee.

    :param leave_type_ref:
    Reference to the type of leave (str)
    Examples: "Illness", "R & R", "Captivity", "Off-record secret mission"

    :param uuid:
    The object uuid (str/uuid)

    :param date_from:
    Start date e.g. "1900-01-01" (str)

    :param date_to:
    End date e.g. "1900-01-01" (str)
    """

    def __init__(self, leave_type_ref, date_from, date_to=None, uuid=None):
        super().__init__()

        self.type_id = "leave"

        self.uuid = uuid

        self.type_ref = leave_type_ref
        self.type_ref_uuid = None

        self.date_from = date_from
        self.date_to = date_to

    def build(self):
        """
        Apply class specific attributes before calling
        the underlying _build method to create the POST data payload.

        :return: POST data payload (dict)
        """

        self.payload = {
            "leave_type": {
                "uuid": self.type_ref_uuid
            }
        }

        return self._build_payload()


class RoleType(MoType):
    """
    Role type detail describes a which role an employee holds
    with the associated organisation unit.

    :param org_unit:
    Reference to the associated organisation unit (str)

    :param role_type_ref:
    Reference to the role type (str)
    Examples: "Illness", "R & R", "Captivity", "Off-record secret mission"

    :param uuid:
    The object uuid (str/uuid)

    :param date_from:
    Start date e.g. "1900-01-01" (str)

    :param date_to:
    End date e.g. "1900-01-01" (str)
    """

    def __init__(self, org_unit, role_type_ref, date_from, date_to=None, uuid=None):
        super().__init__()

        self.type_id = "role"

        self.uuid = uuid

        self.org_unit_ref = org_unit
        self.org_unit_uuid = None

        self.type_ref = role_type_ref
        self.type_ref_uuid = None

        self.date_from = date_from
        self.date_to = date_to

    def build(self):
        """
        Apply class specific attributes before calling
        the underlying _build method to create the POST data payload.

        :return: POST data payload (dict)
        """

        self.payload = {
            "org_unit": {
                "uuid": self.org_unit_uuid
            },
            "role_type": {
                "uuid": self.type_ref_uuid
            }
        }

        return self._build_payload()


class ManagerType(MoType):
    """
    Role type detail describes a which role an employee holds
    with the associated organisation unit.

    :param org_unit:
    Reference to the associated organisation unit (str)

    :param manager_type_ref:
    Reference to type of manager position (str)
    Examples: "Jedi Master", "Emperor" etc.

    :param manager_level_ref:
    Reference to the role type (str)
    Examples: "Security level 5", "Bridge access" etc

    :param responsibility_list:
    List of references to responsibility types (list)
    Examples: "Bridge officer", "Squad leader", "Victory party organiser"

    :param address_uuid:
    The (uuid) identifier of a DAR address object (str/uuid)

    :param address_type_ref:
    Reference to the address type (str)
    NOTE: this can only be a reference to a Klasse object with the scope: DAR.

    :param uuid:
    The object uuid (str/uuid)

    :param date_from:
    Start date e.g. "1900-01-01" (str)

    :param date_to:
    End date e.g. "1900-01-01" (str)
    """

    def __init__(self, org_unit, manager_type_ref, manager_level_ref,
                 responsibility_list, date_from, date_to=None,
                 address_uuid=None, address_type_ref=None, uuid=None):
        super().__init__()

        self.type_id = "manager"

        self.uuid = uuid

        self.org_unit_ref = org_unit
        self.org_unit_uuid = None

        self.type_ref = manager_type_ref
        self.type_ref_uuid = None

        self.manager_level_ref = manager_level_ref
        self.manager_level_uuid = None

        if not isinstance(responsibility_list, list):
            raise TypeError("Responsabilities must be passed as a list")

        self.responsibility_list = responsibility_list
        self.responsibilities = []

        self.address_uuid = address_uuid
        self.address_type_ref = address_type_ref
        self.address_type_uuid = None

        self.date_from = date_from
        self.date_to = date_to

    def build(self):
        """
        Apply class specific attributes before calling
        the underlying _build method to create the POST data payload.

        :return: POST data payload (dict)
        :return:
        """

        self.payload = {
            "org_unit": {
                "uuid": self.org_unit_uuid
            },
            "manager_type": {
                "uuid": self.type_ref_uuid
            },
            "manager_level": {
                "uuid": self.manager_level_uuid
            },
            "responsibility": [
                {
                    "uuid": responsibility_uuid
                }
                for responsibility_uuid in self.responsibilities
            ]
        }

        if self.address_uuid:
            self.payload["address"] = {
                "uuid": self.address_uuid,
                "address_type": {
                    "uuid": self.address_type_uuid
                }
            }

        return self._build_payload()


class OrganisationUnitType(MoType):
    """
    :param name:
    Name of the organisation unit (str)

    :param type_ref:
    Reference to the organisation unit type/Klasse (str)

    :param user_key:
    Optionally set a specific user_key (str)
    This is mainly usefull as an internal reference.

    :param parent_ref:
    Reference to the parent organisation unit/Klasse (str)
    If this value is not set, the organisation becomes the parent.

    :param uuid:
    The object uuid (str/uuid)

    :param date_from:
    Start date e.g. "1900-01-01" (str)

    :param date_to:
    End date e.g. "1900-01-01" (str)
    """

    def __init__(self, name, type_ref, date_from, date_to=None,
                 user_key=None, parent_ref=None, uuid=None):
        super().__init__()

        self.uuid = uuid
        self.name = name
        self.user_key = (user_key or name)

        self.parent_ref = parent_ref
        self.parent_uuid = None

        self.type_ref = type_ref
        self.type_ref_uuid = None

        self.details = []

        self.date_from = date_from
        self.date_to = date_to

    def build(self):
        """
        Apply class specific attributes before calling
        the underlying _build method to create the POST data payload.

        :return: POST data payload (dict)
        """

        if not self.parent_uuid:
            raise ReferenceError("UUID of the parent organisation is missing")

        if not self.type_ref_uuid:
            raise ReferenceError("UUID of the unit type is missing")

        self.payload = {
            "user_key": self.user_key,
            "name": self.name,
            "parent": {
                "uuid": self.parent_uuid
            },
            "org_unit_type": {
                "uuid": self.type_ref_uuid
            }
        }

        return self._build_payload()


class EmployeeType(MoType):
    """
    :param name:
    Full name of the employee (str)

    :param cpr_no:
    10 digit CPR identifier code (str)

    :param user_key:
    Optionally set a specific user_key (str)
    This is mainly usefull as an internal reference.

    :param org:
    Reference to the organisation to which the employee belongs (str)

    :param uuid:
    The object uuid (str/uuid)

    :param date_from:
    Start date e.g. "1900-01-01" (str)

    :param date_to:
    End date e.g. "1900-01-01" (str)
    """

    def __init__(self, name, cpr_no, org=None, uuid=None, user_key=None):
        super().__init__()

        self.name = name
        self.cpr_no = cpr_no

        self.uuid = uuid
        self.user_key = user_key

        self.org = org
        self.org_uuid = None

    def build(self):
        """
        Apply class specific attributes before calling
        the underlying _build method to create the POST data payload.

        :return: POST data payload (dict)
        """

        if not self.org_uuid:
            raise ReferenceError("UUID of the organisation is missing")

        self.payload = {
            "name": self.name,
            "cpr_no": self.cpr_no,
            "org": {
                "uuid": self.org_uuid
            }
        }

        return self._build_payload()
