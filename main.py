'''
Nicholas Boni
10/21/2024
'''
import json
import time
import datetime
import os

from nyct_gtfs import NYCTFeed

def read_config():

    with open('config.json') as f:
        config_dict = json.load(f)

    return config_dict

def update_config():

    print('\nLet\'s set your preferred train line and station.\n\
          Note that the line goes by color, so e.g., you can specify \n\
          A, C, or E, and you will get updates for the ACE line.\n')

    line = input("Which train line do you want to track? ")
    station = input("Which station do you want to track? ")
    direction = input("Which direction do you care about, uptown or downtown? ")
    # mode = input("Type 'any' if any train on that line will do. Type 'only' if you only care about the train specified. ")

    with open('config.json', 'r') as f:
        config_dict = json.load(f)
        config_dict['line'] = line.upper()
        config_dict['station'] = station
        config_dict['direction'] = direction
    # config_dict['mode'] = mode

    with open('config.json', 'w') as f:
        f.write( json.dumps(config_dict, indent=4) )

    print('\nSaved! New config:\n')
    print(json.dumps(config_dict, indent=4) + '\n')
    time.sleep(1)

    return None

def help():

    print_title_card()

    '''
    confirm = input('Do you want a station reference for your selected train line (y/n)? ')

    if confirm == 'y':
        config_dict = read_config()
        print(f'\nSTATION NAMES FOR THE {config_dict['line']} TRAIN\n')
        previous = ''

        trips = NYCTFeed(config_dict['line']).trips
        list_trip_stops(trips[0])

        with open('google_transit/stops.txt') as f:
            for line in f:
                line_list = line.split(',')
                if line_list[0][0] == config_dict['line']:
                    station_name = line_list[2]
                    if station_name == previous:
                        continue
                    previous = station_name
                    print(f'{line_list[2]}')

        print()
        time.sleep(1)
    '''

    return None

def query_station_arrivals():

    with open('config.json') as f:
        config_dict = json.load(f)
        line = config_dict['line']
        station = config_dict['station']
        direction = config_dict['direction']
    # mode = config_dict['mode']
        
    # if mode == 'only':
    trips = NYCTFeed(line).filter_trips(line_id=line)
    # else:
    #     trips = NYCTFeed(line).trips

    arrival_times = []
    countdown_dict = {}
    outstr = ''

    for trip in trips:
        # Sometimes trains with invalid metadata
        # can cause a ValueError.
        try:
            # print(trip)
            train_name = trip.__str__().split(',')[0]
        except ValueError:
            print('A train with invalid metadata was ignored.')
            continue

        if ( direction == 'uptown' and 'Southbound' in train_name ) \
              or ( direction == 'downtown' and 'Northbound' in train_name ):
            continue

        if trip.headed_to_stop( stop_name_to_stop_id(station) ):
            remaining_stops = trip.stop_time_updates
            for stop in remaining_stops:
                if station == stop.stop_name:
                    eta = stop.arrival.strftime('%I:%M %p')
                    countdown = int( ( stop.arrival - datetime.datetime.now() ).total_seconds() / 60 )
                    arrival_times.append(eta)
                    outstr = f'{eta} (in {countdown} min): {train_name}, currently at {remaining_stops[0].stop_name}.\n'
                    countdown_dict[countdown] = outstr

    # if mode == 'any':
    #     print(f'\nARRIVAL TIMES FOR: any train on the {line} line at {station}\n')
    # else:
        print(f'\nARRIVAL TIMES FOR: only {line} trains at {station}\n')
    
    sorted_countdown_keys = sorted(countdown_dict)
    
    for key in sorted_countdown_keys:
        if key < 0:
            print(f'Canceled: {countdown_dict[key]}')
        else:
            print(countdown_dict[key])

    return arrival_times

def list_trip_stops(trip):
    stops = {}
    trip_train = trip.trip_id.split('..')[0][-1]
    
    with open('google_transit/stop_times.txt') as f:
        for line in f:
            line_list = line.split(',')
            line_trip_id = line_list[0]

            print('searching file for route...')
            if trip_train != line_trip_id.split('..')[0][-1].strip():
                continue
            print('found.')

            line_stop_id = line_list[1]
            line_stop_index = line_list[-1].strip()

            if trip.trip_id in line_trip_id:
                input(f'stop {line_list[-1].strip()}: {stop_id_to_stop_name(line_list[1])}')
                stops[line_list[-1].strip()] = stop_id_to_stop_name(line_list[1])
            
    print(stops)
    return stops

def stop_id_to_stop_name(stop_id):

    with open('google_transit/stops.txt') as f:
        for line in f:
            line_list = line.split(',')

            if line_list[0] == stop_id:
                return line_list[1]

    return ''

def stop_name_to_stop_id(stop_name):
    with open('config.json') as f:
        config_dict = json.load(f)

    with open('google_transit/stops.txt') as f:
        for line in f:
            line_list = line.split(',')

            if line_list[-1].strip() == '':
                continue

            if config_dict['direction'] == 'uptown' and not 'N' in line_list[0]:
                continue

            if config_dict['direction'] == 'downtown' and not 'S' in line_list[0]:
                continue

            if line_list[1] == stop_name:
                return line_list[0]

    return ''

def handle_user_input():
    command = input('What would you like to do? ').lower()
    
    if command == 'config':
        print('Your current config is: ')
        print(read_config())
        if input('Update? ').lower() == 'y':
            update_config()
    
    elif command == 'update':
        query_station_arrivals()
        # new_query()

    elif command == 'help':
        help()

    elif command == 'quit':
        quit()

    else:
        print('Command not recognized. Type "help" for available commands.')
        handle_user_input()

def print_title_card():

    title_copy='\n**************************************************\n\
Nick\'s MTA tracker\n\
\n\
This tool tracks train times.\n\
\n\
Type "config" to set your preferred station.\n\
Type "update" to get the latest arrival times\n\
    to your preferred station.\n\
Type "help" for help.\n\
Type "quit" to exit the program.\n\
**************************************************\n'

    print(title_copy)
    
def main():
    print_title_card()

    if not os.path.isfile('config.json'):
        update_config()

    while True:
        handle_user_input()

if __name__ == '__main__':
    main()