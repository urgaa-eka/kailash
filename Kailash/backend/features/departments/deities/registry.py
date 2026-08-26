
from backend.features.departments.deities.agni import AgniDepartment
from backend.features.departments.deities.ashwini import AshwiniDepartment
from backend.features.departments.deities.base_department import BaseDepartment
from backend.features.departments.deities.brahma import BrahmaDepartment
from backend.features.departments.deities.brihaspati import BrihaspatiDepartment
from backend.features.departments.deities.chandra import ChandraDepartment
from backend.features.departments.deities.dharma import DharmaDepartment
from backend.features.departments.deities.durga import DurgaDepartment
from backend.features.departments.deities.hanuman import HanumanDepartment
from backend.features.departments.deities.indra import IndraDepartment
from backend.features.departments.deities.kartikeya import KartikeyaDepartment
from backend.features.departments.deities.kubera import KuberaDepartment
from backend.features.departments.deities.lakshmi import LakshmiDepartment
from backend.features.departments.deities.narada import NaradaDepartment
from backend.features.departments.deities.saraswati import SaraswatiDepartment
from backend.features.departments.deities.surya import SuryaDepartment
from backend.features.departments.deities.varuna import VarunaDepartment
from backend.features.departments.deities.vayu import VayuDepartment
from backend.features.departments.deities.vishnu import VishnuDepartment
from backend.features.departments.deities.vishwakarma import VishwakarmaDepartment
from backend.features.departments.deities.yama import YamaDepartment

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
