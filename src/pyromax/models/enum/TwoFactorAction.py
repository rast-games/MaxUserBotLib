from enum import Enum


class TwoFactorAction(Enum):
    SET_PASSWORD = "set_password"
    UPDATE_PASSWORD = "update_password"
    RESTORE_PASSWORD = "restore_password"
    HINT = "hint"
    EMAIL = "email"
    REMOVE_2FA = "remove_2fa"
