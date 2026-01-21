# models/states.py
from aiogram.fsm.state import State, StatesGroup

class QuickTestStates(StatesGroup):
    questions = State()

class MaslachTestStates(StatesGroup):
    questions = State()

class BoykoTestStates(StatesGroup):
    questions = State()

class HeckHessTestStates(StatesGroup):
    questions = State()