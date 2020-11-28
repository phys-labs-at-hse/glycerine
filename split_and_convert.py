common_coords, common_nframes = [], []

# Read the data into two lists initialized above
with open('video_raw_data.csv') as datafile:
    for line in datafile:
        coord, nframe = map(float, line.strip().split(','))
        common_coords.append(coord)
        common_nframes.append(int(nframe))

# Split the data into ten parts, one for each ball
coords, nframes = [], []
current_balls_coords = [common_coords[0]]
current_balls_nframes = [common_nframes[0]]
for i in range(1, len(common_coords)):
    if common_coords[i - 1] - common_coords[i] > 400 or i == len(common_coords) - 1:
        coords.append(current_balls_coords)
        nframes.append(current_balls_nframes)

        current_balls_coords = []
        current_balls_nframes = []

    current_balls_coords.append(common_coords[i])
    current_balls_nframes.append(common_nframes[i])

# Check that I got it right, there were exactly 10 balls
assert len(coords) == len(nframes) == 10

# Subtract the initial frame number and convert frame number into seconds
fps = 30
for i in range(len(nframes)):
    nframes[i] = list(map(lambda x: (x - nframes[i][0]) / fps, nframes[i]))

# Convert pixels into meters; see `info.txt`, comments in `main_script.py`,
# and the original video for info on the scaler value.
scaler = ((250 - 30) / 580) * (19.4 / (250 - 20))
for i in range(len(coords)):
    coords[i] = list(map(lambda x: x * scaler, coords[i]))

# Write each ball's data into separate file
for i in range(10):
    with open(f'particular_balls/ball_{str(i + 1).zfill(2)}.csv', 'a') as file:
        for j in range(len(coords[i])):
            file.write(f'{coords[i][j]},{nframes[i][j]}\n')
