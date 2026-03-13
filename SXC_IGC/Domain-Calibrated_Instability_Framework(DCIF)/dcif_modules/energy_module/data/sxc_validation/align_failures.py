import pandas as pd

load = pd.read_csv("load_clean.csv")
failures = pd.read_csv("failures_clean.csv")

load['UTC'] = pd.to_datetime(load['UTC'])
failures['Start'] = pd.to_datetime(failures['Start'])

# Initialize the binary target: 1 = System in Fracture/Pre-Fracture
load['Failure_Event'] = 0

for event_time in failures['Start']:
    # Mark the 6 hours leading up to the trip event
    mask = (load['UTC'] >= event_time - pd.Timedelta(hours=6)) & \
           (load['UTC'] <= event_time)
    load.loc[mask, 'Failure_Event'] = 1

load.to_csv("aligned_data.csv", index=False)
