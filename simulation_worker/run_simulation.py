import os
import json
import traci
from collections import defaultdict

DIR_PATH = os.path.dirname(os.path.abspath(__file__))

SPEED_THRESHOLD = 0.3  # m/s
INTERSECTIONS_OF_INTEREST = ("I2", "I3")
SIMULATION_DURATION = 2000
SUMO_BINARY = "sumo"
CONFIG_PATH = os.path.join(DIR_PATH, "hw_model.sumocfg.xml")
SCENARIO_PATH = os.path.join(DIR_PATH, "scenario.json")


def add_vehicles(vehicles_batch, start_index):
    index = start_index
    for route_id, _, vehicle_type in vehicles_batch:
        vehicle_id = f"{route_id}_{index}"
        traci.vehicle.add(vehicle_id, route_id, vehicle_type)
        index += 1
    return index


def run_simulation():
    with open(SCENARIO_PATH, 'r') as file:
        vehicle_schedule = json.load(file)

    traci.start([
        SUMO_BINARY,
        "-c", CONFIG_PATH,
        "--start",
        "--quit-on-end"
    ])

    delays = defaultdict(int)
    stopped_vehicles = defaultdict(set)
    index = 0

    try:
        for step in range(SIMULATION_DURATION):
            if str(step) in vehicle_schedule:
                index = add_vehicles(vehicle_schedule[str(step)], index)

            traci.simulationStep()

            for veh_id in traci.vehicle.getIDList():
                speed = traci.vehicle.getSpeed(veh_id)
                edge = traci.vehicle.getRoadID(veh_id)

                if speed < SPEED_THRESHOLD:
                    intersection = next((i for i in INTERSECTIONS_OF_INTEREST if i in edge), None)
                    if intersection:
                        delays[intersection] += 1
                        stopped_vehicles[intersection].add(veh_id)
    finally:
        traci.close()

    avg_delays = {
        k: (delays[k] / len(stopped_vehicles[k]) if stopped_vehicles[k] else 0)
        for k in INTERSECTIONS_OF_INTEREST
    }

    print("\nFinal intersection average delays (seconds):")
    for intersection, avg in avg_delays.items():
        print(f"{intersection}: {avg:.2f} seconds")

    return avg_delays


if __name__ == "__main__":
    avg_delays = run_simulation()
    print(json.dumps({"intersection_avg_delays": avg_delays}))
