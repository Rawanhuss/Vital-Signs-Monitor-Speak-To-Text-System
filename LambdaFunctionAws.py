import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
import uuid
 
 
#That's the lambda handler, you can not modify this method
# the parameters from JSON body can be accessed like deviceId = event['deviceId']

def lambda_handler(event, context):
    # Instanciating connection objects with DynamoDB using boto3 dependency
    dynamodb = boto3.resource('dynamodb')
    client = boto3.client('dynamodb')
    
    # Getting the table 
    #vital signs table in Dynamodb
    vitalSignsTable = dynamodb.Table('vital_signs')
    varAll = dynamodb.Table('values')
    
    # Getting the current datetime and transforming it to string in the format bellow
    id = str(uuid.uuid4())
    created_at = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    deviceId = event['deviceId']
    username = event['username']
    bpm = event['bpm']
    spo2 = event['spo2']
    temperature = event['temperature']
   
    # Putting a try/catch to log to user when some error occurs
    try:
        if ((int(bpm) <= 0 ) or (int(spo2) <= 0 )):
            return {
                'statusCode': 400,
                'body': json.dumps('Some Empty Readings')
                }
                
        #In normal BPM range,normal SPo2 and normal body temperature but potentially sleep 
        elif (60 <= int(bpm) <= 90 ):
            abnormal = False
            vitalSignsTable.put_item(
                Item={
                    'id': id,
                    'deviceId': deviceId,
                    'username': username,
                    'created_at': created_at,
                    'bpm': int(bpm),
                    'spo2': int(spo2),
                    'temperature': int(temperature),
                    'abnormal': abnormal
                    }
                )
            
            return {
                'statusCode': 200,
                'body': json.dumps('Normal ,stay save :)')
                }
                

        elif (91 <= int(bpm) <= 100 ) :
            if ((91<= int(spo2) <= 100) & (35.00 <= float(temperature) <= 37.00)):
                abnormal = False
                vitalSignsTable.put_item(
                    Item={
                        'id': id,
                        'deviceId': deviceId,
                        'username': username,
                        'created_at': created_at,
                        'bpm': int(bpm),
                        'spo2': int(spo2),
                        'temperature': int(temperature),
                        'abnormal': abnormal
                         }
                         )
                return {
                'statusCode': 200,
                'body': json.dumps('Normal,Stay Safe :)')
                }
            elif ((86 <= int(spo2) <= 90) & (35.00 <= float(temperature) <= 37.00)):
                abnormal = True
                vitalSignsTable.put_item(
                    Item={
                        'id': id,
                        'deviceId': deviceId,
                        'username': username,
                        'created_at': created_at,
                        'bpm': int(bpm),
                        'spo2': int(spo2),
                        'temperature': int(temperature),
                        'abnormal': abnormal
                        }
                    )
                return {
                    'statusCode': 200,
                    'body': json.dumps('Please find another room not crowded or even go outside to take some oxygen')
                    }
            elif ((int(spo2) <= 85) & (35.00 <= float(temperature) <= 37.00)):
                abnormal = True
                vitalSignsTable.put_item(
                    Item={
                        'id': id,
                        'deviceId': deviceId,
                        'username': username,
                        'created_at': created_at,
                        'bpm': int(bpm),
                        'spo2': int(spo2),
                        'temperature': int(temperature),
                        'abnormal': abnormal
                        }
                    )
                
                return {
                    'statusCode': 200,
                    'body': json.dumps('call the ambulance,needed oxygen')
                    }
            elif ((91<= int(spo2) <= 100) & (float(temperature) > 37.01)):
                abnormal = True
                vitalSignsTable.put_item(
                    Item={
                        'id': id,
                        'deviceId': deviceId,
                        'username': username,
                        'created_at': created_at,
                        'bpm': int(bpm),
                        'spo2': int(spo2),
                        'temperature': int(temperature),
                        'abnormal': abnormal
                    }
                    )
                
                return {
                    'statusCode': 200,
                    'body': json.dumps('High body temperature,there is probably an infection')
                    }
            else:
                
                return {
                    'statusCode': 200,
                    'body': json.dumps('Normal Stay save')
                    }
            
           
        elif (101 <= int(bpm) <= 120 ) :
            abnormal = True
            vitalSignsTable.put_item(
                Item={
                    'id': id,
                    'deviceId': deviceId,
                    'username': username,
                    'created_at': created_at,
                    'bpm': int(bpm),
                    'spo2': int(spo2),
                    'temperature': int(temperature),
                    'abnormal': abnormal
                    }
                )
                
                    
            if((86 <= int(spo2) <= 90) & (35.00 <= float(temperature) <= 37.00)):
                return {
                    'statusCode': 200,
                    'body': json.dumps('abnormal BPM and Oxygen percantage ,Please find another room not crowded or even go outside to take some oxygen and make sure to take a rest after per activity')
                    }

            elif((int(spo2) <= 85) & (35.00 <= float(temperature) <= 37.00)):
                return {
                    'statusCode': 200,
                    'body': json.dumps('abnormal BPM and Oxygen percantage,call the ambulance,needed oxygen')
                    }
            elif((91<= int(spo2) <= 100) & (float(temperature) > 37.01)):
                return {
                'statusCode': 200,
                'body': json.dumps('abnormal BPM ,please make sure to take a rest after per activity and High body temperature was detected,there is probably an infection')
                }
            else:
                return{
                    'statusCode': 200,
                    'body': json.dumps('abnormal heart rate')
                    
                }
                
    except:
        print('Closing lambda function')
        return {
                'statusCode': 400,
                'body': json.dumps('Error saving the signs')
        }