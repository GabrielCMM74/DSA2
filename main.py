'''
Name: Gabriel Coello
Student ID: 011062646
'''
import csv
import datetime
from ups_package import Package
from ups_truck import Truck
from ups_hash import HashMap


def load_csv_data(file_path):
    data = []
    with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            data.append(row)
    return data


# Load data from CSV files
ups_address_data = load_csv_data('UPS_Files/UPS_Address_File.csv')

ups_distance_data = load_csv_data('UPS_Files/UPS_Distance_File.csv')

ups_package_data = load_csv_data('UPS_Files/UPS_Package_File.csv')


package_hash_map = HashMap()

# Function to create Package objects and insert them into the hash map
# Function to create Package objects and insert them into the hash map
def load_packages_into_hashmap(package_data, package_hash_map):
    for package in package_data[1:]:  # Skip the header row
        package_id = int(package[0])
        address = package[1]
        city = package[2]
        state = package[3]
        zip_code = package[4]
        deadline = parse_time(package[5])  # Parse deadline before creating the package object
        weight = package[6]
        status = "At Hub"  # Default status
        special_notes = package[7] if len(package) > 7 else None

        # Create a Package object with parsed deadline
        package_obj = Package(package_id, address, city, state, zip_code, deadline, weight, status, special_notes)
        
        # Insert the Package object into the hash map
        package_hash_map.insert(package_id, package_obj)


# Initialize trucks with their respective package lists
# We create lists of package IDs for each truck
ups1_truck_packages = [1, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37, 40]  # Example packages for truck1
ups2_truck_packages = [3, 6, 12, 17, 18, 21, 22, 23, 24, 26, 27, 35, 36, 38, 39]  # Example packages for truck2, including those that can only be on truck 2
ups3_truck_packages = [2, 4, 5, 6, 7, 8, 9, 10, 11, 25, 28, 32, 33]  # Example delayed packages that arrive at 9:05 am

# Initialize the truck objects
ups1_truck = Truck(truck_id=1, packages=ups1_truck_packages, current_location='Hub', start_time='08:00 AM', capacity=16, average_speed=18, mileage=0)
ups2_truck = Truck(truck_id=2, packages=ups2_truck_packages, current_location='Hub', start_time='10:20 AM', capacity=16, average_speed=18, mileage=0)
ups3_truck = Truck(truck_id=3, packages=ups3_truck_packages, current_location='Hub', start_time='09:05 AM', capacity=16, average_speed=18, mileage=0)

# Since trucks will be loaded manually, we just assign the package lists directly
# Load package details into trucks based on the IDs
def load_truck_packages(truck, package_hash_map):
    for package_id in truck.packages:
        package = package_hash_map.lookup(package_id)
        if package:
            truck.load_package(package)
        else:
            print(f"Package ID {package_id} not found. Cannot load onto truck {truck.truck_id}.")

truck_departure_times = {
    1: datetime.datetime.strptime('08:00 AM', '%I:%M %p'),
    2: datetime.datetime.strptime('09:05 AM', '%I:%M %p'),
    3: datetime.datetime.strptime('10:20 AM', '%I:%M %p')
}
# Load packages onto each truck
for truck in [ups1_truck, ups2_truck, ups3_truck]:
    departure_time = truck_departure_times[truck.truck_id]
    load_truck_packages(truck, package_hash_map, departure_time)


def calculate_travel_time(distance, average_speed=18):
    # Assuming average_speed is in miles per hour
    hours_to_travel = distance / average_speed
    return datetime.timedelta(hours=hours_to_travel)

def find_next_package(packages, distance_matrix, address_to_index, current_location_index, current_time):
    next_package = None
    minimum_time = datetime.timedelta.max

    for package in packages:
        if package.status != 'delivered':
            address_key = package.address.lower().strip()
            if address_key not in address_to_index:
                print(f"Warning: Address '{package.address}' not found in address index.")
                continue

            package_address_index = address_to_index[address_key]
            travel_distance = distance_matrix.get((current_location_index, package_address_index)) or \
                            distance_matrix.get((package_address_index, current_location_index))

            if travel_distance is None:
                print(f"Warning: No distance data available for address '{package.address}'.")
                continue

            travel_time = calculate_travel_time(travel_distance)
            arrival_time = current_time + travel_time

            if package.deadline == 'EOD' or arrival_time <= package.deadline:
                if arrival_time < minimum_time:
                    next_package = package
                    minimum_time = arrival_time

    return next_package

    
