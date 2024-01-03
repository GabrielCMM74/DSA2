'''
Name: Gabriel Coello
Student ID: 011062646
'''
import csv
from datetime import datetime, timedelta
from ups_truck import Truck
from ups_package import Package
from ups_hash import HashMap

# Function to load data from a CSV file
def load_csv_data(file_path, is_address_file=False):
    data = []
    with open(file_path, mode='r', encoding='utf-8-sig') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            # If it's an address file, make sure to convert the address to lower case
            if is_address_file and len(row) > 1:
                row[1] = row[1].lower()
            data.append(row)
    return data


# Make sure to pass 'skip_header=True' only if your CSV files have a header.
ups_address_data = load_csv_data('UPS_Files/UPS_Address_File.csv', is_address_file=True)
ups_distance_data = load_csv_data('UPS_Files/UPS_Distance_File.csv')
ups_package_data = load_csv_data('UPS_Files/UPS_Package_File.csv')


# Creates a package hash map to store Package objects
package_hash_map = HashMap()

# Created lists of package IDs for each truck
ups1_truck_packages = [1, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37, 40] 
ups2_truck_packages = [3, 6, 12, 17, 18, 21, 22, 23, 24, 26, 27, 35, 36, 38, 39]  
ups3_truck_packages = [2, 4, 5, 6, 7, 8, 9, 10, 11, 25, 28, 32, 33]  

# Initialized all of the trucks
ups1_truck = Truck(1, 'at_hub', '08:00 AM', '4001 South 700 East', None, None, None, 0, None, ups1_truck_packages, 16, 18, 0)
ups2_truck = Truck(2, 'at_hub', '10:20 AM', '4001 South 700 East', None, None, None, 0, None, ups2_truck_packages, 16, 18, 0)
ups3_truck = Truck(3, 'at_hub', '09:05 AM', '4001 South 700 East', None, None, None, 0, None, ups3_truck_packages, 16, 18, 0)

# List of trucks
trucks = [ups1_truck, ups2_truck, ups3_truck]  

# Function to determine the truck ID for a given package ID
def determine_truck_id_for_package(package_id):
    # Check if the package is in the list of packages for truck 1, 2, or 3
    if package_id in ups1_truck_packages:
        return ups1_truck.truck_id
    elif package_id in ups2_truck_packages:
        return ups2_truck.truck_id
    elif package_id in ups3_truck_packages:
        return ups3_truck.truck_id
    return None # Return None if the package ID doesn't match any truck

# Function to load package data from CSV into the hash map
def load_package_data(csv_data):
    for package in csv_data:
        # Extract package details from each row
        package_id = int(package[0])
        package_address = package[1].lower()
        package_city = package[2]
        package_state = package[3]
        package_zipcode = package[4]
        package_deadline_time = package[5]
        package_weight = package[6]
        package_status = "At Hub"  # Default status
        package_special_notes = package[7] if len(package) > 7 else ""
        package_delivery_time = package[8] if len(package) > 8 else None

        new_package = Package(
            package_id, 
            package_address, 
            package_city, 
            package_state, 
            package_zipcode, 
            package_deadline_time, 
            package_weight, 
            package_status, 
            package_special_notes, 
            package_delivery_time
        )
        # Determine and assign the truck ID to the package
        new_package.truck_id = determine_truck_id_for_package(package_id) 
        # Set expected delivery time to None initially
        new_package.expected_delivery_time = None  
        # Insert the new package into the hash map
        package_hash_map.insert(new_package.package_id, new_package)

load_package_data(ups_package_data)

def assign_packages_to_trucks(trucks, package_hash_map):
    for truck in trucks:
        # Iterate through each package ID in the truck's package list
        for package_id in truck.packages:
            # Lookup the package in the hash map
            package = package_hash_map.lookup(package_id)

            # Check if the package exists in the hash map
            if package:
                # If the package is found, load it onto the truck and update its status
                truck.load_package(package)
                package.update_status('en_route')
            else:
                # If the package is not found, print an error message
                print(f"Package ID {package_id} not found in hash map.")

# Call the function to assign packages to trucks
assign_packages_to_trucks(trucks, package_hash_map)

# Function to calculate the distance between two addresses using their indices in the distance data
def distance_in_between(index1, index2, distance_data):
    try:
        distance = distance_data[index1][index2]
        # If distance is not found in one direction, check the reverse direction
        if distance == '':
            distance = distance_data[index2][index1]
        return float(distance) # Convert the distance to a float
    except IndexError as e:
        # Print an error message if indices are out of range
        print(f"IndexError accessing distance_data with indices {index1}, {index2}: {e}")
        return None

# Function to format the address for lookup, typically using only the street address
def format_address_for_lookup(address):
    return address.split(',')[0].strip() # Return only the street part of the address

# Function to find the index of a given address in the address data
def extract_address_index(address, address_data):
    formatted_address = format_address_for_lookup(address).lower().strip()
    for index, name, addr in address_data:
        addr = addr.lower().strip()  # Ensure consistent formatting
        if formatted_address == addr:
            return int(index) - 1  # Adjust for zero-based index if needed
    print(f"Address not found in data: '{formatted_address}'")
    return None

