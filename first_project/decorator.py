# Dekorator elott @ jel van:

def loud(function):
    '''Dekorátor függvény péda'''
    def wrapper():
        print('--- KEZDÉS ---')
        function()
        print('--- VÉGE ---')
    return wrapper

def greetings():
    print("Szia, Lajos!")

# "kézi" dekorálás történik:
greet_loud = loud(greetings)
greet_loud()

@loud
def greetings2(name: str):
    print("Szia, Kovács-Simon Balázs!")

greetings2()