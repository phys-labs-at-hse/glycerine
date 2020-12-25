import math

g = 9.82
rho = 1.12
eta = 0.5
mass = 3.9e-4
diameter = 4e-3
print(f'Test: density is {mass / (math.pi * diameter**3 / 6)} kg/m^3')

# initial speed
h = 0.05
vx0 = math.sqrt(2*g*h)

# stable speed
c = (mass*g - (1/6)*rho*g*math.pi*(diameter**3)) / (3*math.pi*eta*diameter)
print(f'c: {c} m/s')

# exponent coefficient
k = 3*math.pi*eta*diameter / mass
print(f'k: {k} 1/s')

# time falling until speed stabilizes
tau = 1/k * math.log((vx0 - c) / (0.01*c))
print(f'tau: {tau} s')
