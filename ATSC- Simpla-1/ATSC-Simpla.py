#!/usr/bin/env python

import os
import sys
from math import sqrt

import random

#路径
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")
import traci
import csv
import simpla

from generator import TrafficGenerator

def collect_waiting_times():
    """
    Retrieve the waiting time of every car in the incoming roads
    """
    # incoming_roads = ["E2TL", "N2TL", "W2TL", "S2TL"]
    incoming_roads = ["N2TL", "E2TL","S2TL","W2TL"]
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
    return average_speed


def get_queue_length():
        """
        Retrieve the number of cars with speed = 0 in every incoming lane
        """
        halt_1 = traci.edge.getLastStepHaltingNumber("N2TL")
        halt_2 = traci.edge.getLastStepHaltingNumber("E2TL")
        halt_3 = traci.edge.getLastStepHaltingNumber("S2TL")
        halt_4 = traci.edge.getLastStepHaltingNumber("W2TL")

        queue_length = (halt_1 + halt_2 + halt_3 + halt_4)/10

        return queue_length

_reward_store=[]
Total_Delay = []
Speed=[]


if __name__ == "__main__":
    
    for i in range(1):
        print("Iteration %s: " % (i))
        val = random.randint(0, 1000)
        TrafficGenerator(3600,960).generate_routefile(val)  # traffic generation for non-CVs
        
        _sum_neg_reward=0
        old_total_wait=0
        delay_time=0       

        sumo_cmd = ['sumo', '--duration-log.statistics', '--tripinfo-output', 'intelligent_lights_output_file.xml', '-c', 'intersection/sumo_config.sumocfg']
        traci.start(sumo_cmd)
        simpla.load("intersection/1type.cfg.xml") 

        step = 0 
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
                

        

        

    
