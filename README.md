In this educational lab project we aim to determine the viscosity of glycerine.

Essence of the python files:
- `main_script.py` convers a video recording `vid.mp4` (since it's 100MB, I had to make git ignore it) into `video_raw_data.csv` --- table with two columns: coordinate and frame number
- `split_and_convert.py` cleans the table and splits it into ten tables `particular_balls/*`, one for each ball, converting the numbers into SI units.
- `processing.py` analyzes the data, calculates the viscosity
