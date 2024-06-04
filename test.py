import json
import psycopg2

# Define a mock class to contain the function and test data
class MockClass:
    def __init__(self, photos_data):
        self.photos_data = photos_data
        self.json_data = {}

    def write_json(self):
        # Organize and write to JSON
        organized_data = {}
        for sku, urls in self.photos_data.items():
            sorted_urls = sorted(urls, key=lambda x: x[0])  # Sort by suffix
            organized_data[sku] = {'url': json.dumps([url for _, url in sorted_urls])}  # Convert to JSON array

        # Store the organized data into the instance variable
        self.json_data = {'photos': organized_data}
        print("Photos JSON prepared")
        return self.json_data

    def update_database(self):
        # Setup the database connection
        connection = psycopg2.connect(
            dbname="postgres",
            user="bluurr",
            password="548406",
            host="127.0.0.1",
            port="5432"
        )
        cursor = connection.cursor()

        for sku, data in self.json_data['photos'].items():
            # Check if the SKU exists in the database
            cursor.execute('SELECT sku FROM inventory.obt_inventory WHERE sku = %s', (sku,))
            row = cursor.fetchone()
            if row:
                # Update the URL for the existing SKU
                cursor.execute('UPDATE inventory.obt_inventory SET photos = %s WHERE sku = %s', (data['url'], sku))
                print(f"Updated SKU {sku} with URL {data['url']}")
            else:
                # Optionally, handle the case where SKU does not exist
                print(f"SKU {sku} does not exist in the database")
        connection.commit()

        # Print out the updated database content for verification
        cursor.execute('SELECT * FROM inventory.obt_inventory')
        rows = cursor.fetchall()
        for row in rows:
            print(row)

        # Close the database connection
        cursor.close()
        connection.close()

    def use_json_data(self):
        # Function to use the JSON data in some way
        print("Using JSON data in a separate function:")
        print(json.dumps(self.json_data, indent=4))
        # Additional processing can be added here

# Test data for the write_json function
test_data = {
    'photos_data': {
        'ABC123': [(1, 'http://example.com/photo1.jpg'), (2, 'http://example.com/photo2.jpg')],
        'ABC456': [(1, 'http://example.com/photo3.jpg'), (3, 'http://example.com/photo4.jpg'), (2, 'http://example.com/photo5.jpg')],
        'ABC789': [(2, 'http://example.com/photo6.jpg'), (1, 'http://example.com/photo7.jpg')],
    }
}

# Instantiate the mock class with test data
mock_instance = MockClass(test_data['photos_data'])

# Call the function to test it and get the JSON data
output = mock_instance.write_json()

# Use the JSON data to update the database
mock_instance.update_database()
