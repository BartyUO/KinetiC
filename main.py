# main.py

import matplotlib
matplotlib.use('TkAgg')

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from substance import Substance
from reaction import (
    Reaction, UnimolecularReaction, BimolecularReaction,
    TrimolecularReaction, ReversibleReaction, CatalyticReaction,
    EnzymaticReaction, MichaelisMentenReaction, AutocatalyticReaction,
    InhibitoryReaction
)
from simulation import gillespie_simulation
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def main():
    root = tk.Tk()
    root.title("Simulace reakční kinetiky")
    root.geometry("1200x800")

    # Rámec pro vstupní parametry
    input_frame = ttk.Frame(root)
    input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    # Definice látek
    substance_info = []

    # Aktualizované názvy látek
    initial_substances = ['A', 'B', 'C', 'D', 'E', 'F', 'S', 'P', 'E', 'I']  # S = Substrát, P = Produkt, E = Enzym, I = Inhibitor
    for name in initial_substances:
        substance_info.append({'name': name, 'label': name, 'default': '0'})

    # Rámec pro látky
    substance_frame = ttk.LabelFrame(input_frame, text="Látky")
    substance_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

    # Funkce pro aktualizaci vstupních polí látek
    def update_substance_entries():
        for widget in substance_frame.winfo_children():
            widget.destroy()
        row = 0
        ttk.Label(substance_frame, text="Počáteční množství látek:").grid(row=row, column=0, columnspan=2)
        row += 1
        for info in substance_info:
            ttk.Label(substance_frame, text=f"{info['label']}:").grid(row=row, column=0, sticky=tk.E)
            entry = ttk.Entry(substance_frame)
            entry.insert(0, info['default'])
            entry.grid(row=row, column=1)
            info['entry'] = entry
            row += 1

    update_substance_entries()

    # Definice předdefinovaných reakcí, včetně bočných a následných
    predefined_reactions = [
        {
            'label': 'Unimolekulární rozklad A → B',
            'description': 'Jednoduchá unimolekulární reakce, kde se látka A přemění na látku B.',
            'type': 'Unimolecular',
            'reactants': {'A': 1},
            'products': {'B': 1},
            'default_k': '0.1'
        },
        {
            'label': 'Bimolekulární reakce A + B → C',
            'description': 'Bimolekulární reakce, kde se látky A a B spojí za vzniku látky C.',
            'type': 'Bimolecular',
            'reactants': {'A': 1, 'B': 1},
            'products': {'C': 1},
            'default_k': '0.01'
        },
        {
            'label': 'Následná reakce B → C',
            'description': 'Následná reakce, kde látka B se přemění na látku C.',
            'type': 'Unimolecular',
            'reactants': {'B': 1},
            'products': {'C': 1},
            'default_k': '0.05'
        },
        {
            'label': 'Bočná reakce A → D',
            'description': 'Bočná reakce, kde látka A se přemění na D.',
            'type': 'Unimolecular',
            'reactants': {'A': 1},
            'products': {'D': 1},
            'default_k': '0.03'
        },
        {
            'label': 'Vratná reakce A ⇌ B',
            'description': 'Vratná reakce mezi látkami A a B.',
            'type': 'Reversible',
            'reactants': {'A': 1},
            'products': {'B': 1},
            'default_k_forward': '0.05',
            'default_k_reverse': '0.02'
        },
        {
            'label': 'Katalytická reakce A → B (katalyzátor E)',
            'description': 'Reakce, kde katalyzátor E urychluje přeměnu látky A na B.',
            'type': 'Catalytic',
            'reactants': {'A': 1},
            'products': {'B': 1},
            'catalyst': 'E',
            'default_k': '0.1'
        },
        {
            'label': 'Autokatalytická reakce A + B → 2B',
            'description': 'Reakce, kde produkt B katalyzuje svou vlastní tvorbu.',
            'type': 'Autocatalytic',
            'reactants': {'A': 1, 'B': 1},
            'products': {'B': 2},
            'default_k': '0.02'
        },
        {
            'label': 'Enzymatická reakce S + E → P + E',
            'description': 'Enzymatická reakce, kde enzym E katalyzuje přeměnu substrátu S na produkt P.',
            'type': 'Enzymatic',
            'substrate': 'S',
            'product': 'P',
            'enzyme': 'E',
            'default_k': '0.05'
        },
        {
            'label': 'Michaelis-Menten kinetika S → P',
            'description': 'Enzymatická reakce podle Michaelis-Mentenovy kinetiky.',
            'type': 'MichaelisMenten',
            'substrate': 'S',
            'product': 'P',
            'enzyme': 'E',
            'default_vmax': '1.0',
            'default_km': '10'
        },
        {
            'label': 'Inhibovaná reakce A → B (inhibitor I)',
            'description': 'Reakce, kde inhibitor I snižuje rychlost přeměny látky A na B.',
            'type': 'Inhibitory',
            'reactants': {'A': 1},
            'products': {'B': 1},
            'inhibitor': 'I',
            'default_k': '0.1'
        }
    ]

    # Rámec pro reakce
    reaction_frame = ttk.LabelFrame(input_frame, text="Reakce")
    reaction_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

    selected_reactions = []

    # Funkce pro vytvoření tooltipu
    def create_tooltip(widget, text):
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        label = ttk.Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1, wraplength=300)
        label.pack()

        def enter(event):
            tooltip.deiconify()
            x = widget.winfo_rootx() + 20
            y = widget.winfo_rooty() + 20
            tooltip.geometry(f"+{x}+{y}")

        def leave(event):
            tooltip.withdraw()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    # Funkce pro aktualizaci vstupních polí reakcí
    def update_reaction_entries():
        for widget in reaction_frame.winfo_children():
            widget.destroy()
        ttk.Label(reaction_frame, text="Vyberte reakce pro simulaci:").grid(row=0, column=0, columnspan=5)
        row = 1
        for info in predefined_reactions:  # Opraveno, odstraněn idx
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(reaction_frame, text=info['label'], variable=var)
            chk.grid(row=row, column=0, sticky=tk.W)
            info['selected'] = var

            # Tooltip s popisem reakce
            create_tooltip(chk, info['description'])

            if info['type'] == 'Reversible':
                ttk.Label(reaction_frame, text="k_forward:").grid(row=row, column=1)
                entry_k_forward = ttk.Entry(reaction_frame, width=7)
                entry_k_forward.insert(0, info['default_k_forward'])
                entry_k_forward.grid(row=row, column=2)
                info['entry_k_forward'] = entry_k_forward

                ttk.Label(reaction_frame, text="k_reverse:").grid(row=row, column=3)
                entry_k_reverse = ttk.Entry(reaction_frame, width=7)
                entry_k_reverse.insert(0, info['default_k_reverse'])
                entry_k_reverse.grid(row=row, column=4)
                info['entry_k_reverse'] = entry_k_reverse
            elif info['type'] == 'MichaelisMenten':
                ttk.Label(reaction_frame, text="Vmax:").grid(row=row, column=1)
                entry_vmax = ttk.Entry(reaction_frame, width=7)
                entry_vmax.insert(0, info['default_vmax'])
                entry_vmax.grid(row=row, column=2)
                info['entry_vmax'] = entry_vmax

                ttk.Label(reaction_frame, text="Km:").grid(row=row, column=3)
                entry_km = ttk.Entry(reaction_frame, width=7)
                entry_km.insert(0, info['default_km'])
                entry_km.grid(row=row, column=4)
                info['entry_km'] = entry_km

                # Přidání vysvětlujícího popisku
                ttk.Label(reaction_frame, text="(S = Substrát, P = Produkt, E = Enzym)").grid(row=row+1, column=0, columnspan=5)
                row += 1

                # Přidání tooltipů
                create_tooltip(entry_vmax, "Vmax: Maximální rychlost reakce při plné saturaci enzymu substrátem.")
                create_tooltip(entry_km, "Km: Michaelisova konstanta, koncentrace substrátu při polovině maximální rychlosti reakce.")
            elif info['type'] == 'Catalytic':
                ttk.Label(reaction_frame, text="k:").grid(row=row, column=1)
                entry_k = ttk.Entry(reaction_frame, width=7)
                entry_k.insert(0, info['default_k'])
                entry_k.grid(row=row, column=2)
                info['entry_k'] = entry_k

                ttk.Label(reaction_frame, text=f"Katalyzátor: {info['catalyst']}").grid(row=row, column=3, columnspan=2)
                # Přidání tooltipu
                create_tooltip(chk, f"{info['description']} Katalyzátor: {info['catalyst']}")
            elif info['type'] == 'Enzymatic':
                ttk.Label(reaction_frame, text="k:").grid(row=row, column=1)
                entry_k = ttk.Entry(reaction_frame, width=7)
                entry_k.insert(0, info['default_k'])
                entry_k.grid(row=row, column=2)
                info['entry_k'] = entry_k

                # Přidání vysvětlujícího popisku
                ttk.Label(reaction_frame, text="(S = Substrát, P = Produkt, E = Enzym)").grid(row=row+1, column=0, columnspan=5)
                row += 1

                # Přidání tooltipu
                create_tooltip(chk, info['description'])
            else:
                ttk.Label(reaction_frame, text="k:").grid(row=row, column=1)
                entry_k = ttk.Entry(reaction_frame, width=7)
                entry_k.insert(0, info.get('default_k', '0.1'))
                entry_k.grid(row=row, column=2)
                info['entry_k'] = entry_k

                # Přidání tooltipu
                create_tooltip(entry_k, "k: Rychlostní konstanta reakce.")
            row += 1

    update_reaction_entries()

    # Parametry simulace
    params_frame = ttk.LabelFrame(input_frame, text="Parametry simulace")
    params_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

    ttk.Label(params_frame, text="Maximální čas simulace:").grid(row=0, column=0, sticky=tk.E)
    entry_t_max = ttk.Entry(params_frame)
    entry_t_max.insert(0, "100")
    entry_t_max.grid(row=0, column=1)

    # Tlačítko pro spuštění simulace
    simulate_button = ttk.Button(input_frame, text="Spustit simulaci", command=lambda: run_simulation())
    simulate_button.grid(row=1, column=0, columnspan=3, pady=10)

    # Rámec pro graf
    plot_frame = ttk.Frame(root)
    plot_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def run_simulation():
        try:
            # Vytvoření látek
            substances = {}
            for info in substance_info:
                amount = int(info['entry'].get())
                substances[info['name']] = Substance(info['name'], amount)

            # Doba simulace
            t_max = float(entry_t_max.get())

            # Vytvoření reakcí
            reactions = []
            for info in predefined_reactions:
                if info['selected'].get():
                    reaction_type = info['type']
                    if reaction_type == 'Unimolecular':
                        reactants = {substances[name]: coeff for name, coeff in info['reactants'].items()}
                        products = {substances[name]: coeff for name, coeff in info['products'].items()}
                        k = float(info['entry_k'].get())
                        reaction = UnimolecularReaction(reactants, products, k)
                    elif reaction_type == 'Bimolecular':
                        reactants = {substances[name]: coeff for name, coeff in info['reactants'].items()}
                        products = {substances[name]: coeff for name, coeff in info['products'].items()}
                        k = float(info['entry_k'].get())
                        reaction = BimolecularReaction(reactants, products, k)
                    elif reaction_type == 'Trimolecular':
                        reactants = {substances[name]: coeff for name, coeff in info['reactants'].items()}
                        products = {substances[name]: coeff for name, coeff in info['products'].items()}
                        k = float(info['entry_k'].get())
                        reaction = TrimolecularReaction(reactants, products, k)
                    elif reaction_type == 'Reversible':
                        reactants = {substances[name]: coeff for name, coeff in info['reactants'].items()}
                        products = {substances[name]: coeff for name, coeff in info['products'].items()}
                        k_forward = float(info['entry_k_forward'].get())
                        k_reverse = float(info['entry_k_reverse'].get())
                        reaction = ReversibleReaction(reactants, products, k_forward, k_reverse)
                    elif reaction_type == 'Catalytic':
                        reactants = {substances[name]: coeff for name, coeff in info['reactants'].items()}
                        products = {substances[name]: coeff for name, coeff in info['products'].items()}
                        catalyst = substances[info['catalyst']]
                        k = float(info['entry_k'].get())
                        reaction = CatalyticReaction(reactants, products, catalyst, k)
                    elif reaction_type == 'Autocatalytic':
                        reactants = {substances[name]: coeff for name, coeff in info['reactants'].items()}
                        products = {substances[name]: coeff for name, coeff in info['products'].items()}
                        k = float(info['entry_k'].get())
                        reaction = AutocatalyticReaction(reactants, products, k)
                    elif reaction_type == 'Enzymatic':
                        substrate = substances[info['substrate']]
                        product = substances[info['product']]
                        enzyme = substances[info['enzyme']]
                        k = float(info['entry_k'].get())
                        reaction = EnzymaticReaction(substrate, product, enzyme, k)
                    elif reaction_type == 'MichaelisMenten':
                        substrate = substances[info['substrate']]
                        product = substances[info['product']]
                        vmax = float(info['entry_vmax'].get())
                        km = float(info['entry_km'].get())
                        reaction = MichaelisMentenReaction(substrate, product, enzyme, vmax, km)
                    elif reaction_type == 'Inhibitory':
                        reactants = {substances[name]: coeff for name, coeff in info['reactants'].items()}
                        products = {substances[name]: coeff for name, coeff in info['products'].items()}
                        inhibitor = substances[info['inhibitor']]
                        k = float(info['entry_k'].get())
                        reaction = InhibitoryReaction(reactants, products, inhibitor, k)
                    else:
                        messagebox.showerror("Chyba", f"Neznámý typ reakce: {reaction_type}")
                        return
                    reactions.append(reaction)

            if not reactions:
                messagebox.showwarning("Upozornění", "Nevybrali jste žádné reakce pro simulaci.")
                return

        except Exception as e:
            messagebox.showerror("Chyba", str(e))
            return

        # Spuštění simulace
        times, history = gillespie_simulation(substances, reactions, t_max)

        # Zobrazení výsledků
        plot_results(times, history)

    def plot_results(times, history):
        # Vyčištění starého grafu
        for widget in plot_frame.winfo_children():
            widget.destroy()

        # Vytvoření nového grafu
        fig, ax = plt.subplots(figsize=(8, 4))

        for substance_name, amounts in history.items():
            ax.plot(times, amounts, label=substance_name)

        ax.set_xlabel('Čas')
        ax.set_ylabel('Množství molekul')
        ax.legend()
        ax.set_title('Simulace reakční kinetiky')

        # Vložení grafu do Tkinter okna
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    root.mainloop()

if __name__ == '__main__':
    main()
