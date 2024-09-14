# substance.py

class Substance:
    def __init__(self, name, amount):
        self.name = name          # Název látky
        self.amount = amount      # Množství látky (počet molekul)

    def __repr__(self):
        return f"{self.name}: {self.amount}"
