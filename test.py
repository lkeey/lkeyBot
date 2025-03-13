from json import *

question = {1: {"task": "Сколько будет 2+2?", "options": ["3", "4", "5", "6"]}}

with open("polls.json", "w") as f:
    dump(question, f)
