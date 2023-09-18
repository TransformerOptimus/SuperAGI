from enum import Enum

class IsInstalled(Enum):
    INSTALLED = 'INSTALLED'
    UNINSTALLED = 'UNINSTALLED'

    @classmethod
    def get_install_state(cls, is_installed):
        if is_installed is None:
            raise ValueError("Queue status type cannot be None.")
        is_installed = is_installed.upper()

        if is_installed in cls.__members__:
            return cls[is_installed]
        raise ValueError(f"{is_installed} is not a valid storage name.")