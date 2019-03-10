from __future__ import print_function
import boto3
from botocore.exceptions import ClientError
import pytz
from datetime import datetime, timedelta
import os

print('Loading function')

def is_dst(zonename):
	tz = pytz.timezone(zonename)
	now = pytz.utc.localize(datetime.utcnow())
	return now.astimezone(tz).dst() != timedelta(0)

def lambda_handler(event, context):
	message = event['Records'][0]['Sns']['Message']
	print('From SNS: ' + message)

	holderStr = message
	holderStr = holderStr.split('"value":"', 1)
	holderStr = holderStr[1].split('",', 1)
	instanceID = holderStr[0]

	currentDT = datetime.utcnow()
	currentDT = currentDT.strftime('%H:%M:%S')

	tz = os.environ['TimeZone']
	if is_dst(tz):
		maintWindowStartTime = os.environ['MaintWindowStart_DST']
		maintWindowEndTime = os.environ['MaintWindowEnd_DST']
	else:
		maintWindowStartTime = os.environ['MaintWindowStart_ST']
		maintWindowEndTime = os.environ['MaintWindowEnd_ST']

	if currentDT > maintWindowStartTime and currentDT < maintWindowEndTime:
		ec2 = boto3.client('ec2')

		try:
			ec2.reboot_instances(InstanceIds=[instanceID], DryRun=True)
		except ClientError as e:
			if 'DryRunOperation' not in str(e):
				print("You do not have permission to reboot instances.")
				raise

		try:
			response = ec2.reboot_instances(InstanceIds=[instanceID], DryRun=False)
			print('Reboot initiated for: ' + instanceID, response)
		except ClientError as e:
			print('Error', e)

	return message
