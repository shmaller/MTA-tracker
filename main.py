'''
Nicholas Boni
10/21/2024
'''
import json, time, datetime
from nyct_gtfs import NYCTFeed

def update_config():
    print('\nLet\'s set your preferred train line and station.\n\
          Note that the line goes by color, so e.g., you can specify \n\
          A, C, or E, and you will get updates for the ACE line.\n')

    line = input("Which train line do you want to track? ")
    station = input("Which station do you want to track? ")
    direction = input("Which direction do you care about, uptown or downtown? ")
    mode = input("Type 'any' if any train on that line will do. Type 'only' if you only care about the train specified. ")

    with open('config.json', 'r') as f:
        config_dict = json.load(f)
        config_dict['line'] = line.upper()
        config_dict['station'] = station
        config_dict['direction'] = direction
        config_dict['mode'] = mode

    with open('config.json', 'w') as f:
        f.write( json.dumps(config_dict, indent=4) )

    print('\nSaved! New config:\n')
    print(json.dumps(config_dict) + '\n')
    time.sleep(1)

    return None

def query_station_arrivals():

    with open('config.json') as f:
        config_dict = json.load(f)
        line = config_dict['line']
        station = config_dict['station']
        direction = config_dict['direction']
        mode = config_dict['mode']
        
    if mode == 'only':
        trains = NYCTFeed(line).filter_trips(line_id=line)
    else:
        trains = NYCTFeed(line).trips

    arrival_times = []
    countdown_dict = {}
    outstr = ''

    for train in trains:

        # Sometimes trains with invalid metadata
        # can cause a ValueError.
        try:
            train_name = train.__str__().split(',')[0]
        except ValueError:
            continue

        if ( direction == 'uptown' and 'Southbound' in train_name ) \
              or ( direction == 'downtown' and 'Northbound' in train_name ):
            continue

        remaining_stops = train.stop_time_updates

        for stop in remaining_stops:
            if station == stop.stop_name:
                print(stop)
                eta = stop.arrival.strftime('%I:%M %p')
                countdown = int( ( stop.arrival - datetime.datetime.now() ).total_seconds() / 60 )
                arrival_times.append(eta)
                outstr = f'{eta} (in {countdown} min): {train_name}, currently at {remaining_stops[0].stop_name}.\n'
                countdown_dict[countdown] = outstr

    if mode == 'any':
        print(f'\nARRIVAL TIMES FOR: any train on the {line} line at {station}\n')
    else:
        print(f'\nARRIVAL TIMES FOR: only {line} trains at {station}\n')
    
    sorted_countdown_keys = sorted(countdown_dict)
    
    for key in sorted_countdown_keys:
        print(countdown_dict[key])

    return arrival_times

def handle_user_input():
    command = input('What would you like to do? ').lower()
    
    if command == 'config':
        update_config()
    
    elif command == 'update':
        query_station_arrivals()

    elif command == 'quit':
        quit()

    else:
        print('Command not recognized.')
        time.sleep(1)
        handle_user_input()

def print_title_card():

    title_copy='**************************************************\n\
Nick\'s MTA tracker\n\
\n\
This tool tracks train times.\n\
\n\
Type "config" to set your preferred station.\n\
Type "update" to get the latest arrival times\n\
    to your preferred station.\n\
Type "quit" to exit the program.\n\
**************************************************\n'

    print(title_copy)
    
def main():
    print_title_card()

    while True:
        handle_user_input()

if __name__ == '__main__':
    main()