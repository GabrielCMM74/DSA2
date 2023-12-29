'''
Name: Gabriel Coello
Student ID: 011062646
'''
import csv
import datetime
from ups_package import Package
# from ups_truck import Truck
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


print(ups_address_data[:5])  # Print first 5 rows
print(ups_distance_data[:5])  # Print first 5 rows
print(ups_package_data[:5])  # Print first 5 rows