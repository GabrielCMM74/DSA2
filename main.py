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
# print(f"Loaded addresses: {ups_address_data[:5]}")  
ups_distance_data = load_csv_data('UPS_Files/UPS_Distance_File.csv')
ups_package_data = load_csv_data('UPS_Files/UPS_Package_File.csv')


# Create a package hash map to store Package objects
package_hash_map = HashMap()

# We create lists of package IDs for each truck
ups1_truck_packages = [1, 13, 14, 15, 16, 19, 20, 29, 30, 31, 34, 37, 40]  # Example packages for truck1
ups2_truck_packages = [3, 6, 12, 17, 18, 21, 22, 23, 24, 26, 27, 35, 36, 38, 39]  # Example packages for truck2, including those that can only be on truck 2
ups3_truck_packages = [2, 4, 5, 6, 7, 8, 9, 10, 11, 25, 28, 32, 33]  # Example delayed packages that arrive at 9:05 am

ups1_truck = Truck(1, 'at_hub', '08:00 AM', '4001 South 700 East', None, None, None, 0, None, ups1_truck_packages, 16, 18, 0)
ups2_truck = Truck(2, 'at_hub', '10:20 AM', '4001 South 700 East', None, None, None, 0, None, ups2_truck_packages, 16, 18, 0)
ups3_truck = Truck(3, 'at_hub', '09:05 AM', '4001 South 700 East', None, None, None, 0, None, ups3_truck_packages, 16, 18, 0)


trucks = [ups1_truck, ups2_truck, ups3_truck]  # List of your trucks

def determine_truck_id_for_package(package_id):
    if package_id in ups1_truck_packages:
        return ups1_truck.truck_id
    elif package_id in ups2_truck_packages:
        return ups2_truck.truck_id
    elif package_id in ups3_truck_packages:
        return ups3_truck.truck_id
    return None

def load_package_data(csv_data):
    for package in csv_data:
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

        new_package.truck_id = determine_truck_id_for_package(package_id)  # Add truck association
        new_package.expected_delivery_time = None  # Placeholder for delivery time

        package_hash_map.insert(new_package.package_id, new_package)
        print(f"Loaded package ID: {package_id}, Address: {package[1]}")

        # Add a debugging print statement

        if package_id == 1:
            print(f"Special check: Package 1 loaded with address {package[1]}")


load_package_data(ups_package_data)


# Initialize trucks with their respective package lists

# Adjusted function to assign packages to trucks
def assign_packages_to_trucks(trucks, package_hash_map):
    for truck in trucks:
        not_delivered = [package_hash_map.lookup(package_id) for package_id in truck.packages]
        print(f"Truck {truck.truck_id} packages before delivery:", not_delivered)  # Debugging line
        for package_id in truck.packages:
            package = package_hash_map.lookup(package_id)

            if package is None:
                print(f"Warning: Package ID {package_id} not found in hash map.")
                continue

            if package:
                # If the package is found, load it onto the truck and update its status
                truck.load_package(package)
                package.update_status('en_route')
            else:
                # If the package is not found, print an error message
                print(f"Package ID {package_id} not found in hash map.")

# Call the function to assign packages to trucks
assign_packages_to_trucks(trucks, package_hash_map)

def distance_in_between(index1, index2, distance_data):
    try:
        distance = distance_data[index1][index2]
        if distance == '':
            distance = distance_data[index2][index1]
        return float(distance)
    except IndexError as e:
        print(f"IndexError accessing distance_data with indices {index1}, {index2}: {e}")
        return None

    
    
    # Returning None to indicate that an index was out of range



def format_address_for_lookup(address):
    # Example: Just use the street part of the address
    return address.split(',')[0].strip()

def extract_address_index(address, address_data):
    formatted_address = format_address_for_lookup(address).lower().strip()
    # print(f"Looking up index for: '{formatted_address}'")  # Debug print
    for index, name, addr in address_data:
        addr = addr.lower().strip()  # Ensure consistent formatting
        # print(f"Checking against: '{addr}'")  # Debug print
        if formatted_address == addr:
            return int(index) - 1  # Adjust for zero-based index if needed
    print(f"Address not found in data: '{formatted_address}'")
    return None


def calculate_distance(address1, address2, address_data, distance_data):
    index1 = extract_address_index(address1, address_data)
    index2 = extract_address_index(address2, address_data)
    
    if index1 is None or index2 is None:
        print(f"Error: One of the addresses was not found. Address 1: {address1} (index {index1}), Address 2: {address2} (index {index2})")
        return 0

    distance = distance_data[index1][index2]
    if distance == '':
        distance = distance_data[index2][index1]

    return float(distance)


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
            break  # No more reachable packages

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

# Call the function for each truck
for truck in [ups1_truck, ups2_truck, ups3_truck]:
    deliver_packages(truck, package_hash_map, ups_address_data, ups_distance_data)




def determine_package_status(package, current_time, trucks):
    truck_id = package.truck_id  # This assumes that each package has an associated truck_id
    truck = next((t for t in trucks if t.truck_id == truck_id), None)  # Find the truck for this package

    if truck:
        truck_start_time = datetime.strptime(truck.start_time, '%I:%M %p')

        if current_time < truck_start_time:
            return 'at_hub'  # Truck hasn't left yet

        if not package.expected_delivery_time:
            return 'at_hub'

        expected_delivery_dt = datetime.strptime(package.expected_delivery_time, '%I:%M %p')
        if truck_start_time <= current_time < expected_delivery_dt:
            return 'en_route'
        elif current_time >= expected_delivery_dt:
            return 'delivered'
    else:
        # If no truck is associated with the package, default to 'at_hub'
        return 'at_hub'


def query_status(package_hash_map, trucks):
    print("Western Governors University Parcel Service (WGUPS)")
    total_miles = sum(truck.mileage for truck in trucks)
    print(f"Total miles for all deliveries: {total_miles:.2f}")

    while True:
        user_input = input("Enter 'time' to check package statuses at a specific time, 'package' to check a single package, or 'exit' to quit: ").lower()

        if user_input == 'exit':
            break

        elif user_input == 'time':
            time_str = input("Enter the time (HH:MM AM/PM): ")
            try:
                specified_time = datetime.strptime(time_str, '%I:%M %p')
                for package_id in range(1, 41):
                    package = package_hash_map.lookup(package_id)
                    if package:
                        package_status_at_time = determine_package_status(package, specified_time, trucks)
                        # print(f"Package {package.package_id} status at {time_str}: {package_status_at_time}, Address: {package.address}, City: {package.city}, Zip: {package.zipcode}, Weight: {package.weight}, Deadline: {package.deadline}")
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
                    print(f"Package {package.package_id}: Address - {package.address}, City - {package.city}, Zip - {package.zipcode}, Weight - {package.weight}, Status - {package.status}, Deadline - {package.deadline}")
                else:
                    print("Package not found.")
            except ValueError:
                print("Please enter a numeric Package ID.")


print(f"Truck 1 delivery schedule: {ups1_truck.delivery_schedule}")

package1 = package_hash_map.lookup(1)
print(f"Package 1 status after deliveries: {package1.status}")



query_status(package_hash_map, trucks)

# Call the UI function at the end of your main.py
# def track_package():
#     while True:
#         try:
#             package_id = int(input("Enter the package ID to track (0 to exit): "))
#             if package_id == 0:
#                 break
#             package = package_hash_map.lookup(package_id)
#             if package:
#                 print(f"Package ID {package_id}: {package}")
#             else:
#                 print(f"Package ID {package_id} not found.")
#         except ValueError:
#             print("Please enter a valid package ID.")

# track_package()