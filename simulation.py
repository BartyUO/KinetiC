# simulation.py

import numpy as np
from reaction import Reaction, ReversibleReaction

def gillespie_simulation(substances, reactions, t_max):
    time = 0
    times = [time]
    history = {substance.name: [substance.amount] for substance in substances.values()}

    while time < t_max:
        propensities = []
        for reaction in reactions:
            prop = reaction.propensity()
            propensities.append(prop)

        total_propensity = sum(propensities)

        if total_propensity == 0:
            break

        # Generování času do další reakce
        tau = np.random.exponential(1 / total_propensity)
        time += tau

        # Výběr reakce, která proběhne
        probabilities = [p / total_propensity for p in propensities]
        reaction_index = np.random.choice(len(reactions), p=probabilities)
        reaction = reactions[reaction_index]

        # Aktualizace látek
        reaction.update_substances()

        times.append(time)
        for substance in substances.values():
            history[substance.name].append(substance.amount)

    return times, history
