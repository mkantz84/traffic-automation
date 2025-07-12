# utils.py
# Shared utility functions 

def calculate_error(sim_delays, expected_delays):
    return sum(
        (sim_delays.get(k, 0) - expected_delays[k]) ** 2
        for k in expected_delays
    ) 