# Created Truck class with defaults 
class Truck:
    def __init__(self, truck_id, status='at_hub', start_time='08:00 AM', 
                    current_location=None, driver=None, route=None, 
                    delivery_schedule=None, total_delivery_time=0, special_notes=None, 
                    packages=None, capacity=16, average_speed=18, mileage=0):
        self.truck_id = truck_id
        self.status = status
        self.start_time = start_time
        # If no current_location is provided, default is to 'Hub'
        self.current_location = current_location if current_location else 'Hub'
        self.driver = driver
        # Initialize route to an empty list if not provided
        self.route = route if route else []
        # Initialize delivery_schedule to an empty dictionary if not provided
        self.delivery_schedule = delivery_schedule if delivery_schedule else {}
        self.total_delivery_time = total_delivery_time
        # Initialize special_notes to an empty list if not provided
        self.special_notes = special_notes if special_notes else []
        
        # If packages is None, initialize to an empty list to avoid mutable default argument issues
        self.packages = packages if packages is not None else []
        self.capacity = capacity
        self.average_speed = average_speed
        self.mileage = mileage
        
    def update_mileage(self, additional_miles):
        self.mileage += additional_miles

    def __str__(self):
        return f"Truck {self.truck_id}: {self.status}, {len(self.packages)} packages, Total mileage: {self.mileage} miles"
    
    def load_package(self, package):
        if len(self.packages) < self.capacity:
            # Do NOT append the package object to self.packages
            # Update package status or handle other loading logic here
            print(f"Loaded package ID {package.package_id} onto truck {self.truck_id}.")
        else:
            print(f"Truck {self.truck_id} is full and cannot take package {package.package_id}.")
