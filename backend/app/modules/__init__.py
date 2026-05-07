from .ofac import OFACModule
from .opencorporates import OpenCorporatesModule
from .whois import WhoisModule
from .username_enum import UsernameEnumModule
from .courtlistener import CourtListenerModule
from .sec_edgar import SecEdgarModule
from .fec import FecModule
from .faa_registry import FaaRegistryModule
from .hibp import HibpModule
from .dns_lookup import DnsLookupModule
from .ip_geolocation import IpGeolocationModule
from .gdelt import GdeltModule

ALL_MODULES = [
    OFACModule(),
    OpenCorporatesModule(),
    WhoisModule(),
    UsernameEnumModule(),
    CourtListenerModule(),
    SecEdgarModule(),
    FecModule(),
    FaaRegistryModule(),
    HibpModule(),
    DnsLookupModule(),
    IpGeolocationModule(),
    GdeltModule(),
]
