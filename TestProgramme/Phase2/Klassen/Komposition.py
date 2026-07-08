from dataclasses import dataclass, field


@dataclass
class Leaf:
    color: str
    age: float
    def __del__(self):
        print(f"Leaf {self} has died")

@dataclass
class Tree:
    leaves: list[Leaf] = field(default_factory=list)

    # Tree kontrolliert Leaf lifecycle
    def new_leaf(self, color: str, age: float):
        self.leaves.append(Leaf(color, age))

    def del_leaf(self, target_leaf: Leaf):
        self.leaves.remove(target_leaf)

    def __del__(self):
        print(f"Tree {self} has died")



newTree = Tree()
newTree.new_leaf("green", 1.012)
newTree.new_leaf("red", 10.999)
newTree.del_leaf(newTree.leaves[1])
for leaf in newTree.leaves:
    print(leaf.color, leaf.age)