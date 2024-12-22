'''Replace Magic Number with Symbolic Constant'''

# Приклад до рефакторингу
def calculate_circle_area(radius):
    return 3.14 * radius * radius

# Приклад після рефакторингу
PI = 3.14

def refactoreed_calculate_circle_area(radius):
    return PI * radius * radius


'''Replace Method with Method Object'''

# Приклад до рефакторингу
def calculate_triangle_area(a, b, c):
    s = (a + b + c) / 2
    return (s * (s - a) * (s - b) * (s - c)) ** 0.5

def calculate_triangle_perimeter(a, b, c):
    return a + b + c

# Приклад після рефакторингу
class Triangle:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def calculate_area(self):
        s = self.calculate_perimeter() / 2
        return (s * (s - self.a) * (s - self.b) * (s - self.c)) ** 0.5

    def calculate_perimeter(self):
        return self.a + self.b + self.c

triangle = Triangle(3, 4, 5)
perimeter = triangle.calculate_perimeter()
area = triangle.calculate_area()


'''Replace Record with Data Class'''

# Приклад до рефакторингу
user = {
    "name": "John",
    "surname": "Doe",
    "email": "john.doe@example.com",
    "age": 30
}

def get_full_name(user):
    return f"{user['name']} {user['surname']}"

full_name = get_full_name(user)


# Приклад після рефакторингу
from dataclasses import dataclass

@dataclass
class User:
    name: str
    surname: str
    email: str
    age: int

    def get_full_name(self):
        return f"{self.name} {self.surname}"

user = User(name="John", surname="Doe", email="john.doe@example.com", age=30)
full_name = user.get_full_name()
