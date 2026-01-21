# services/__init__.py
from .test_calculator import TestCalculator
from .recommendations import (
    get_boyko_recommendations,
    get_maslach_recommendations,
    get_heck_hess_recommendations,
    get_quick_test_recommendations,
    get_general_it_recommendations,
    get_general_prevention_tips  # <-- добавьте эту строку
)

__all__ = [
    'TestCalculator',
    'get_boyko_recommendations',
    'get_maslach_recommendations',
    'get_heck_hess_recommendations',
    'get_quick_test_recommendations',
    'get_general_it_recommendations',
    'get_general_prevention_tips'  # <-- добавьте эту строку
]