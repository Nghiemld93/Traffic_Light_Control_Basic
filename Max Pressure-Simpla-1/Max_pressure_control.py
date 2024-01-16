# Ensure Python knows where TraCI is
import os, sys
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci
import random
from generator import TrafficGenerator
import simpla

def collect_waiting_times():
    """
    Retrieve the waiting time of every car in the incoming roads
    """
    # incoming_roads = ["E2TL", "N2TL", "W2TL", "S2TL"]
    incoming_roads = ["end1_junction", "end2_junction","end3_junction","end4_junction"]
    car_list = traci.vehicle.getIDList()
    waiting_times = dict()

    for car_id in car_list:
        wait_time = traci.vehicle.getAccumulatedWaitingTime(car_id)
        road_id = traci.vehicle.getRoadID(car_id)   # get the road id where the car is located
        if road_id in incoming_roads:               # consider only the waiting times of cars in incoming roads
            waiting_times[car_id] = wait_time
        else:
            if car_id in waiting_times:       # a car that was tracked has cleared the intersection
                del waiting_times[car_id] 
    
    total_waiting_time = sum(waiting_times.values())

    return total_waiting_time

def average_speed():
    sum_speed=0
    car_list = traci.vehicle.getIDList()
    for car_id in car_list:
        vehicle_speed=traci.vehicle.getSpeed(car_id)
        sum_speed+=vehicle_speed
    average_speed=sum_speed/(len(car_list)+0.0000000000001)
    print ("average_speed", average_speed)
    return average_speed


def get_queue_length():
        """
        Retrieve the number of cars with speed = 0 in every incoming lane
        """
        halt_1 = traci.edge.getLastStepHaltingNumber("end1_junction")
        halt_2 = traci.edge.getLastStepHaltingNumber("end2_junction")
        halt_3 = traci.edge.getLastStepHaltingNumber("end3_junction")
        halt_4 = traci.edge.getLastStepHaltingNumber("end4_junction")

        queue_length = (halt_1 + halt_2 + halt_3 + halt_4)/10
        return queue_length

# define helper functions
def movement_pressure(det_in, det_out):
    """
    Calculate maneuver pressure based on a pair of detectors 
    """
    incoming = traci.lanearea.getJamLengthVehicle(det_in)
    outgoing = traci.lanearea.getJamLengthVehicle(det_out)
    return incoming - outgoing

def phase_pressure(phases, detectors):
    """
    Calculate phase pressure aggregating all of its maneuver pressures
    """
    pressures = {} # dict
    for phase_id, movement_ids in phases.items():

        p_total = 0
        for m_id in movement_ids:

            det_in, det_out = detectors[m_id]
            p_total += movement_pressure(det_in, det_out)

        pressures[phase_id] = p_total
    return pressures

movement_detectors = [
    ("e2_0", "e2_26"),   #0
    ("e2_1", "e2_13"),   #1
    ("e2_2", "e2_9"),   #2

    ("e2_16", "e2_5"),   #3
    ("e2_20", "e2_7"),   #4
    ("e2_21", "e2_12"),   #5

    ("e2_24", "e2_11"),   #6
    ("e2_23", "e2_4"),   #7
    ("e2_22", "e2_8"),   #8

    ("e2_18", "e2_14"),   #9
    ("e2_17", "e2_10"),   #10
    ("e2_15", "e2_3")    #11
]

n_phases = 7
phases = {
    0: [0, 1, 3, 6, 7, 9],
    2: [0,2,3,6,8,9],
    4: [0,3,4,6,9,10],
    6: [0,3,5,6,9,11],
}

min_green = 150  # 15 seconds
phase_timers = {
    0: 0,
    2: 0,
    4: 0,
    6: 0
}

transitions = {
    0: 0,
    2: 2,
    4: 4,
    6: 6
}

_reward_store=[]
Total_Delay = []
Speed=[]

if __name__ == "__main__":
    
    for i in range(1):
        
        _sum_neg_reward=0
        old_total_wait=0
        delay_time=0

        print("Iteration %s: " % (i))
        val = random.randint(0, 1000)
        TrafficGenerator(3600,960).generate_routefile(val)

        sumo_cmd = ['sumo', '--duration-log.statistics', '--tripinfo-output', 'intelligent_lights_output_file.xml', '-c', 'intersection/intelligent_traffic.sumo.cfg']
        traci.start(sumo_cmd)
        simpla.load("intersection/1type.cfg.xml")
    
        step = 0
        time = 0
        Speed=[]
        while step <36000:  # 1 hour
            step += 1                          
            traci.simulationStep()

            current_total_wait = collect_waiting_times()
            reward = old_total_wait - current_total_wait
            old_total_wait = current_total_wait
            if reward<0:
                _sum_neg_reward+=reward

            delay_time+=get_queue_length()

            if step % 10 == 0:
                a_speed=average_speed()
                Speed.append(a_speed)
                  
            # controller implementation here
            phase = traci.trafficlight.getPhase("junction") # phase in 0,1,2,3,4,5,6
    
            # calculate pressure and max pressure phase
            pressures = phase_pressure(phases, movement_detectors)  # dict
            max_pressure_phase = phase # integal

            if any(pressures.values()):
                max_pressure_phase = max(pressures, key=pressures.get)

            if phase >= n_phases:
                print("time: {}, status: transition phase {}, pressures: {}, max pressure phase: {}".format(
                    time, phase, pressures, max_pressure_phase))
                time += 1
                continue

            if phase_timers[phase] < min_green: # min_green=10s
                phase_timers[phase] += 1
                print ("phase_timers[phase]", phase_timers[phase])
                print("time: {}, status: min_green, current phase: {}, pressures: {}, max pressure phase: {}".format(
                    time, phase, pressures, max_pressure_phase))
                time += 1
                continue

            # calulate phase switch
            if phase != max_pressure_phase:
                traci.trafficlight.setPhase("junction", transitions[max_pressure_phase])
                phase_timers[phase] = 0
                print("time: {}, status: trainsition from: {} to {}, pressures: {}, max pressure phase: {}".format(
                    time, phase, max_pressure_phase, pressures, max_pressure_phase))    
            else:
                traci.trafficlight.setPhase("junction", phase)
                phase_timers[phase] + 1
                print("time: {}, status: extend phase, current phase: {}, pressures: {}, max pressure phase: {}".format(
                    time, phase, pressures, max_pressure_phase))            
           

        _reward_store.append(_sum_neg_reward)
        with open('Total_waiting_time.csv', mode='w') as f1:
            for value in _reward_store:
                f1.write("%s\n" % value)

        Total_Delay.append(delay_time)
        with open('Total_Delay_time.csv', mode='w') as f2:
            for value in Total_Delay:
                f2.write("%s\n" % value)


        with open('Average_Speed.csv', mode='w') as f3:
            for value in Speed:
                f3.write("%s\n" % value)

        sys.stdout.flush()
        traci.close()
                