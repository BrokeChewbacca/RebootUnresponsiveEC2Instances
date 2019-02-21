from __future__ import print_function
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

print('Loading function')

def lambda_handler(event, context):
    message = event['Records'][0]['Sns']['Message']
    print("From SNS: " + message)
    
    # The four lines below get the instance id that triggered the alert by splitting
    # the message string until all that is left is the Instance ID
    message = message.split('"value":"', 1)
    message = message[1].split('",', 1)
    instanceID = message[0]

    # Gets the current date/time, since this is run in AWS this time is in UTC
    currentDT = datetime.now()
    # Strips the date portion off, leaving it in HH:MM:SS format
    currentDT = currentDT.strftime('%H:%M:%S')
    
    # Reminder, the time below is adjusted for UTC
    # Below it is set to reboot if the current time is between 03:00:00 UTC
    # and 11:00:00 UTC
    if currentDT > '03:00:00' and currentDT < '11:00:00':
        ec2 = boto3.client('ec2')
        
        try:
            ec2.reboot_instances(InstanceIds=[instanceID], DryRun=True)
        except ClientError as e:
            if 'DryRunOperation' not in str(e):
                print("You don't have permission to reboot instances.")
                raise
        
        try:
            response = ec2.reboot_instances(InstanceIds=[instanceID], DryRun=False)
            print('Success', response)
        except ClientError as e:
            print('Error', e)
            
    return message
