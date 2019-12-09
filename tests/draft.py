import os

current_path = __file__
print(os.getcwd())
print(current_path)
print(os.path.dirname(current_path))
print(os.path.abspath(os.path.join(os.path.dirname(current_path), '..')))
