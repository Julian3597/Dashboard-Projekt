class Duck:
    def quack(self):
        print("quack")


class Goose:
    def quack(self):
        print("whonk")


for bird in [Duck(), Goose()]:
    bird.quack()