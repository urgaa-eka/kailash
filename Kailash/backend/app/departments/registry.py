
from .agni import AgniDepartment
from .ashwini import AshwiniDepartment
from .base_department import BaseDepartment
from .brahma import BrahmaDepartment
from .brihaspati import BrihaspatiDepartment
from .chandra import ChandraDepartment
from .dharma import DharmaDepartment
from .durga import DurgaDepartment
from .hanuman import HanumanDepartment
from .indra import IndraDepartment
from .kartikeya import KartikeyaDepartment
from .kubera import KuberaDepartment
from .lakshmi import LakshmiDepartment
from .narada import NaradaDepartment
from .saraswati import SaraswatiDepartment
from .surya import SuryaDepartment
from .varuna import VarunaDepartment
from .vayu import VayuDepartment
from .vishnu import VishnuDepartment
from .vishwakarma import VishwakarmaDepartment
from .yama import YamaDepartment

DEPARTMENT_CLASSES = {
    "VISHWAKARMA": VishwakarmaDepartment,
    "LAKSHMI": LakshmiDepartment,
    "SURYA": SuryaDepartment,
    "SARASWATI": SaraswatiDepartment,
    "VAYU": VayuDepartment,
    "KUBERA": KuberaDepartment,
    "INDRA": IndraDepartment,
    "YAMA": YamaDepartment,
    "VARUNA": VarunaDepartment,
    "AGNI": AgniDepartment,
    "CHANDRA": ChandraDepartment,
    "BRIHASPATI": BrihaspatiDepartment,
    "VISHNU": VishnuDepartment,
    "BRAHMA": BrahmaDepartment,
    "KARTIKEYA": KartikeyaDepartment,
    "DURGA": DurgaDepartment,
    "HANUMAN": HanumanDepartment,
    "NARADA": NaradaDepartment,
    "ASHWINI": AshwiniDepartment,
    "DHARMA": DharmaDepartment,
}

DEPARTMENT_REGISTRY: dict[str, BaseDepartment] = {}

def initialize_departments():
    """Initialize all department instances"""
    global DEPARTMENT_REGISTRY
    for name, dept_class in DEPARTMENT_CLASSES.items():
        DEPARTMENT_REGISTRY[name] = dept_class()

def get_department(name: str) -> BaseDepartment:
    """Get department by name"""
    return DEPARTMENT_REGISTRY.get(name.upper())

def list_departments() -> dict[str, dict]:
    """List all departments"""
    return {name: dept.get_status() for name, dept in DEPARTMENT_REGISTRY.items()}

initialize_departments()
