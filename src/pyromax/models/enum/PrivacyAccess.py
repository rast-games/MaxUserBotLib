from enum import Enum


class PrivacyAccess(str, Enum):
    ALL = "ALL"
    CONTACTS = "CONTACTS"
    NOBODY = "NOBODY"
