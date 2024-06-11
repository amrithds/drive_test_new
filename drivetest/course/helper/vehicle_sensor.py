
import time
import requests
from bs4 import BeautifulSoup
import json


class VehicleSensor():
    START_RANGE = 28
    MAX_RANGE = 250

    @classmethod
    def IP_in_range(cls, ip_address:str) -> bool:
        try:
            data = cls.fetch_data(ip_address)
        except Exception as e:
            return False
        
        distance = data['distance']
        if cls.START_RANGE <= distance and distance <= cls.MAX_RANGE:
            return True
        
        return False
    
    @classmethod
    def distance_ip_addrs(cls, ip_address:str) -> bool:
        try:
            data = cls.fetch_data(ip_address)
        except Exception as e:
            return False
        distance = data['distance']
        return distance

    
    @classmethod
    def fetch_data(cls, ip_address: str):
        url = f'http://{ip_address}/'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.text
                soup = BeautifulSoup(data, 'html.parser')

                # Extract the text from the <h1> tag
                distance = soup.find('h1').text

                # Remove "Distance: " and " cm" from the extracted text
                distance_value = distance.replace('Distance: ', '').replace(' cm', '')

                # Create a dictionary to hold the data
                data = {'ip_address':ip_address ,'distance': float(distance_value)} # Convert distance value to float

                # Convert the dictionary to JSON
                json_data = json.dumps(data)

                data = json.loads(json_data)

                return data 
            else:
                print(f"Failed to fetch data. Status code: {response.status_code}")
                raise Exception(f"Failed to fetch data. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error fetching data: {e}")
            raise e