def prioritize_packages_for_delivery(packages, distances, current_time, current_location):
    sorted_packages = []
    while packages:
        next_package = find_next_package(packages, distances, current_location, current_time)
        if not next_package:
            break  # No more packages can be delivered today

        sorted_packages.append(next_package)
        packages.remove(next_package)
        travel_time = calculate_travel_time(distances[current_location][next_package.address])
        current_time += travel_time
        current_location = next_package.address
        next_package.status = 'delivered'  # Update package status

    return sorted_packages

def parse_time(time_str):
    # Handles parsing of time strings, accounting for 'EOD' as end of business day (5:00 PM)
    if time_str == 'EOD':
        return datetime.datetime.strptime('17:00:00', '%H:%M:%S').time()
    else:
        return datetime.datetime.strptime(time_str, '%H:%M %p').time()
    
address_to_index = {}

def create_address_index_mapping(address_data):
    address_to_index = {}
    for index, row in enumerate(address_data[1:]):  # Skip the header row
        # Construct a unique key for each address (could also include city, state, and zip if needed)
        address_key = row[1].strip().lower()  # Using address field, make sure to strip and lower for consistency
        address_to_index[address_key] = index
    return address_to_index

address_to_index = create_address_index_mapping(ups_address_data)


def create_distance_matrix(distance_data, address_to_index):
    # Initialize a dictionary to hold the distances
    distance_matrix = {}

    for i, row in enumerate(distance_data[1:]):  # Skip the header row
        for j, distance in enumerate(row[1:], start=1):  # Skip the first column and enumerate starting at 1
            if distance:  # Only if there's a distance value present
                # The distance matrix is indexed by a tuple of address indices
                distance_matrix[(i, j)] = float(distance)

    return distance_matrix

distance_matrix = create_distance_matrix(ups_distance_data, address_to_index)

def calculate_distance(from_index, to_index, distance_matrix):
    return distance_matrix.get((from_index, to_index)) or distance_matrix.get((to_index, from_index))

def plan_and_execute_delivery(truck, package_hash_map, distance_matrix, address_to_index):
    current_location_index = address_to_index[truck.current_location.lower().strip()]
    packages_to_deliver = [package_hash_map.lookup(package_id) for package_id in truck.packages]
    delivery_plan = prioritize_packages_for_delivery(packages_to_deliver, distance_matrix, datetime.datetime.now(), current_location_index)

    for package in delivery_plan:
        package.update_status('en_route')
        distance_to_next_package = calculate_distance(current_location_index, address_to_index[package.address.lower().strip()], distance_matrix)
        truck.update_mileage(distance_to_next_package)
        current_location_index = address_to_index[package.address.lower().strip()]
        package.update_status('delivered')

    truck.update_status('completed_route')


def display_truck_status_and_mileage(trucks):
    for truck in trucks:
        print(truck)


# Execute delivery for each truck
for truck in [ups1_truck, ups2_truck, ups3_truck]:
    plan_and_execute_delivery(truck, package_hash_map, distance_matrix, address_to_index)

# Display the status and mileage of each truck
display_truck_status_and_mileage([ups1_truck, ups2_truck, ups3_truck])

def query_status(package_hash_map, trucks):
    while True:
        user_input = input("Enter package ID for package status, 'trucks' for truck status, or 'exit' to quit: ")
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'trucks':
            display_truck_status_and_mileage(trucks)
        else:
            try:
                package_id = int(user_input)
                package = package_hash_map.lookup(package_id)
                if package:
                    print(package)
                else:
                    print("Package not found.")
            except ValueError:
                print("Invalid input. Please enter a numeric package ID or 'trucks'.")

# Call this function to start the UI
query_status(package_hash_map, [ups1_truck, ups2_truck, ups3_truck])