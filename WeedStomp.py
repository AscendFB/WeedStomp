#!/usr/bin/env python
"""
"""
import os
import json
import base64
import requests
import numpy as np
import CeleryPy
import ENV
from time import sleep
from CeleryPy import log
from sequence_writer import Sequence






class WeedStomp(object):

    def __init__(self):
        """Set initial attributes."""
        self.plants = {'known': [], 'save': [],
                       'remove': [], 'safe_remove': []}
        self.weed_sequence = {'seq_id': []}
        self.seq = {'all_sequences' : []}
        self.sorted_coords = {'sorted':[]}
        self.found_sequence=0
        self.search_sequence_counter=0
        self.sequence_done=False
        self.seq_id_as_int = 0

        
        self.sequences = []
        self.weed_sequence = []

        # API requests setup
        try:
            api_token = os.environ['API_TOKEN']
        except KeyError:
 #           api_token = 'x.eyJpc3MiOiAiLy9zdGFnaW5nLmZhcm1ib3QuaW86NDQzIn0.x'
            api_token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ1bmtub3duIiwic3ViIjoxNywiaWF0IjoxNTE3Njc4NjYwLCJqdGkiOiJhZDNhNmY1OS0zOGM4LTQ5NjctODdhZC03ZjQ4NjQ1MmQ3OGQiLCJpc3MiOiIvL215LmZhcm1ib3QuaW86NDQzIiwiZXhwIjoxNTIxMTM0NjYwLCJtcXR0IjoiYnJpc2stYmVhci5ybXEuY2xvdWRhbXFwLmNvbSIsImJvdCI6ImRldmljZV8xNyIsInZob3N0IjoidmJ6Y3hzcXIiLCJtcXR0X3dzIjoid3NzOi8vYnJpc2stYmVhci5ybXEuY2xvdWRhbXFwLmNvbTo0NDMvd3MvbXF0dCIsIm9zX3VwZGF0ZV9zZXJ2ZXIiOiJodHRwczovL2FwaS5naXRodWIuY29tL3JlcG9zL2Zhcm1ib3QvZmFybWJvdF9vcy9yZWxlYXNlcy9sYXRlc3QiLCJpbnRlcmltX2VtYWlsIjoiaGVoZTEyMzRAaG90bWFpbC5kZSIsImZ3X3VwZGF0ZV9zZXJ2ZXIiOiJERVBSRUNBVEVEIiwiYmV0YV9vc191cGRhdGVfc2VydmVyIjoiaHR0cHM6Ly9hcGkuZ2l0aHViLmNvbS9yZXBvcy9GYXJtQm90L2Zhcm1ib3Rfb3MvcmVsZWFzZXMvOTUxMDc2NSJ9.p5wp-F54ke4Ftdn2Q-mbrgl--ZeMoW55YfmiSF_CCflkdDhb_GY9S_kfpHYeuruxyv0fcu010M5-k9QrT2JSFGUUDcIIBn2XOhI_TFAo0GalC3i--4_m6EwgLkX1_zOQHfuPKzKtK3EhSH9f4fi2x3PmXxE3kI0ule07Z3gyEpmW8mf-FgaDoB_rT8sLtIxC90AkL4zcLo2A1F2Atf734rVu_rq8ZN9C6DxQ-9he3OIdf62_FaSUgknxUy45b9aE4CxpEI243i9kKzOMRC_hMNBJet-FB1fAteACNIRiSWq2tL_aa0gJ-2_BzQJ_2Q-9KF9xAETv9wk2f9MiKDQM7Q'
        try:
            encoded_payload = api_token.split('.')[1]
            encoded_payload += '=' * (4 - len(encoded_payload) % 4)
            json_payload = base64.b64decode(encoded_payload).decode('utf-8')
            server = json.loads(json_payload)['iss']
        except:  # noqa pylint:disable=W0702
            server = '//my.farmbot.io'
        self.api_url = 'http{}:{}/api/'.format(
            's' if 'localhost' not in server else '', server)
        self.headers = {'Authorization': 'Bearer {}'.format(api_token),
                        'content-type': "application/json"}
        self.errors = {}

    def api_get(self, endpoint):
        """GET from an API endpoint."""
        response = requests.get(self.api_url + endpoint, headers=self.headers)
        self.api_response_error_collector(response)
        self.api_response_error_printer()
        return response

    def api_response_error_collector(self, response):
        """Catch and log errors from API requests."""
        self.errors = {}  # reset
        if response.status_code != 200:
            try:
                self.errors[str(response.status_code)] += 1
            except KeyError:
                self.errors[str(response.status_code)] = 1

    def api_response_error_printer(self):
        """Print API response error output."""
        error_string = ''
        for key, value in self.errors.items():
            error_string += '{} {} errors '.format(value, key)
        print(error_string)


 
    def load_weeds_from_web_app(self):
        """Download known Weeds from the FarmBot Web App API."""
        response = self.api_get('points')
        app_points = response.json()
        if response.status_code == 200:
            plants = []
            for point in app_points:
                if point['name'] == 'Weed':
                    plants.append({
                        'x': point['x'],
                        'y': point['y'],})
            self.plants['known'] = plants
            self.sorted_coords = sorted(self.plants['known'], key=lambda x:sorted(x.keys()))
            print (self.sorted_coords)
            print (plants)

          

    def load_sequences_from_app(self):
        response = self.api_get('sequences')
        app_sequences = response.json()
        if response.status_code == 200:
            self.sequences = []
            self.weed_sequence = []
            for seq in app_sequences:
                if seq['name'] == 'FW_WeedStomp':
                  self.weed_sequence.append(seq['id'])
                  self.found_sequence=1
        a.check_if_sequence_found()

                  
                 

    def check_if_sequence_found(self):
        if self.found_sequence == 0:    
                self.weed_sequence[:] = []
                log("No weeding sequence found. I will create one.",message_type ='info', title = 'WeedStomp')
                a.create_sequence()
                self.search_sequence_counter +=1                                                                              
        if self.found_sequence == 1:
                [int(i) for i in self.weed_sequence]
                self.seq_id_as_int = int(i)
                if self.sequence_done == False:
                    log("Found the weeding sequence.",message_type ='info', title = 'WeedStomp')
                    a.loop_plant_points()


                
               

           
    def loop_plant_points(self): 
