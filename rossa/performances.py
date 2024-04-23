from .types import PerformanceType, Option


class BasePerformance(Option):
    value: PerformanceType


class InstantPerformance(BasePerformance):
    value: PerformanceType = PerformanceType.INSTANT
    title: str = "Instant"
    description: str = "Real-time generation (up to 2 seconds)."
    default: bool = False


class BalancedPerformance(BasePerformance):
    value: PerformanceType = PerformanceType.BALANCED
    title: str = "Balanced"
    description: str = "Efficient speed and quality balance (up to 10 seconds)."
    default: bool = True


class QualityPerformance(BasePerformance):
    value: PerformanceType = PerformanceType.QUALITY
    title: str = "Quality"
    description: str = "Maximum quality (up to 20 seconds)."
    default: bool = False