# Function to calculate the distance between two addresses
def calculate_distance(address1, address2, address_data, distance_data):
    index1 = extract_address_index(address1, address_data)
    index2 = extract_address_index(address2, address_data)
    
    distance = distance_data[index1][index2]
    if distance == '':
        distance = distance_data[index2][index1]

    return float(distance)

# Function to deliver packages using the nearest neighbor algorithm
def deliver_packages(truck, package_hash_map, address_data, distance_data):
    current_time = datetime.strptime(truck.start_time, '%I:%M %p')
    truck.current_location_index = extract_address_index(truck.current_location, address_data)

    remaining_packages = set(truck.packages)
    while remaining_packages:
        closest_package_id = None
        closest_distance = float('inf')

        for package_id in remaining_packages:
            package = package_hash_map.lookup(package_id)
            destination_index = extract_address_index(package.address, address_data)
            distance_to_package = distance_in_between(truck.current_location_index, destination_index, distance_data)

            if distance_to_package < closest_distance:
                closest_distance = distance_to_package
                closest_package_id = package_id

        if closest_package_id is None:
            break  # Break if no more packages are reachable

        # Update for the closest package
        remaining_packages.remove(closest_package_id)
        package = package_hash_map.lookup(closest_package_id)
        travel_time = closest_distance / truck.average_speed
        travel_time_delta = timedelta(hours=travel_time)
        current_time += travel_time_delta
        delivery_time = current_time.strftime('%I:%M %p')

        package.expected_delivery_time = delivery_time  # Set expected delivery time


        truck.deliver_package(package, delivery_time)
        truck.current_location = package.address
        truck.current_location_index = extract_address_index(package.address, address_data)
        truck.update_mileage(closest_distance)

    # Add the return trip to the hub mileage
    hub_index = extract_address_index('4001 South 700 East', address_data)
    return_distance = distance_in_between(truck.current_location_index, hub_index, distance_data)
    truck.update_mileage(return_distance)

# Deliver packages for each truck
for truck in [ups1_truck, ups2_truck, ups3_truck]:
    deliver_packages(truck, package_hash_map, ups_address_data, ups_distance_data)


# Function to determine the status of a package at a given time
def determine_package_status(package, current_time, trucks):
    truck_id = package.truck_id # Get truck ID associated with the package
    # Find the truck that corresponds to the truck ID
    truck = next((t for t in trucks if t.truck_id == truck_id), None)  # Find the truck for this package


    if truck:
        truck_start_time = datetime.strptime(truck.start_time, '%I:%M %p')
        # If current time is before the truck's start time, the package is still at the hub
        if current_time < truck_start_time:
            return 'at_hub'  # Truck hasn't left yet

        if not package.expected_delivery_time:
            return 'at_hub'

        # Convert expected delivery time to datetime object
        expected_delivery_dt = datetime.strptime(package.expected_delivery_time, '%I:%M %p')
        # Determine if the package is en route or has been delivered
        if truck_start_time <= current_time < expected_delivery_dt:
            return 'en_route'
        elif current_time >= expected_delivery_dt:
            return 'delivered'
    else:
        # If no truck is associated with the package, default to 'at_hub'
        return 'at_hub'

# Function to query the status of packages
def query_status(package_hash_map, trucks):
    print("Welcome to the University Parcel Service (UPS)")
    # Calculate and display total miles for all deliveries
    total_miles = sum(truck.mileage for truck in trucks)
    print(f"Total miles for all 40 deliveries: {total_miles:.2f}")

    while True:
        user_input = input("Enter 'time' to check package statuses at a specific time, 'package' to check a single package, or 'exit' to quit: ").lower()

        if user_input == 'exit':
            break # Exit the loop if the user inputs 'exit'

        elif user_input == 'time':
            time_str = input("Enter the time (HH:MM AM/PM): ")
            try:
                specified_time = datetime.strptime(time_str, '%I:%M %p')
                # Iterate through all packages to determine their status at the specified time
                for package_id in range(1, 41):
                    package = package_hash_map.lookup(package_id)
                    if package:
                        package_status_at_time = determine_package_status(package, specified_time, trucks)
                        if package_status_at_time == 'delivered':
                            print(f"Package {package.package_id} status at {time_str}: {package_status_at_time} at {package.delivery_time}, Address: {package.address}, City: {package.city}, State: {package.state}, Zip: {package.zipcode}, Weight: {package.weight}, Deadline: {package.deadline}")
                        else:
                            print(f"Package {package.package_id} status at {time_str}: {package_status_at_time}, Address: {package.address}, City: {package.city}, State: {package.state}, Zip: {package.zipcode}, Weight: {package.weight}, Deadline: {package.deadline}")

            except ValueError:
                print("Invalid time format. Please use HH:MM AM/PM.")

        elif user_input == 'package':
            package_id = input("Enter Package ID: ")
            try:
                package_id = int(package_id)
                package = package_hash_map.lookup(package_id)
                if package:
                    # Print all relevant package information
                    print(f"Package {package.package_id}: Address - {package.address}, City - {package.city}, Zip - {package.zipcode}, Weight - {package.weight}, Status - {package.status}, Deadline - {package.deadline}")
                else:
                    print("Package not found.")
            except ValueError:
                print("Please enter a numeric Package ID.")




query_status(package_hash_map, trucks)
