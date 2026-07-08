from dataclasses import dataclass

@dataclass
class Bean:
    roast: str
    def __del__(self):
        print(f"Bean {self} has died")

@dataclass
class BeanHolder():
    beans: list[Bean]
    def __del__(self):
        print(f"Holder {self} has died")

bean1 = Bean("dark")
bean2 = Bean("dark")
bean3 = Bean("light")

holder = BeanHolder([bean1, bean2, bean3])
print(holder.beans)