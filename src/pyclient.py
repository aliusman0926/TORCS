import sys
import argparse
import socket
import driver
import pandas as pd
import joblib
from sklearn.preprocessing import PolynomialFeatures


if __name__ == '__main__':
    pass

# Load the models
modelAccel = joblib.load('../training/models/acc_controller.sav')

modelSteer = joblib.load('../training/models/steering_controller.sav')

modelBrake = joblib.load('../training/models/brake_controller.sav')

modelGear = joblib.load('../training/models/gear_controller.sav')

# Configure the argument parser
parser = argparse.ArgumentParser(description = 'Python client to connect to the TORCS SCRC server.')

parser.add_argument('--host', action='store', dest='host_ip', default='localhost',
                    help='Host IP address (default: localhost)')
parser.add_argument('--port', action='store', type=int, dest='host_port', default=3001,
                    help='Host port number (default: 3001)')
parser.add_argument('--id', action='store', dest='id', default='SCR',
                    help='Bot ID (default: SCR)')
parser.add_argument('--maxEpisodes', action='store', dest='max_episodes', type=int, default=1,
                    help='Maximum number of learning episodes (default: 1)')
parser.add_argument('--maxSteps', action='store', dest='max_steps', type=int, default=0,
                    help='Maximum number of steps (default: 0)')
parser.add_argument('--track', action='store', dest='track', default=None,
                    help='Name of the track')
parser.add_argument('--stage', action='store', dest='stage', type=int, default=3,
                    help='Stage (0 - Warm-Up, 1 - Qualifying, 2 - Race, 3 - Unknown)')

arguments = parser.parse_args()

# Print summary
print('Connecting to server host ip:', arguments.host_ip, '@ port:', arguments.host_port)
print('Bot ID:', arguments.id)
print('Maximum episodes:', arguments.max_episodes)
print('Maximum steps:', arguments.max_steps)
print('Track:', arguments.track)
print('Stage:', arguments.stage)
print('*********************************************')

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error as msg:
    print('Could not make a socket.')
    sys.exit(-1)

# one second timeout
sock.settimeout(1.0)

shutdownClient = False
curEpisode = 0

verbose = False

d = driver.Driver(arguments.stage)

while not shutdownClient:
    while True:
        print('Sending id to server: ', arguments.id)
        buf = arguments.id + d.init()
        print('Sending init string to server:', buf)
        try:
            sock.sendto(buf.encode(), (arguments.host_ip, arguments.host_port))
        except socket.error as msg:
            print("Failed to send data...Exiting...")
            sys.exit(-1)
            
        try:
            buf, addr = sock.recvfrom(1700)
            print('Received data from server:', buf.decode())
            if buf.decode().find("***identified***") >= 0:
                break
        except socket.error as msg:
            print("didn't get response from server...")


    currentStep = 0
    
    while True:
        # wait for an answer from server
        buf = None
        try:
            buf, addr = sock.recvfrom(1700)
        except socket.error as msg:
            print("didn't get response from server...")
        
        if verbose:
            print('Received: ', buf)
        
        if buf != None and buf.decode().find('***shutdown***') >= 0:
            d.onShutDown()
            shutdownClient = True
            print('Client Shutdown')
            break
        
        if buf != None and buf.decode().find('***restart***') >= 0:
            d.onRestart()
            print('Client Restart')
            break
        
        currentStep += 1
        if currentStep != arguments.max_steps:
            if buf != None:
                # Get sensor data
                sensors=d.parser.parse(buf.decode())

                # Get control data
                prevBreak=float(d.control.getBrake())
                tPos=float(sensors['trackPos'][0])
                angle=float(sensors['angle'][0])
                diff=abs(tPos)-abs(angle)
                buf2=buf
                buf2 = d.drive(buf2.decode())
                currBreak=float(d.control.getBrake())

                # Create a DataFrame to hold the sensor data
                column_names = ["S1", "S17","S9", "TPos","TAngle","PGear","RPM","PSpeed","DIff","PrevBreak","CurrBreak","PredictAccel","PredictGear","PredictSteer","PredictBrake"]
                df = pd.DataFrame(columns=column_names)
                df.loc[0]=[float(sensors['track'][1]),float(sensors['track'][17]),float(sensors['track'][9]),float(sensors['trackPos'][0]),float(sensors['angle'][0]),float(sensors['gear'][0]),float(sensors['rpm'][0]),float(sensors['speedX'][0]),diff,prevBreak,currBreak,float(d.control.getAccel()),float(d.control.getGear()),float(d.control.getSteer()),float(d.control.getBrake())]
                df.drop(columns = ['PredictSteer','PredictAccel','PredictGear'],inplace=True)
                dataset=df.values
                X= dataset[:, 0:-1]
                print(X)
                X=X.astype('float')

                # Use PolynomialFeatures to create polynomial features
                poly = PolynomialFeatures(degree=2, include_bias=False)
                # Transform the input data based on model
                poly_features = poly.fit_transform(X)

                # Use transformed data to predict and set control values
                Accel=modelAccel.predict(poly_features)
                Brake=modelBrake.predict(poly_features)
                Brake=Brake[0].round(1)
                Steer=modelSteer.predict(poly_features)
                Gear=modelGear.predict(X)
                Gear=Gear[0].round(1)

                # Set control values to TORCS buffer
                buf=d.control.toMsg()
                print(buf,'\n')

        else:
            buf = '(meta 1)'
        
        if verbose:
            print('Sending: ', buf)
        
        if buf != None:
            try:
                sock.sendto(buf.encode(), (arguments.host_ip, arguments.host_port))
            except socket.error as msg:
                print("Failed to send data...Exiting...")
                sys.exit(-1)
    
    curEpisode += 1
    
    if curEpisode == arguments.max_episodes:
        shutdownClient = True

sock.close()
