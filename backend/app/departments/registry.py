from typing import Dict
from .base_department import BaseDepartment
from .vishwakarma import VishwakarmaDepartment
from .lakshmi import LakshmiDepartment
from .surya import SuryaDepartment
from .saraswati import SaraswatiDepartment
from .vayu import VayuDepartment
from .kubera import KuberaDepartment
from .indra import IndraDepartment
from .yama import YamaDepartment
from .varuna import VarunaDepartment
from .agni import AgniDepartment
from .chandra import ChandraDepartment
from .brihaspati import BrihaspatiDepartment
from .vishnu import VishnuDepartment
from .brahma import BrahmaDepartment
from .kartikeya import KartikeyaDepartment
from .durga import DurgaDepartment
from .hanuman import HanumanDepartment
from .narada import NaradaDepartment
from .ashwini import AshwiniDepartment
from .dharma import DharmaDepartment

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

DEPARTMENT_REGISTRY: Dict[str, BaseDepartment] = {}

def initialize_departments():
    """Initialize all department instances"""
    global DEPARTMENT_REGISTRY
    for name, dept_class in DEPARTMENT_CLASSES.items():
        DEPARTMENT_REGISTRY[name] = dept_class()

def get_department(name: str) -> BaseDepartment:
    """Get department by name"""
    return DEPARTMENT_REGISTRY.get(name.upper())

def list_departments() -> Dict[str, Dict]:
    """List all departments"""
    return {name: dept.get_status() for name, dept in DEPARTMENT_REGISTRY.items()}

initialize_departments()
