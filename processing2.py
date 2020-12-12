# In this file, I calculate viscosity as described in the last
# section of `theory.tex`: assume the the speed is already stable,
# numerically differentiate, then calculate the viscosity at a
# specific coordinate for each ball. Apply moving average to get rid
# of the noise.
# Most convenience functions are taken from `processing.py`.


import csv

import matplotlib.pyplot as plt
import numpy as np

import processing


def read_ball_csv(filepath):
    """Read a csvfile and return 2 np arrays: x(t) and t"""
    with open(filepath) as file:
        x = []
        t = []
        csv_reader = csv.reader(file, delimiter=',')
        for row in csv_reader:
            x.append(float(row[0]))
            t.append(float(row[1]))
    return (np.array(x), np.array(t))


def get_viscosity(speed, mass, diameter):
    """Calculate the viscosity from parameters and speed"""
    g = 9.82
    rho = 1.12
    mass /= 1000
    diameter /= 1000
    speed /= 100
    return g * (mass - rho * np.pi * diameter ** 3 / 6) / (3 * np.pi * diameter * speed)


def moving_average(x, w=3):
    """Calculate moving average of x using w neighbours"""
    return np.convolve(x, np.ones(w), 'valid') / w


def csv_path(n):
    return f'particular_balls/ball_{n + 1:02d}.csv'


# Balls' characteristics
diameters, masses = [], []
with open('balls.csv') as file:
    csv_reader = csv.reader(file, delimiter=',')
    next(csv_reader)
    next(csv_reader)
    for row in csv_reader:
        diameters.append(float(row[1]))
        masses.append(float(row[2]))

# Get a list of viscosity(height) data merged across the balls
all_viscosities, all_x = [], []
for i in range(10):
    x, t = read_ball_csv(csv_path(i))
    all_x.extend(x)
    speeds = np.gradient(x, t)
    viscosities = list(map(lambda speed: get_viscosity(speed, masses[i], diameters[i]), speeds))
    all_viscosities.extend(viscosities)
all_viscosities = np.array(all_viscosities)
all_x = np.array(all_x)

# Sort the two arrays by x
indices = all_x.argsort()
all_x = all_x[indices]
all_viscosities = all_viscosities[indices]

# Get rid of the duplicates
indices = np.argwhere(np.diff(all_x) == 0)  # 98, 1025
all_x = np.delete(all_x, indices)
all_viscosities = np.delete(all_viscosities, indices)

# Plot with a moving-averaged line
w = 30
plt.scatter(all_x, all_viscosities)
plt.scatter(all_x[int(w / 2 - 1):int(-w / 2)], moving_average(all_viscosities, w))

# Remove the noise due to boundary effects in multiple places
indices = (all_x > 0.5) * (all_x < 17.5)
all_x = all_x[indices]
all_viscosities = all_viscosities[indices]

indices = (all_viscosities < 2.25) * (all_viscosities > 1.1)
all_x = all_x[indices]
all_viscosities = all_viscosities[indices]

# Convert x from 'distance passed since appearance in the video'
# into 'distance from the bottom', using `info.txt`
# Invert and add distance from the bottom till the notch 250
all_x = (19.4 + 20 / (250 - 20) * 19.4) - all_x

# Plot with a moving-averaged line, once again, with style
w = 120
all_x_averaged = all_x[int(w / 2 - 1):int(-w / 2)]
all_viscosities_averaged = moving_average(all_viscosities, w)

plt.close()
plt.scatter(all_x, all_viscosities)
plt.scatter(all_x_averaged, all_viscosities_averaged)
plt.grid()
plt.xlabel('Расстояние до дна, см', fontsize=18)
plt.ylabel('Вязкость, Па·с', fontsize=18)

# Save the viscosity data to csv tables to be attached to the report
with open('viscosity_at_height.csv', 'w') as file:
    file.write('height (cm), viscosity (Pa*s)\n')
    for i in range(len(all_x)):
        file.write(f'{all_x[i]}, {all_viscosities[i]}\n')

# Save the average data
with open('viscosity_at_height_averaged.csv', 'w') as file:
    file.write('height (cm), viscosity (Pa*s)\n')
    for i in range(len(all_x_averaged)):
        file.write(f'{all_x_averaged[i]}, {all_viscosities_averaged[i]}\n')

# Roughly check for bias in balls' diameters.
# The plot above didn't distinguish between viscosities calculated from
# different balls, but it's interesting to see if viscosity is systematically
# different for some balls. That would mean an error in diameter.
plt.plot()
plt.figure(figsize=(6, 4))
plt.grid()
plt.ylim(1.1, 1.8)
for i in range(10):
    x, t = read_ball_csv(csv_path(i))
    speeds = np.gradient(x, t)
    viscosities = map(lambda speed: get_viscosity(speed, masses[i], diameters[i]), speeds)
    viscosities = np.array(list(viscosities))
    w = 20
    x = x[int(w / 2 - 1):int(-w / 2)]
    viscosities = moving_average(viscosities, w)
    plt.plot(x, viscosities, label=f'{i + 1}', color=processing.colors[i])

plt.tick_params(labelsize=8)
plt.legend(fontsize=8)
plt.xlabel('Пройденное расстояние, см', fontsize=8)
plt.ylabel('Вязкость, Па·с', fontsize=8)
plt.savefig('figures/viscosity-position.png')

# There clearly is a bias; let's adjust the diameters according to the known
# density of lead: 11300 kg/m^3.

# Print densities with measured diameters
for i in range(10):
    volume = np.pi * (diameters[i] / 1000) ** 3 / 6
    print((masses[i] / 1000) / volume)
# Steel is OK, while lead is often incorrect

adjusted_diameters = diameters.copy()
for i in range(3, 10):
    # Adjusted diameter is in millimeters, and mass is in grams
    adjusted_diameters[i] = ((masses[i] / 1000 / 11300) * 6 / np.pi) ** (1 / 3) * 1000

plt.close()
plt.plot()
plt.ylim(1.1, 1.8)
for i in range(10):
    x, t = read_ball_csv(csv_path(i))
    speeds = np.gradient(x, t)
    viscosities = map(lambda speed: get_viscosity(speed, masses[i], adjusted_diameters[i]), speeds)
    viscosities = np.array(list(viscosities))
    w = 20
    x = x[int(w / 2 - 1):int(-w / 2)]
    viscosities = moving_average(viscosities, w)
    if i < 3:
        plt.scatter(x, viscosities, label=i + 1, color='gray')
    else:
        plt.scatter(x, viscosities, label=i + 1)
    plt.legend()
plt.title('With adjusted diameters')
plt.grid()
plt.xlabel('Пройденное расстояние, см', fontsize=18)
plt.ylabel('Вязкость, Па·с', fontsize=18)
