from Weather_work.root_gate_checker import Gate_checker

Gate_checker().get_UA_flight_nums()
Gate_checker().multiple_thread()

while True:
    gate = input('What gate?')
    if gate:
        Gate_checker(gate).ewr_UA_gate()
    else:
        break
