#databaseURL='http://localhost:9000/?ns=pydb-c9033'

from __future__ import print_function
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative

import argparse


import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents
cred = credentials.Certificate('C:/Users/DELL/Downloads/pydb-c9033-firebase-adminsdk-23j6e-e98f84324d.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    #local host database url 
    'databaseURL': "http://localhost:9000/?ns=pydb-c9033"
    
    #realtime database url 
    #databaseURL='https://pydb-c9033-default-rtdb.firebaseio.com/'

})

ref = db.reference('server')

parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect',
                    help="Vehicle connection target string..")
args = parser.parse_args()





connection_string = args.connect
sitl = None


# Start SITL if no connection string specified
if not connection_string:
    import dronekit_sitl
    sitl = dronekit_sitl.start_default()
    connection_string = sitl.connection_string()


# Connect to the Vehicle
print('Connecting to vehicle on: %s' % connection_string)
vehicle = connect(connection_string, wait_ready=True)

# Get Vehicle Home location - will be `None` until first set by autopilot
while not vehicle.home_location:
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    if not vehicle.home_location:
        print ("no way home")


def mode_callback(self, attr_name, value):
     
     users_ref = ref.child('drone1hex')
     users_ref.child('status').set({
         'mode':value.name
     })


vehicle.add_attribute_listener('mode', mode_callback)


 #Callback to print the location in global frames. 'value' is the updated value
def location_callback(self, attr_name, value):
     
     users_ref = ref.child('drone1hex')
     users_ref.child('data').set({
         'lat': value.lat,
        'lon': value.lon,
        'alt': value.alt,
        })
     #print(ref.get())



print ("The Mode is", vehicle.mode.name)

users_ref = ref.child('drone1hex')
users_ref.child('status').set({
         'mode':vehicle.mode.name
     })

#Command from the Client Application
users_ref = ref.child('drone1hex')
users_ref.child('command').set({
         'RTL': "false"
     })



 # Add a callback `location_callback` for the `global_frame` attribute.
vehicle.add_attribute_listener('location.global_frame', location_callback)


    # Wait 2s so callback can be notified before the observer is removed
time.sleep(2)

    # Remove observer - specifying the attribute and previously registered callback function
#vehicle.remove_message_listener('location.global_frame', location_callback)





# Close vehicle object before exiting script
print("Close vehicle object")
#vehicle.close()

def listener(event):
      # can be 'put' or 'patch'
    if event.data == 'true':
        vehicle.mode = VehicleMode("RTL")
        print(vehicle.mode.name) 
        users_ref = ref.child('drone1hex')
        users_ref.child('command').set({
         'RTL': "false"
     })
         # relative to the reference, it seems
    print(event.data) 


firebase_admin.db.reference('server/drone1hex/command/RTL').listen(listener)
# Shut down simulator if it was started.
if sitl:
    sitl.stop()