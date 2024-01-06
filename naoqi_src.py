from naoqi import ALProxy
import pika # pika==1.1.0
import json

def move():
    print( 20*"-" + "\n Data Dict:\n" + 20*"-")
    velocity = 1
    joints = {
        "HeadPitch" : 0.0,
        "HeadYaw" : 0.0,
        "LShoulderPitch" : -0.9,
        "LShoulderRoll" : 0.0,
        "RShoulderPitch" : -0.9,
        "RShoulderRoll" : 0.0,
        "LElbowYaw" : 0.0,
        "LElbowRoll" : 0.0,
        "RElbowYaw" : 0.0,
        "RElbowRoll" : 0.0,
        "LWristYaw" : 0.0,
        "LHand" : 0.0,
        "RHand" : 0.0,
        "RWristYaw" : 0.0,
        "LHipYawPitch" : 0.0,
        "RHipYawPitch" : 0.0,
        "LHipPitch" : 0.0,
        "RHipPitch" : 0.0,
        "LHipRoll" : 0.0,
        "RHipRoll" : 0.0,
        "LKneePitch" : 0.0,
        "RKneePitch" : 0.0,
        "LAnklePitch" : 0.0,
        "RAnklePitch" : 0.0,
        "LAnkleRoll" : 0.0,
        "RAnkleRoll" : 0.0,
        }
    motion_proxy = ALProxy("ALMotion", NAO_IP, NAO_PORT)

    for key, value in joints.items():
        motion_proxy.setAngles(key, value, velocity)
        
   
    
def callback(ch, method, properties, body):
    print(body)
    joint_data_dict = json.loads(body.decode('utf-8'))
    data_dict = {}
    # Process the received joint data dictionary
    for joint in joint_data_dict:
        jointType,Position=joint.items()
        data_dict[jointType[1]]=Position[1]
    move(data_dict)
          
def messageQueue():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))  # Replace with your RabbitMQ server address if not running locally
    channel = connection.channel()

    channel.queue_declare(queue='joint_queue')

    channel.basic_consume(queue='joint_queue',
                          on_message_callback=callback,
                          auto_ack=True)
    channel.start_consuming()


        
if __name__ == "__main__":

    NAO_IP = "127.0.0.1"
    NAO_PORT = 9559
    messageQueue()
    print( 20*"-" + "\n Done!\n" + 20*"-")
