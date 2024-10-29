import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons
import matplotlib.image as mpimg
import matplotlib.patches as mpatches
import random
from random import randint

# Generer tilfeldig data for et år
def GenereateRandomYearDataList(intencity: float, seed: int = 0) -> list[int]:
    if seed != 0:
        random.seed(seed)
    centervals = [200, 150, 100, 75, 75, 75, 50, 75, 100, 150, 200, 250, 300]
    centervals = [x * intencity for x in centervals]
    nox = centervals[0]
    inc = True
    noxList = []
    for index in range(1, 365):
        if randint(1, 100) > 50:
            inc = not inc
        center = centervals[int(index / 30)]
        dx = min(5, max(0.2, nox / center))
        nox = nox + randint(1, 5) / dx if inc else nox - randint(1, 5) * dx
        nox = max(15, nox)
        noxList.append(nox)
    return noxList

# Initialiser data og parametere
days_per_quarter = 90
kron_nox_year = GenereateRandomYearDataList(intencity=1.0, seed=2)
nord_nox_year = GenereateRandomYearDataList(intencity=.3, seed=1)
days_interval = (1, days_per_quarter)
marked_point = (0, 0)

# Sett scroll_start til 1
scroll_start = 1

# Lag figur og akser
fig = plt.figure(figsize=(13, 5))
axNok = fig.add_axes((0.05, 0.1, 0.45, 0.8))
axBergen = fig.add_axes((0.5, 0.1, 0.45, 0.8))

coordinates_Nordnes = (30, 120)
coordinates_Kronstad = (1300, 1400)

# Beregn gjennomsnittsverdi
def calculate_average(data):
    return sum(data) / len(data) if data else 0

# Kalkuler NOX-verdi basert på to målestasjoner
def CalcPointValue(valN, valK):
    distNordnes = math.dist(coordinates_Nordnes, marked_point)
    distKronstad = math.dist(coordinates_Kronstad, marked_point)
    distNordnesKronstad = math.dist(coordinates_Nordnes, coordinates_Kronstad)
    val = (1 - distKronstad / (distKronstad + distNordnes)) * valK + \
          (1 - distNordnes / (distKronstad + distNordnes)) * valN
    val = val * (distNordnesKronstad / (distNordnes + distKronstad)) ** 50
    return val

# Tegner kartet med sirkler på stasjonene
def draw_circles_stations():
    circle = mpatches.Circle((90, 30), 10, color='blue')
    axBergen.add_patch(circle)
    circle = mpatches.Circle((460, 22), 10, color='purple')
    axBergen.add_patch(circle)

# Oppdater grafen med data
def plot_graph():
    axNok.cla()
    axBergen.cla()
    nord_nox = nord_nox_year[days_interval[0]-1:days_interval[1]-1]
    kron_nox = kron_nox_year[days_interval[0]-1:days_interval[1]-1]
    days = len(nord_nox)
    list_days = np.linspace(1, days, days)

    # Beregn gjennomsnitt
    nord_nox_avg = calculate_average(nord_nox)
    kron_nox_avg = calculate_average(kron_nox)

    # Tegn grafene og legg til gjennomsnittsverdiene i legend
    l1, = axNok.plot(list_days, nord_nox, 'blue', label=f"Skuteviken (Gj.snitt: {nord_nox_avg:.2f})")
    l2, = axNok.plot(list_days, kron_nox, 'purple', label=f"StoreLundgårsvann (Gj.snitt: {kron_nox_avg:.2f})")

    # Marker punkt om det finnes
    l3 = None
    if marked_point != (0, 0):
        nox_point = [CalcPointValue(nord_nox[i], kron_nox[i]) for i in range(days)]
        nox_point_avg = calculate_average(nox_point)
        l3, = axNok.plot(list_days, nox_point, 'lightgreen', label=f"Markert punkt (Gj.snitt: {nox_point_avg:.2f})")
        circle = mpatches.Circle((marked_point[0], marked_point[1]), 10, color='lightgreen')
        axBergen.add_patch(circle)

    lines = [l1, l2] if l3 is None else [l1, l2, l3]
    axNok.legend(handles=lines, loc="upper right")

    axNok.set_title("NOX verdier")
    axNok.grid(linestyle='--')
    axBergen.axis('off')
    img = mpimg.imread('NyBergen.jpg')
    img = axBergen.imshow(img)
    axBergen.set_title("Kart Bergen")
    draw_circles_stations()
    plt.draw()

# Oppdater days_interval basert på scrollbar
def update_scroll(val):
    global days_interval
    start_day = int(scroll.val)
    end_day = start_day + days_per_quarter
    days_interval = (start_day, min(end_day, 366))
    plot_graph()

# Initialiser scrollbar med korrekt øvre grense
axScroll = fig.add_axes([0.25, 0.01, 0.5, 0.03], facecolor="lightgrey")
scroll = Slider(axScroll, "Dag", 1, 365, valinit=scroll_start, valstep=1)
scroll.on_changed(update_scroll)

# Håndter klikk på kartet
def on_click(event):
    global marked_point
    if ax := event.inaxes:
        if ax == axBergen:
            marked_point = (event.xdata, event.ydata)
            plot_graph()

plt.connect('button_press_event', on_click)

plot_graph()
plt.show()
