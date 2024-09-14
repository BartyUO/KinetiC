# reaction.py

from abc import ABC, abstractmethod
import numpy as np

class Reaction(ABC):
    def __init__(self, reactants, products):
        """
        Inicializuje obecnou reakci.

        Parameters:
        - reactants: dict {Substance: koeficient}
        - products: dict {Substance: koeficient}
        """
        self.reactants = reactants
        self.products = products

    @abstractmethod
    def propensity(self):
        """
        Abstraktní metoda pro výpočet propence reakce.
        Musí být implementována v podtřídách.
        """
        pass

    @abstractmethod
    def update_substances(self):
        """
        Aktualizuje množství látek po proběhnutí reakce.
        Musí být implementována v podtřídách.
        """
        pass

class UnimolecularReaction(Reaction):
    def __init__(self, reactants, products, rate_constant):
        super().__init__(reactants, products)
        self.k = rate_constant

    def propensity(self):
        prop = self.k
        for substance, stoich in self.reactants.items():
            if substance.amount < stoich:
                return 0
            # Kombinatorický výpočet pro stechiometrii
            for i in range(stoich):
                prop *= (substance.amount - i)
        return prop

    def update_substances(self):
        for substance, stoich in self.reactants.items():
            substance.amount -= stoich
        for substance, stoich in self.products.items():
            substance.amount += stoich

class BimolecularReaction(Reaction):
    def __init__(self, reactants, products, rate_constant):
        super().__init__(reactants, products)
        self.k = rate_constant

    def propensity(self):
        prop = self.k
        reactants_list = list(self.reactants.items())
        if len(reactants_list) != 2:
            raise ValueError("Bimolekulární reakce musí mít přesně dva reaktanty.")
        (sub1, stoich1), (sub2, stoich2) = reactants_list
        if sub1.amount < stoich1 or sub2.amount < stoich2:
            return 0
        if sub1 == sub2:
            # Reakce 2A -> produkty
            prop *= sub1.amount * (sub1.amount - 1) / 2
        else:
            prop *= sub1.amount * sub2.amount
        return prop

    def update_substances(self):
        for substance, stoich in self.reactants.items():
            substance.amount -= stoich
        for substance, stoich in self.products.items():
            substance.amount += stoich

class TrimolecularReaction(Reaction):
    def __init__(self, reactants, products, rate_constant):
        super().__init__(reactants, products)
        self.k = rate_constant

    def propensity(self):
        prop = self.k
        reactants_list = list(self.reactants.items())
        if len(reactants_list) != 3:
            raise ValueError("Trimolekulární reakce musí mít přesně tři reaktanty.")
        amounts = []
        for sub, stoich in reactants_list:
            if sub.amount < stoich:
                return 0
            amounts.extend([sub.amount] * stoich)
        prop *= np.prod(amounts)
        return prop

    def update_substances(self):
        for substance, stoich in self.reactants.items():
            substance.amount -= stoich
        for substance, stoich in self.products.items():
            substance.amount += stoich

class ReversibleReaction(Reaction):
    def __init__(self, reactants, products, k_forward, k_reverse):
        super().__init__(reactants, products)
        self.k_forward = k_forward
        self.k_reverse = k_reverse

    def propensity_forward(self):
        prop = self.k_forward
        for substance, stoich in self.reactants.items():
            if substance.amount < stoich:
                return 0
            for i in range(stoich):
                prop *= (substance.amount - i)
        return prop

    def propensity_reverse(self):
        prop = self.k_reverse
        for substance, stoich in self.products.items():
            if substance.amount < stoich:
                return 0
            for i in range(stoich):
                prop *= (substance.amount - i)
        return prop

    def propensity(self):
        return self.propensity_forward() + self.propensity_reverse()

    def update_substances(self):
        prop_forward = self.propensity_forward()
        prop_reverse = self.propensity_reverse()
        total_propensity = prop_forward + prop_reverse

        if total_propensity == 0:
            return  # Žádná reakce nemůže proběhnout

        rand = np.random.rand()
        if rand < prop_forward / total_propensity:
            # Forward reakce
            for substance, stoich in self.reactants.items():
                substance.amount -= stoich
            for substance, stoich in self.products.items():
                substance.amount += stoich
        else:
            # Reverse reakce
            for substance, stoich in self.products.items():
                substance.amount -= stoich
            for substance, stoich in self.reactants.items():
                substance.amount += stoich

