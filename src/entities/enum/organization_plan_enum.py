from enum import Enum


class OrganizationPlanEnum(Enum):
    PRO = "pro"
    BASIC = "basic"
    ULTRA = "ultra"

    @classmethod
    def from_str(cls, plan: str):
        try:
            return OrganizationPlanEnum(plan)
        except KeyError:
            return OrganizationPlanEnum.BASIC
