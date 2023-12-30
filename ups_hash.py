# Creating the Hash Table
class HashMap:
    def __init__(self, size=101):
        self.size = size
        self.table = [[] for _ in range(size)]
        # This inner list is to help hold package details in case of collisions


    def hash(self, key):
        if not isinstance(key, int):
            raise TypeError(f"Hash key must be an integer, got {type(key)}")
        return key % self.size
    
    
    def insert(self, package_id, details):
        index = self.hash(package_id)
        # Appends the package details to the list at the calc index
        self.table[index].append(details)

    
    def lookup(self, package_id):
        index = self.hash(package_id)
        # Searches for the package by ID within the list at the index
        for package in self.table[index]:
            if package.package_id == package_id:
                return package
        return None # If package not found
    

    def delete(self, package_id):
        index = self.hash(package_id)
        # Iterate over the list at the index to find the package with the given package_id
        for i, package in enumerate(self.table[index]):
            if package.package_id == package_id:
                # Remove the package from the list using its index
                del self.table[index][i]
                return True  # Return True to indicate successful deletion

        return False  # Return False if the package was not found   