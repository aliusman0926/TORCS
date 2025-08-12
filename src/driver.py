import msgParser
import carState
import carControl

class Driver(object):
    def __init__(self, stage):
        '''Constructor'''
        self.WARM_UP = 0
        self.QUALIFYING = 1
        self.RACE = 2
        self.UNKNOWN = 3
        self.stage = stage
        self.braking=False
        
        self.parser = msgParser.MsgParser()
        self.state = carState.CarState()
        self.control = carControl.CarControl()
        
        self.steer_lock = 0.785398 # Lock Steering (for counter-steering)
        self.max_speed = 130 # Top-Speed (for stability)
        self.prev_rpm = None # Previous RPM (for gear shifting)
    
    def init(self):
        '''Return init string with rangefinder angles'''
        self.angles = [0 for x in range(19)]
        
        for i in range(5):
            self.angles[i] = -90 + i * 15
            self.angles[18 - i] = 90 - i * 15
        
        for i in range(5, 9):
            self.angles[i] = -20 + (i-5) * 5
            self.angles[18 - i] = 20 - (i-5) * 5
        
        return self.parser.stringify({'init': self.angles})
    
    def drive(self, msg):
        self.state.setFromMsg(msg)
        self.speed()
        self.steer()
        self.gear()
        
        return self.control.toMsg()
    
    def steer(self):
        '''Steer the car based on the track position and angle'''
        # Get the track position and angle
        angle = self.state.angle
        dist = self.state.trackPos

        trackPos=self.state.getTrack()
        # Steer to remain on the track
        if trackPos[17]<7.5:
            self.control.setSteer((angle*1.5 - dist)/self.steer_lock)
        elif trackPos[1]<7.5:
            self.control.setSteer((angle*1.5 - dist)/self.steer_lock)
        else:
            self.control.setSteer((angle - dist)/self.steer_lock)
    
    def gear(self):
        '''Change the gear based on the RPM and current gear'''
        rpm = self.state.getRpm()
        gear = self.state.getGear() or 0
        # Start in gear 1
        if gear is None:
            gear = 0
        
        # Start with gear upshift
        if self.prev_rpm == None:
            up = True
        else:
            # If the previous RPM is greater than the current RPM, we are downshifting
            if (self.prev_rpm - rpm) < 0:
                up = True
            else:
                up = False
        
        # Gear change thresholds (vary based on cars)
        if up and rpm > 6000:
            gear += 1
        if not up and rpm < 2000:
            gear -= 1
        
        self.control.setGear(gear)
    
    def speed(self):
        '''Set the speed based on the track conditions'''
        speed = self.state.getSpeedX()
        accel = self.control.getAccel()
        trackPos=self.state.getTrack()
        angle = self.state.angle
        dist = self.state.trackPos
        diff=abs(dist)-abs(angle)

        # Conditions for braking (Turns)
        if ((trackPos[9]>160 and trackPos[9]<=180) and (trackPos[17]<7.5 or trackPos[1]<7.5) and speed>80 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.0)
        elif ((trackPos[9]>140 and trackPos[9]<=160) and (trackPos[17]<7.5 or trackPos[1]<7.5) and self.braking==False and speed>80 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.4)
        elif ((trackPos[9]>120 and trackPos[9]<=140) and (trackPos[17]<7.5 or trackPos[1]<7.5) and self.braking==False and speed>80 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.75)
        elif ((trackPos[9]>100 and trackPos[9]<=120) and (trackPos[17]< 7.5 or trackPos[1]<7.5) and self.braking==False and speed>80 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.75)
        elif ((trackPos[9]>80 and trackPos[9]<=100) and (trackPos[17]<7.5 or trackPos[1]<7.5) and self.braking==False and speed>80 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.75)
        elif ((trackPos[9]>60 and trackPos[9]<=80) and (trackPos[17]<7.5 or trackPos[1]<7.5) and self.braking==False and speed>80 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.75)
        elif (trackPos[9]<=60 and (trackPos[17]<7.5 or trackPos[1]<7.5) and self.braking==False and speed>80 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.8)

        # Conditions for speeding up (Straights)
        elif ((trackPos[9]>160 and trackPos[9]<=180) and (trackPos[17]>=7.2 or trackPos[1]>=7.2) and speed>90 and diff>0.0  and self.braking==False):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.0)
        elif ((trackPos[9]>140 and trackPos[9]<=160) and (trackPos[17]>=7.2 or trackPos[1]>=7.2) and self.braking==False and speed>90 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.0)
        elif ((trackPos[9]>120 and trackPos[9]<=140) and (trackPos[17]>=7.2 or trackPos[1]>=7.2) and self.braking==False and speed>90 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.0)
        elif ((trackPos[9]>100 and trackPos[9]<=120) and (trackPos[17]>=7.2 or trackPos[1]>=7.2) and self.braking==False and speed>90 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.0)
        elif ((trackPos[9]>80 and trackPos[9]<=100) and (trackPos[17]>=7.2 or trackPos[1]>=7.2) and self.braking==False and speed>90 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.4)
        elif ((trackPos[9]>60 and trackPos[9]<=80) and (trackPos[17]>=7.2 or trackPos[1]>=7.2) and self.braking==False and speed>90 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.7)
        elif (trackPos[9]<=60 and (trackPos[17]>=7.2 or trackPos[1]>=7.2) and self.braking==False and speed>90 and diff>0.0):
            self.braking=True
            speed=self.max_speed
            self.control.setBrake(0.75)
            
        else:
            self.braking=False
            self.control.setBrake(0.0)

        # Conditions for acceleration
        if speed < self.max_speed and self.braking==False:
            self.control.setBrake(0.0)
            accel += 0.1
            if accel > 1:
                accel = 1.0
        else:
            accel -= 0.2    
            if self.braking==True:
                accel=0.2          
            if accel < 0:
                accel = 0.0
        wheelSpin=self.state.getWheelSpinVel()
        
        self.control.setAccel(accel)
            
        
    def onShutDown(self):
        pass
    
    def onRestart(self):
        pass
        