from .ofac import OFACModule
from .opencorporates import OpenCorporatesModule
from .whois import WhoisModule
from .username_enum import UsernameEnumModule

ALL_MODULES = [
    OFACModule(),
    OpenCorporatesModule(),
    WhoisModule(),
    UsernameEnumModule(),
]
