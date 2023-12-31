# This is package Class and attributes
from datetime import datetime

EOD_TIME = '05:00 PM'  # Define End of Day time if not already defined

class Package:
    statuses = ['at_hub', 'en_route', 'delivered']

    def __init__(self, package_id, address, city, state, zipcode, deadline, weight, status, special_notes, delivery_time):
        self.package_id = package_id
        self.address = address.lower().strip()
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.deadline = deadline  # This should be a string in 'HH:MM AM/PM' format or 'EOD'
        self.weight = weight
        self.status = status if status in self.statuses else 'at_hub'
        self.special_notes = special_notes
        self.delivery_time = delivery_time  # This should be a string in 'HH:MM AM/PM' format when updated

    def __str__(self):
        # String representation with detailed package information
        return (f"Package ID: {self.package_id}, Address: {self.address}, City: {self.city}, State: {self.state}, " +
                f"Zipcode: {self.zipcode}, Weight: {self.weight}, Status: {self.status}, " +
                f"Delivery Deadline: {self.deadline}, Delivery Time: {self.delivery_time}, " +
                f"Special Notes: {self.special_notes}")

    def update_status(self, new_status):
        if new_status in self.statuses:
            self.status = new_status
        else:
            raise ValueError(f"{new_status} is an incorrect status")

    def update_delivery_time(self, time):
        # Assuming time is provided as a string in 'HH:MM AM/PM' format
        if time.upper() == 'EOD':
            time = EOD_TIME
        try:
            # Try to parse the time to check if it's valid
            parsed_time = datetime.strptime(time, '%I:%M %p')
            self.delivery_time = parsed_time.strftime('%I:%M %p')
        except ValueError:
            # If the time format is invalid, raise an error
            raise ValueError(f"The time {time} is not in the correct format (HH:MM AM/PM).")
    

    def get_deadline_datetime(self):
        # Convert the deadline string to a datetime object
        if self.deadline.upper() == 'EOD':
            return datetime.strptime(EOD_TIME, '%I:%M %p')
        else:
            return datetime.strptime(self.deadline, '%I:%M %p')

    def is_delivered_on_time(self):
        if self.delivery_time and self.deadline:
            delivery_time_obj = datetime.strptime(self.delivery_time, '%I:%M %p')
            deadline_obj = self.get_deadline_datetime()
            return delivery_time_obj <= deadline_obj
        return False





# class Package:
#     # Class variable holding valid statuses for all package instances
#     statuses = ['at_hub', 'en_route', 'delivered']

#     def __init__(self, package_id, address, deadline, city, state, zipcode, weight, status, special_notes, delivery_time):
#         self.package_id = package_id
#         # Format the address for consistency with the address_to_index mapping
#         self.address = address.lower().strip()
#         self.deadline = deadline
#         self.city = city
#         self.state = state
#         self.zipcode = zipcode
#         self.weight = weight
#         self.status = status if status in self.statuses else 'at_hub'
#         self.special_notes = special_notes
#         self.delivery_time = delivery_time


#     def __str__(self):
#         # String representation of the package, key information.
#         return f"Package {self.package_id} is on route to {self.address} in {self.city} city. The status is {self.status}"


#     def update_status(self, new_status):
#         # Updates the package's status if the new status is correct.
#         if new_status in self.statuses:
#             self.status = new_status
#         else:
#             # Raises an error if an invalid status is provided.
#             raise ValueError(f"{new_status} is an incorrect status")

# # test = Package(13131, "123 south st", "3:45am", "Bronx", 281044, "44lbs", "en_route")
# # test.update_status('at_hub')
# # print(test)