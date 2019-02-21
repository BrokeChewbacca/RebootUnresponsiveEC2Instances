# RebootUnresponsiveEC2Instances
Python script you can run in AWS Lambda to automatically reboot EC2 Instances within a specified time period that fail Cloudwatch checks.

# Usage
You will need to have the script in reboot.py in a Lambda function that is using the Python 3.7 runtime. The function needs to be triggered by SNS and needs access to Amazon CloudWatch Logs, Amazon EC2, and Amazon SQS (SQS is only needed if you want to schedule the reboot for a later time, you will also need to add additional code for scheduling it).

Any print statements will print to CloudWatch logs which is very useful for troubleshooting code if you make changes.

The *lambda_handler* function is provided by AWS when you create a new Lambda function and it gives you access to details about the event that called the Lambda function. The event details are used to find the EC2 Instance ID so we can reboot the Instance that is failing the CloudWatch checks. More specifically, within the event details, there is a section labeled "Message" that contains the Instance ID so we set *message* equal to that portion of the event details.

To obtain the instance ID we start stripping off portions of the *message* string until we are left with the instance ID string, which gets stored in *instanceID* (lines 14-16).

Since there is the possibility of false positives with CloudWatch alarms, we don't want the instances to reboot on their own during business hours (in our case 6am EST - 10pm EST) so we add a check for that before rebooting (line 26). We get the current time (UTC since that's what AWS uses and that is where this script will be ran) using *datetime.now()* and store it in *currentDT*. We are not concerned with the date portion so we remove that on line 21.

Lines 27 - 40 send the request to reboot the instance.

# Testing
When testing this in your own AWS environment, you can force failed CloudWatch checks by setting your alarm threshold to be greater than or equal to zero, rather than just greater than zero.

I would recommend testing against Linux instances because Windows instances are billed a minimum of an hour every time the instance is stopped and started. If you do test against a Linux instance, before changing the CloudWatch alarm threshold start a ping test to it's public IP because small Linux instances stop and start so fast that the EC2 console doesn't update the status in time.
