import csv
import math

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats


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


def abline(slope, intercept, color='b'):
    """Plot a line from slope and intercept"""
    axes = plt.gca()
    x_vals = np.array(axes.get_xlim())
    y_vals = intercept + slope * x_vals
    plt.plot(x_vals, y_vals, '--', color=color, linewidth=1)


x, t = read_ball_csv('particular_balls/ball_05.csv')
plt.scatter(t, x)
plt.xlabel('time, s')
plt.ylabel('x, cm')

# Add a manually picked line, just to check linearity at the end
slope = 2.7
x0, y0 = t[-1], x[-1]
plt.plot([3, 6.06], [slope * (3 - x0) + y0, slope * (6.06 - x0) + y0], linewidth=3)

# Numerical differentiation attempt
plt.scatter(t, np.gradient(x) / np.gradient(t))
plt.xlabel('time, s')
plt.ylabel('speed, cm')

# Approximate the tail with linear regression
tail_start = int(0.8 * len(x))
model = stats.linregress(t[tail_start:], x[tail_start:])
plt.scatter(t, x)
plt.xlabel('time, s')
plt.ylabel('x, cm')
abline(model[0], model[1])


# Here starts the 10-csvs-long pipeline starts
def get_speed(x_array, time_array, start_from=0.8):
    plt.close()
    tail_start = int(start_from * len(x_array))
    time = time_array[tail_start:]
    coord = x_array[tail_start:]
    model = stats.linregress(time, coord)
    plt.scatter(time_array, x_array)
    plt.xlabel('time, s')
    plt.ylabel('coordinate, cm')
    abline(model[0], model[1])
    print(model)
    slope_uncertainty = 2 * math.sqrt(1 / len(coord) * (np.std(coord) ** 2 / np.std(time) ** 2 - model[0] ** 2))
    print(f'Slope uncertainty is {slope_uncertainty}')
    return model[0]


# get_speed(*read_ball_csv('particular_balls/ball_01.csv'))
# get_speed(*read_ball_csv('particular_balls/ball_02.csv'))
# get_speed(*read_ball_csv('particular_balls/ball_03.csv'))
# get_speed(*read_ball_csv('particular_balls/ball_04.csv'))
# get_speed(*read_ball_csv('particular_balls/ball_05.csv'))
# get_speed(*read_ball_csv('particular_balls/ball_06.csv'))
# get_speed(*read_ball_csv('particular_balls/ball_07.csv'))
# get_speed(*read_ball_csv('particular_balls/ball_08.csv'))
# get_speed(*read_ball_csv('particular_balls/ball_09.csv'))
# get_speed(*read_ball_csv('particular_balls/ball_10.csv'))

# List of 10 speeds
[get_speed(*read_ball_csv(f'particular_balls/ball_0{i}.csv')) for i in range(1, 10)].append(
    get_speed(*read_ball_csv('particular_balls/ball_10.csv')))

speeds = [4.07, 4.13, 4.09, 2.46, 2.70, 3.76, 3.88, 6.51, 6.26, 6.31]
speed_uncertainties = [0.03, 0.03, 0.03, 0.02, 0.02, 0.03, 0.02, 0.06, 0.05, 0.06]

# Balls' characteristics
diameters, masses = [], []
with open('balls.csv') as file:
    csv_reader = csv.reader(file, delimiter=',')
    next(csv_reader)
    next(csv_reader)
    for row in csv_reader:
        diameters.append(float(row[1]))
        masses.append(float(row[2]))

assert (len(masses) == 10)


# Calculate the viscosity from parameters and speed
def get_viscosity(speed, mass, diameter):
    g = 9.82
    rho = 1.12
    mass /= 1000
    diameter /= 1000
    speed /= 100
    return g * (mass - rho * np.pi * diameter ** 3 / 6) / (3 * np.pi * diameter * speed)


viscosities = []
for i in range(10):
    viscosities.append(round(get_viscosity(speeds[i], masses[i], diameters[i]), 3))
print(viscosities)

# Write the results into a final csv
with open('viscosities.csv', 'w') as file:
    file.write('speed (cm/s), speed uncertainty (cm/s), viscosity (Pa*s)\n')
    for i in range(10):
        file.write(f'{speeds[i]}, {speed_uncertainties[i]}, {viscosities[i]}\n')

# Get a fancy plot, displaying x(t) for each of the four types of balls:
# plotting_balls = [1, 4, 6, 8]
plotting_balls = range(10)

plt.close()
plt.figure(figsize=(6, 4))
plt.grid()

colors = ['#6929c4', '#1192e8', '#005d5d', '#9f1853', '#fa4d56', '#570408', '#198038', '#002d9c', '#ee538b', '#b28600']

for i in plotting_balls:
    x, t = read_ball_csv(f'particular_balls/ball_{i + 1:02d}.csv')
    plt.plot(t, x, c=colors[i], label=f'{i + 1}, m ≈ {masses[i]:.2f} г', )

plt.ylim(ymin=0)
plt.xlim(xmin=0)
plt.tick_params(labelsize=8)
plt.legend(fontsize=8)
plt.xlabel('Время, с', fontsize=8)
plt.ylabel('Глубина, см', fontsize=8)

abline(speeds[1], 1.71, 'k')
abline(speeds[4], 1.71, 'k')
abline(speeds[7], 1.71, 'k')

plt.savefig('figures/position-time.png')

# Get some statistics
np.mean(viscosities)
2 * np.std(viscosities)
