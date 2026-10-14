import random

def get_number(start: int, end: int) -> float:
    """Visszaad egy véletlen számot!"""
    return round(random.randint(start,end-1)+random.random(), 3)
# for (int i=0; i < 30; i++) {}
for n in range(2):
    n = get_number(3, 7)
    print(f"szám: {n}")

# Generátor függvény:
def gen_function(stop: int) -> int:
    i = 0
    while i < stop:
        yield i
        i += 1

gen = gen_function(6)

for i in gen:
    print(i)

print(next(gen))