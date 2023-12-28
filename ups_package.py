# This is package Class and attributes 

class Package: 
    def __init__(self, package_id, address, deadline, city, zipcode, weight, status):
        self.package_id = package_id
        self.address = address
        self.deadline = deadline
        self.city = city
        self.zipcode = zipcode
        self.weight = weight
        self.status = status

    def __str__(self):
        return f"Package {self.package_id} is on route to {self.address} at {self.city} city. The status is {self.status}"
    
    def update_status(self, new_status):
        
        statuses = ['at_hub', 'en_route', 'delivered']
        if new_status in statuses:
            self.status = new_status
        else:
            raise ValueError(f"{new_status} is an incorrect status")

test = Package(13131, "123 south st", "3:45am", "Bronx", 281044, "44lbs", "en_route")
print(test.update_status('at_hub'))