#       count = 0                               #Counter to limit the points for tests.      
        for plant in self.sorted_coords:
#               if count < 3:
                   print ("moving to points")
                   CeleryPy.move_absolute(
                    location=[plant['x'],plant['y'] ,0],
                    offset=[0, 0, 0],
                    speed=800)
                   print(plant['x'],plant['y'])
                   CeleryPy.execute_sequence(sequence_id= self.seq_id_as_int)
                   print(self.seq_id_as_int)
                   self.sequence_done = True
 #                 count +=1

  
          
    def count_downloaded_plants(self):
        plant_count = len(self.plants['known'])
        log( "{} weeds were detected." .format(plant_count)
            ,message_type= 'info',title= 'WeedStomp')

   

    def create_sequence(self):

        def upload(sequence):
            r = requests.post(self.api_url + 'sequences', data=json.dumps(sequence), headers=self.headers)
            print(r, r.json())
            self.response = r

        if self.search_sequence_counter <3:
         with Sequence("FW_WeedStomp", "green", upload) as s:
            s.write_pin(number = 10,value = 1,mode = 0)
            s.wait(milliseconds=200)
            s.write_pin(number = 10,value = 0,mode = 0)
        if self.response.status_code == 422:
            log("Cant create sequence because this name already exists. Check for upper- and lowercases.",message_type ='info', title = 'WeedStomp')
        if self.response.status_code == 200:
            log("Created a sequence named FW_WeedStomp.",message_type ='info', title = 'WeedStomp')
            CeleryPy.sync()
            a.load_sequences_from_app()
        else:
            print("There was an Error creating the sequence.")
        




if __name__ == "__main__":
    a = WeedStomp()

    log("Starting", message_type= 'info',title='WeedStomp')

    a.load_weeds_from_web_app()
    a.count_downloaded_plants()
    a.load_sequences_from_app()

