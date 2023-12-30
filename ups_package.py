# This is package Class and attributes
class Package:
    # Class variable holding valid statuses for all package instances
    statuses = ['at_hub', 'en_route', 'delivered']

    def __init__(self, package_id, address, deadline, city, state, zipcode, weight, status, special_notes):
        self.package_id = package_id
        # Format the address for consistency with the address_to_index mapping
        self.address = address.lower().strip()
        self.deadline = deadline
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.weight = weight
        self.status = status if status in self.statuses else 'at_hub'
        self.special_notes = special_notes


    def __str__(self):
        # String representation of the package, key information.
        return f"Package {self.package_id} is on route to {self.address} in {self.city} city. The status is {self.status}"


    def update_status(self, new_status):
        # Updates the package's status if the new status is correct.
        if new_status in self.statuses:
            self.status = new_status
        else:
            # Raises an error if an invalid status is provided.
            raise ValueError(f"{new_status} is an incorrect status")

# test = Package(13131, "123 south st", "3:45am", "Bronx", 281044, "44lbs", "en_route")
# test.update_status('at_hub')
# print(test)