class CatalyticReaction(Reaction):
    def __init__(self, reactants, products, catalyst, rate_constant):
        super().__init__(reactants, products)
        self.catalyst = catalyst
        self.k = rate_constant

    def propensity(self):
        prop = self.k * self.catalyst.amount
        for substance, stoich in self.reactants.items():
            if substance.amount < stoich:
                return 0
            for i in range(stoich):
                prop *= (substance.amount - i)
        return prop

    def update_substances(self):
        for substance, stoich in self.reactants.items():
            substance.amount -= stoich
        for substance, stoich in self.products.items():
            substance.amount += stoich

class EnzymaticReaction(Reaction):
    def __init__(self, substrate, product, enzyme, rate_constant):
        reactants = {substrate: 1, enzyme: 1}
        products = {product: 1, enzyme: 1}
        super().__init__(reactants, products)
        self.k = rate_constant
        self.substrate = substrate
        self.product = product
        self.enzyme = enzyme

    def propensity(self):
        if self.substrate.amount < 1 or self.enzyme.amount < 1:
            return 0
        prop = self.k * self.substrate.amount * self.enzyme.amount
        return prop

    def update_substances(self):
        self.substrate.amount -= 1
        self.product.amount += 1
        # Enzym je katalyzátor, jeho množství se nemění

class MichaelisMentenReaction(Reaction):
    def __init__(self, substrate, product, enzyme, vmax, km):
        self.substrate = substrate
        self.product = product
        self.enzyme = enzyme
        self.vmax = vmax
        self.km = km

    def propensity(self):
        if self.substrate.amount < 1:
            return 0
        prop = self.vmax * self.substrate.amount / (self.km + self.substrate.amount)
        return prop

    def update_substances(self):
        self.substrate.amount -= 1
        self.product.amount += 1
        # Enzym je zahrnut v parametru vmax

class AutocatalyticReaction(Reaction):
    def __init__(self, reactants, products, rate_constant):
        super().__init__(reactants, products)
        self.k = rate_constant

    def propensity(self):
        # Předpokládáme reakci typu A + B -> 2B
        # kde B je katalyzátor i produkt
        if len(self.reactants) != 2 or len(self.products) != 1:
            raise ValueError("Autokatalytická reakce musí mít 2 reaktanty a 1 produkt.")
        sub_a, sub_b = self.reactants.keys()
        if sub_a.amount < 1 or sub_b.amount < 1:
            return 0
        prop = self.k * sub_a.amount * sub_b.amount
        return prop

    def update_substances(self):
        # A + B -> 2B
        sub_a, sub_b = self.reactants.keys()
        sub_a.amount -= 1
        sub_b.amount -= 1
        # Produkty
        sub_b.amount += 2  # B se obnoví a vytvoří se další B

class InhibitoryReaction(Reaction):
    def __init__(self, reactants, products, inhibitor, rate_constant):
        super().__init__(reactants, products)
        self.inhibitor = inhibitor
        self.k = rate_constant

    def propensity(self):
        prop = self.k
        for substance, stoich in self.reactants.items():
            if substance.amount < stoich:
                return 0
            prop *= substance.amount
        prop /= (1 + self.inhibitor.amount)
        return prop

    def update_substances(self):
        for substance, stoich in self.reactants.items():
            substance.amount -= stoich
        for substance, stoich in self.products.items():
            substance.amount += stoich
