from dataclasses import dataclass


@dataclass
class Parent:
    name: str
    age: int

@dataclass
class Child(Parent):
    secretthirdthing: str

newchild = Child("a", 2, "b")
print(newchild.age)
print(newchild.secretthirdthing)

parent = Parent("parentname", 33)
print(parent)

