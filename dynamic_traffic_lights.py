import traci
import sumolib
import time


def get_vehicle_count(lane_id):
    return traci.lane.getLastStepVehicleNumber(lane_id)


def adjust_traffic_lights():
    traffic_lights = traci.trafficlight.getIDList()

    for tl_id in traffic_lights:
        controlled_lanes = traci.trafficlight.getControlledLanes(tl_id)
        lane_vehicle_counts = {}

        for lane in controlled_lanes:
            if not lane.startswith(':'):  # Skip internal lanes
                count = get_vehicle_count(lane)
                lane_vehicle_counts[lane] = count

        if lane_vehicle_counts:
            max_lane = max(lane_vehicle_counts, key=lane_vehicle_counts.get)
            max_vehicles = lane_vehicle_counts[max_lane]
            print(f"TL {tl_id} - Busiest lane: {max_lane} with {max_vehicles} vehicles")

            current_state = list(traci.trafficlight.getRedYellowGreenState(tl_id))
            controlled_links = traci.trafficlight.getControlledLinks(tl_id)

            for i, links in enumerate(controlled_links):
                if max_lane in links[0]:  # If this link controls the busiest lane
                    current_state[i] = 'G'
                else:
                    current_state[i] = 'r'

            new_state = ''.join(current_state)
            traci.trafficlight.setRedYellowGreenState(tl_id, new_state)
            print(f"TL {tl_id} - New state: {new_state}")
        else:
            print(f"TL {tl_id} - No vehicles in controlled lanes")


def main():
    sumoCmd = ["sumo-gui", "-c",
               "/home/piyush/Desktop/12345/Project 1- Emergency vehicle route optimization/sumo.sumocfg"]
    traci.start(sumoCmd)

    print("Traffic light IDs:", traci.trafficlight.getIDList())

    try:
        step = 0
        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            if step % 30 == 0:  # Adjust traffic lights every 30 steps
                print(f"\nTime step: {step}")
                adjust_traffic_lights()
                time.sleep(1)  # Pause for 1 second to make changes more noticeable
            step += 1
    except traci.exceptions.TraCIException as e:
        print(f"TraCI exception: {e}")
    finally:
        traci.close()


if __name__ == "__main__":
    main()