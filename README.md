# Simulátor Reakční Kinetiky

Tento projekt byl vytvořen s využitím ChatGPT pod vedením JB jako didaktický nástroj pro modelování a simulaci chemických reakcí. Projekt je napsán v Pythonu s jednoduchým GUI postaveným na Tkinteru a umožňuje simulaci různých typů chemických reakcí včetně unimolekulárních, bimolekulárních, trimolekulárních reakcí, vratných reakcí, enzymatických reakcí a dalších.

## Hlavní funkce:
- **Unimolekulární reakce**: Simulace přeměny jedné látky na jinou.
- **Bimolekulární reakce**: Reakce dvou látek vedoucí ke vzniku nové látky.
- **Trimolekulární reakce**: Kombinace tří reaktantů za vzniku produktu.
- **Vratné reakce**: Simulace vratné reakce mezi dvěma látkami.
- **Katalytické reakce**: Simulace reakcí s katalyzátorem.
- **Enzymatické reakce**: Včetně Michaelis-Menten kinetiky.
- **Inhibované reakce**: Reakce s inhibitorem snižujícím rychlost přeměny.
- **Bočné a následné reakce**: Simulace paralelních a sekvenčních reakcí.

## Struktura projektu
- `main.py`: Hlavní skript aplikace, který poskytuje GUI a zajišťuje simulaci.
- `reaction.py`: Skript pro definování reakcí (unimolekulární, bimolekulární, trimolekulární, vratné, katalytické atd.).
- `substance.py`: Skript pro definování látek a jejich vlastností.
- `simulation.py`: Skript zajišťující simulaci reakcí (např. Gillespieho algoritmus).
- `examples/`: HTML stránka s příklady a vysvětlením různých druhů simulací.

## Použití
1. **Instalace závislostí**:
    - Před spuštěním aplikace je nutné nainstalovat potřebné knihovny. Můžete použít příkaz:
    ```bash
    pip install -r requirements.txt
    ```

2. **Spuštění aplikace**:
    - Po instalaci závislostí spusťte aplikaci pomocí následujícího příkazu:
    ```bash
    python main.py
    ```

3. **Simulace reakcí**:
    - Po spuštění aplikace se otevře GUI, kde můžete nastavit počáteční množství látek, vybrat reakce a spustit simulaci. Výsledky simulace jsou zobrazeny graficky.

## Didaktické příklady
Pro lepší pochopení fungování simulátoru je v projektu složka `examples`, která obsahuje HTML stránku s konkrétními příklady simulací. Tato stránka popisuje:
- **Unimolekulární reakce** s konkrétními čísly (např. \( A \rightarrow B \)).
- **Vratné reakce** s vysvětlením rovnováhy.
- **Michaelis-Mentenovu kinetiku** včetně parametrů \( V_{max} \) a \( K_m \).
- **Bočné a následné reakce**, které ukazují, jak látky mohou reagovat souběžně nebo sekvenčně.

Každý příklad obsahuje podrobné vysvětlení, vstupní parametry a výsledky simulace (včetně screenshotů z aplikace).

### Ukázka příkladu:

```html
<h2>Unimolekulární reakce A → B</h2>
<p>V tomto příkladu simulujeme jednoduchou reakci, kde se látka A přemění na látku B s rychlostní konstantou k = 0.1.</p>
<h3>Parametry:</h3>
<ul>
  <li>Počáteční množství A: 100</li>
  <li>Rychlostní konstanta k: 0.1</li>
</ul>
<h3>Výsledek simulace:</h3>
<p>Z grafu vidíme, že množství látky A postupně klesá, zatímco množství látky B roste. Tento výsledek odpovídá exponenciálnímu rozpadu látky A podle unimolekulární kinetiky.</p>
<img src="screenshots/unimolekularni.png" alt="Unimolekulární reakce A → B">
