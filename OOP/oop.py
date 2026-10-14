class Product:
    '''Termék a webáruházban'''
    def __init__(self, name: str, price: float, stock: int):
        # Az init a konstruktor
        # Attribútumok (mezők, tulajdonságok)
        self.name = name
        self._price = price #private
        self.__stock = stock #more private

    @property # Mint C#-ben a get-property -> kintről egyszerű mezőnek látszik, bent viszont egy metódus! Ellenőrzött mezőelérés.
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, new_price: float) -> float:
        '''Ellenőrzött értékadás'''
        if new_price < 0:
            raise ValueError("Az ár nem lehet negatív")
        self._price = new_price

    def introduction(self) -> str:
        '''Egy metódus (osztályban deklarált függvény vagy eljárás (képesség))'''
        return f"{self.name} - {self._price} Ft - {self.__stock} db"

    def is_available(self) -> bool:
        return self.__stock > 0

    def discounted_price(self) -> float:
        return self.price

class Book(Product):
    def __init__(self, name, price, stock, author: str, page_count: int):
        super().__init__(name, price, stock)
        self.author = author
        self.page_count = page_count

    def introduction(self) -> str:
        basic = super().introduction()
        return f"{basic} | {self.author} - {self.page_count} oldal"

    def discounted_price(self):
        '''Teljes felülírása a szülő metódusnak'''
        if self.price > 4000:
            return (self.price / 2)
        return self.price 


# Példányosítás (Az objektum létrehozása a konstruktor révén.)
book = Product("Egri csillagok", 4870, 13)
phone = Product("Iphone Duo", 959000, 342)
print(f"A private price elérése property-vel: {book.price} Ft")
book._price = 231
print(book.introduction())
print(phone.introduction())

b = Book("Egri csillagok", 4990, 23, "Gárdonyi Géza", 467)
print(b.introduction())
print(b.discounted_price())