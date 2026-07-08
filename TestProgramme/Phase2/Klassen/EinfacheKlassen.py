class TestClass:
    x = 42

print(TestClass.x) # 42
TestClass.x -= 24
print(TestClass.x) # 18

instance1 = TestClass()
# Spiegelt Änderungen zu TestClass
print(instance1.x) # 18

# Auch nach instanzierung
TestClass.x = 42
print(instance1.x) # 42

# Aber nicht umgekehrt
instance1.x = 1
print(instance1.x) # 1
print(TestClass.x) # 42

# Nachdem dieser wert mal berührt wurde, spiegelt es nicht mehr.
TestClass.x = 43
print(instance1.x) # 1 (noch immer)
