import numpy as np
import math

class TrafficGenerator:
    def __init__(self, max_steps, n_cars_generated):
        self._n_cars_generated = n_cars_generated  # how many cars per episode
        self._max_steps = max_steps
    def generate_routefile(self, seed):

        print("seed =", seed)
        """
        Generation of the route of every car for one episode
        """
        np.random.seed(seed)  # make tests reproducible
        print( "create file")
        # the generation of cars is distributed according to a weibull distribution
        timings = np.random.weibull(2, self._n_cars_generated)
        timings = np.sort(timings)

        # reshape the distribution to fit the interval 0:max_steps
        car_gen_steps = []
        min_old = math.floor(timings[1])
        max_old = math.ceil(timings[-1])
        min_new = 0
        max_new = self._max_steps
        for value in timings:
            car_gen_steps = np.append(car_gen_steps, ((max_new - min_new) / (max_old - min_old)) * (value - max_old) + max_new)

        car_gen_steps = np.rint(car_gen_steps)  # round every value to int -> effective steps when a car will be generated

        # produce the file for cars generation, one car per line
        with open("intersection/intelligent_traffic.rou.xml", "w") as routes:
            print("""<routes>
            <vType id="CVs" color="cyan" maxSpeed="20" accel="2.5" decel="3" minGap="0.50" tau="1" scale="1"/>
            <vType id="non-CV" color="magenta" maxSpeed="20" accel="2.5" decel="3" minGap="2.5" tau="1" />
    
            <vType id="t_catchup" minGap="2.5" color="red" tau="1" maxSpeed="20" accel="2.5" decel="3"/>
            <vType id="t_catchupFollower" minGap="0.50" color="blue" tau="0.1" maxSpeed="20" accel="2.5" decel="3"/>
            <vType id="t_follower" minGap="0.50" color="green" tau="0.1" maxSpeed="20" accel="2.5" decel="3"/>
            <vType id="t_leader" minGap="2.5" color="yellow" tau="1" maxSpeed="20" accel="2.5" decel="3"/>

            <route id="W_N" edges="end4_junction junction_end1"/>
            <route id="W_E" edges="end4_junction junction_end2"/>
            <route id="W_S" edges="end4_junction junction_end3"/>

            <route id="N_W" edges="end1_junction junction_end4"/>
            <route id="N_E" edges="end1_junction junction_end2"/>
            <route id="N_S" edges="end1_junction junction_end3"/>

            <route id="E_W" edges="end2_junction junction_end4"/>
            <route id="E_N" edges="end2_junction junction_end1"/>
            <route id="E_S" edges="end2_junction junction_end3"/>

            <route id="S_W" edges="end3_junction junction_end4"/>
            <route id="S_N" edges="end3_junction junction_end1"/>
            <route id="S_E" edges="end3_junction junction_end2"/>
            
            <flow id="f_0n" begin="0.00" departLane="0" arrivalLane="0" from="end1_junction" to="junction_end4" end="3600.00" probability="0.01111111111111" type="CVs" departSpeed="5"/>
            <flow id="f_1n" begin="0.00" departLane="1" arrivalLane="1" from="end1_junction" to="junction_end3" end="3600.00" probability="0.01111111111111" type="CVs" departSpeed="5"/>
            <flow id="f_2n" begin="0.00" departLane="2" arrivalLane="2" from="end1_junction" to="junction_end2" end="3600.00" probability="0.01111111111111" type="CVs" departSpeed="5"/>
            
            <flow id="f_0E" begin="0.00" departLane="0" arrivalLane="0" from="end2_junction" to="junction_end1" end="3600.00" probability="0.01111111111111" type="CVs" departSpeed="5"/>
            <flow id="f_1E" begin="0.00" departLane="1" arrivalLane="1" from="end2_junction" to="junction_end4" end="3600.00" probability="0.01111111111111" type="CVs" departSpeed="5"/>
            <flow id="f_2E" begin="0.00" departLane="2" arrivalLane="2" from="end2_junction" to="junction_end3" end="3600.00" probability="0.01111111111111" type="CVs" departSpeed="5"/>            
            
            <flow id="f_0S" begin="0.00" departLane="0" arrivalLane="0" from="end3_junction" to="junction_end2" end="3600.00" probability="0.01111111111111" type="CVs" departSpeed="5"/>
            <flow id="f_1S" begin="0.00" departLane="1" arrivalLane="1" from="end3_junction" to="junction_end1" end="3600.00" probability="0.01111111111111" type="CVs" departSpeed="5"/>
            <flow id="f_2S" begin="0.00" departLane="2" arrivalLane="2" from="end3_junction" to="junction_end4" end="3600.00" probability="0.01111111111111" type="CVs" departSpeed="5"/>

            <flow id="f_0W" begin="0.00" departLane="0" arrivalLane="0" from="end4_junction" to="junction_end3" end="3600.00" probability="0.01111111111111" type="CVs" departSpeed="5"/>
            <flow id="f_1W" begin="0.00" departLane="1" arrivalLane="1" from="end4_junction" to="junction_end2" end="3600.00" probability="0.01111111111111" type="CVs" departSpeed="5"/>
            <flow id="f_2W" begin="0.00" departLane="2" arrivalLane="2" from="end4_junction" to="junction_end1" end="3600.00" probability="0.01111111111111" type="CVs" departSpeed="5"/>




            """, file=routes)

            for car_counter, step in enumerate(car_gen_steps):
                straight_or_turn = np.random.uniform()
                if straight_or_turn < 0.40:  # choose direction: straight or turn - 40% of times the car goes straight
                    route_straight = np.random.randint(1, 5)  # choose a random source & destination
                    if route_straight == 1:
                        print('    <vehicle id="W_E_%i" type="non-CV" route="W_E" depart="%s" departLane="1" arrivalLane="1" departSpeed="5" />' % (car_counter, step), file=routes)
                    elif route_straight == 2:
                        print('    <vehicle id="E_W_%i" type="non-CV" route="E_W" depart="%s" departLane="1" arrivalLane="1" departSpeed="5" />' % (car_counter, step), file=routes)
                    elif route_straight == 3:
                        print('    <vehicle id="N_S_%i" type="non-CV" route="N_S" depart="%s" departLane="1" arrivalLane="1" departSpeed="5" />' % (car_counter, step), file=routes)
                    else:
                        print('    <vehicle id="S_N_%i" type="non-CV" route="S_N" depart="%s" departLane="1" arrivalLane="1" departSpeed="5" />' % (car_counter, step), file=routes)
                else:  # car that turn -25% of the time the car turns
                    route_turn = np.random.randint(1, 9)  # choose random source source & destination
                    if route_turn == 1:
                        print('    <vehicle id="W_N_%i" type="non-CV" route="W_N" depart="%s" departLane="2" arrivalLane="2" departSpeed="5" />' % (car_counter, step), file=routes)
                    elif route_turn == 2:
                        print('    <vehicle id="W_S_%i" type="non-CV" route="W_S" depart="%s" departLane="0" arrivalLane="0" departSpeed="5" />' % (car_counter, step), file=routes)
                    elif route_turn == 3:
                        print('    <vehicle id="N_W_%i" type="non-CV" route="N_W" depart="%s" departLane="0" arrivalLane="0" departSpeed="5" />' % (car_counter, step), file=routes)
                    elif route_turn == 4:
                        print('    <vehicle id="N_E_%i" type="non-CV" route="N_E" depart="%s" departLane="2" arrivalLane="2" departSpeed="5" />' % (car_counter, step), file=routes)
                    elif route_turn == 5:
                        print('    <vehicle id="E_N_%i" type="non-CV" route="E_N" depart="%s" departLane="0" arrivalLane="0" departSpeed="5" />' % (car_counter, step), file=routes)
                    elif route_turn == 6:
                        print('    <vehicle id="E_S_%i" type="non-CV" route="E_S" depart="%s" departLane="2" arrivalLane="2" departSpeed="5" />' % (car_counter, step), file=routes)
                    elif route_turn == 7:
                        print('    <vehicle id="S_W_%i" type="non-CV" route="S_W" depart="%s" departLane="2" arrivalLane="2" departSpeed="5" />' % (car_counter, step), file=routes)
                    elif route_turn == 8:
                        print('    <vehicle id="S_E_%i" type="non-CV" route="S_E" depart="%s" departLane="0" arrivalLane="0" departSpeed="5" />' % (car_counter, step), file=routes)

            print("</routes>", file=routes)



