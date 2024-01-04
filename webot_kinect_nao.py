import numpy as np
import math
import pika
import json
import warnings
from controller import Supervisor,Robot,Node
import controller


def callback(ch, method, properties, body):
     joint_data_dict = json.loads(body.decode('utf-8'))
     data_dict = {}
    # Process the received joint data dictionary
     for joint in joint_data_dict:
        jointType,Position=joint.items()
        data_dict[jointType[1]]=Position[1]
     Move(data_dict)
     supervisor.step(10)



def Finger(point1,point2):
    if abs(point1[0]-point2[0])<0.1   :
        return 1
    return 0
def getAngle(Point1,Point2):
    x=Point1[0]-Point2[0]
    y=Point1[1]-Point2[1]
    Pitch=math.atan(y/x)
    Roll=math.atan(x/y)
    return Pitch,Roll
def getAngle1(point1,point2):
    y=point1[1]-point2[1]
    z=point1[2]-point2[2]
    Pitch=math.atan(z/y)
    return Pitch
def getElbowYaw(HandTip,Thumb):
    dot_product = np.dot(HandTip,Thumb)
    # Calculate the magnitudes of the vectors
    magnitude_hand_tip = np.linalg.norm(HandTip)
    magnitude_thumb = np.linalg.norm(Thumb)
    # Calculate the cosine of the angle
    cos_angle = dot_product / (magnitude_hand_tip * magnitude_thumb)
    # Calculate the angle in radians
    angle_radians = np.arccos(cos_angle)*-20
    print(angle_radians)
    return angle_radians
def Move(a):
    letfFinger=["LPhalanx1","LPhalanx2","LPhalanx3","LPhalanx4","LPhalanx5","LPhalanx6","LPhalanx7","LPhalanx8"]
    rightFinger=["RPhalanx1","RPhalanx2","RPhalanx3","RPhalanx4","RPhalanx5","RPhalanx6","RPhalanx7","RPhalanx8"]
    shoulderRight=np.array(a['ShoulderRight'])
    elbowRight=np.array(a['ElbowRight'])
    shoulderLeft=np.array(a['ShoulderLeft'])
    elbowLeft=np.array(a['ElbowLeft'])
    kneeRight=np.array(a['KneeRight'])
    ankelRight=np.array(a['AnkleRight'])
    kneeLeft=np.array(a['KneeLeft'])
    ankelLeft=np.array(a['AnkleLeft'])
    wirstRight=np.array(a['WristRight'])
    wirstLeft=np.array(a['WristLeft'])
    hipLeft=np.array(a['HipLeft'])
    hipRight=np.array(a['HipRight'])
    head=np.array(a['Head'])
    neck=np.array(a['Neck'])
    thumbLeft=np.array(a['ThumbLeft'])
    handTipLeft=np.array(a['HandTipLeft'])
    thumbRight=np.array(a['ThumbRight'])
    handTipRight=np.array(a['HandTipRight'])
    footLeft=np.array(a['FootLeft'])
    footRight=np.array(a['FootRight'])
    pitch,Roll=getAngle(shoulderRight,elbowRight)
    pitch1,Roll1=getAngle(shoulderLeft,elbowLeft)
    Pitch2=getAngle1(kneeRight,footRight)
    Pitch3=getAngle1(kneeLeft,footLeft)
    Roll2=getAngle1(elbowLeft,wirstLeft)
    Roll3=getAngle1(elbowRight,wirstRight)
    _,Roll4=getAngle(hipRight,kneeRight)
    _,Roll5=getAngle(hipLeft,kneeLeft)
    Pitch4=getAngle1(hipRight,ankelRight)
    Pitch5=getAngle1(hipLeft,ankelLeft)
    headPitch=getAngle1(neck,head)
    if abs(Pitch2)<0.5:
        Pitch2=getAngle1(kneeRight,hipRight)*-1
    if abs(Pitch3)<0.5:
        Pitch3=getAngle1(kneeLeft,footRight)*-1
    motors["RShoulderRoll"].setPosition(np.clip(Roll,motors["RShoulderRoll"].getMinPosition(),motors["RShoulderRoll"].getMaxPosition()))
    motors["RShoulderPitch"].setPosition(np.clip(-pitch, motors["RShoulderPitch"].getMinPosition(), motors["RShoulderPitch"].getMaxPosition()))
    motors["LShoulderPitch"].setPosition(np.clip(pitch1, motors["LShoulderPitch"].getMinPosition(), motors["LShoulderPitch"].getMaxPosition()))
    motors["LShoulderRoll"].setPosition(np.clip(Roll1, motors["LShoulderRoll"].getMinPosition(), motors["LShoulderRoll"].getMaxPosition()))
    motors['RKneePitch'].setPosition(np.clip(-Pitch2, motors["RKneePitch"].getMinPosition(), motors["RKneePitch"].getMaxPosition()))
    motors['LKneePitch'].setPosition(np.clip(-Pitch3, motors["LKneePitch"].getMinPosition(), motors["LKneePitch"].getMaxPosition()))
    motors['LElbowRoll'].setPosition(np.clip(Roll2, motors['LElbowRoll'].getMinPosition(), motors['LElbowRoll'].getMaxPosition()))
    #motors['LWristYaw'].setPosition(getElbowYaw(handTipLeft,thumbLeft))
    motors['LHipPitch'].setPosition(np.clip(-Pitch5, motors['LHipPitch'].getMinPosition(), motors['LHipPitch'].getMaxPosition()))
    motors['RHipPitch'].setPosition(np.clip(-Pitch4, motors['RHipPitch'].getMinPosition(), motors['RHipPitch'].getMaxPosition()))
    motors['RHipRoll'].setPosition(np.clip(Roll4, motors['RHipRoll'].getMinPosition(), motors['RHipRoll'].getMaxPosition()))
    motors['LHipRoll'].setPosition(np.clip(Roll5, motors['LHipRoll'].getMinPosition(), motors['LHipRoll'].getMaxPosition()))
    motors['HeadPitch'].setPosition(np.clip(-2*headPitch, motors['HeadPitch'].getMinPosition(), motors['HeadPitch'].getMaxPosition()))    
    motors['RElbowRoll'].setPosition(np.clip(Roll3, motors['RElbowRoll'].getMinPosition(), motors['RElbowRoll'].getMaxPosition()))
    if Finger(thumbLeft,handTipLeft):
        for finger in letfFinger:
            motors[finger].setPosition(motors[finger].getMinPosition())
    else :
        for finger in letfFinger:
            motors[finger].setPosition(motors[finger].getMaxPosition())
    if Finger(thumbRight,handTipRight):
        for finger in rightFinger:
            motors[finger].setPosition(motors[finger].getMinPosition())
    else :
        for finger in rightFinger:
            motors[finger].setPosition(motors[finger].getMaxPosition())
supervisor =Supervisor()
motors={}
for i in range(supervisor.getNumberOfDevices()):
    device=supervisor.getDeviceByIndex(i)
    if type(device) is controller.motor.Motor:
        motors[device.name]=device
        #print(device.name)
        


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))  # Replace with your RabbitMQ server address if not running locally
channel = connection.channel()

channel.queue_declare(queue='joint_queue')

channel.basic_consume(queue='joint_queue',
                      on_message_callback=callback,
                      auto_ack=True)
channel.start_consuming()
