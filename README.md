# RebootUnresponsiveEC2Instances
Python script you can run in AWS Lambda to automatically reboot EC2 Instances within a specified time period that fail Cloudwatch checks.

## Description
- This script will automatically reboot an Instance, as long as the current time is within the maintenance window, that fails a StatusCheckFailed_Instance EC2 metric check.
- When an instance fails this check, an SNS topic will be sent which will trigger this function.
- The function gets the current time (in UTC) and checks if the time is within the maintenance window.
- If it is, the instance that failed the health check will be rebooted, otherwise, nothing happens.
- If you configure the environment variables in the ‘AWS Environment Configuration’ correctly you won't need to adjust the time to account for daylight-savings time.


## AWS Environment Configuration
- IAM
  - Policies
    - Create a policy named ‘RebootUnresponsiveInstancesBasedOnTime’ using the ‘RebootUnresponsiveInstancesBasedOnTime IAM Policy.json’ file in the ‘IAM Policies’ folder.
    - Create a policy name ‘LambdaUpdateFunctionCode’ using the ‘LambdaUpdateFunctionCode IAM Policy.json’ file in the ‘IAM Policies’ folder.
  - Roles
    - Create a role named ‘RebootUnresponsiveInstancesBasedOnTime’ that will be used by Lambda. For permissions give it the ‘RebootUnresponsiveInstancesBasedOnTime’ policy.
  - Users
    - Create a user named ‘LambdaUpdateFunctionCodeCLI’ with programmatic access. Attach the existing ‘LambdaUpdateFunctionCode’ policy.
    - **MAKE SURE YOU SAVE THE CREDS FOR THIS USER**
- SNS
  - Create a topic named ‘RebootUnresponsiveInstancesBasedOnTime’
    - Optional: Add a subscription to the topic for SMS/Email alerts
- CloudWatch Alarms
  - Create a new alarm named ‘RebootUnresponsiveInstancesBasedOnTime’
    - Metric: EC2 -> Per-Instance Metrics -> StatusCheckFailed_Instance
    - Whenever:
      - is: > 0
      - for: 1 out of 1 datapoints
    - Treat missing data as: missing
    - Whenever this alarm: State is ALARM
    - Send notification to: RebootUnresponsiveInstancesBasedOnTime
- Lambda
  - Create a function named ‘RebootUnresponsiveInstancesBasedOnTime’
    - Runtime: Python 3.7
    - Permissions: Existing Role – RebootUnresponsiveInstancesBasedOnTime
    - Triggers: SNS – RebootUnresponsiveInstancesBasedOnTime
    - Handler: reboot.lambda_handler
    - Don’t worry about the function code right now, you’ll upload it later using the CLI.
    - Under ‘Environment variables’ setup the following:
      - MaintWindowStart_ST
        - This is the start of the maintenance window (when the instances can stop) in standard time. The time needs to be in UTC and in the format HH:MM:SS
      - MaintWindowEnd_ST
        - This is the end of the maintenance window (when the instances can stop) in standard time. The time needs to be in UTC and in the format HH:MM:SS
      - MaintWindowStart_DST
        - This is the start of the maintenance window (when the instances can stop) in daylight savings time. The time needs to be in UTC and in the format HH:MM:SS
      - MaintWindowEnd_DST
        - This is the end of the maintenance window (when the instances can stop) in daylight savings time. The time needs to be in UTC and in the format HH:MM:SS
      - TimeZone
        - This is the time zone that you want these maintenance window times to reference. This is needed to determine if it is standard time or daylight-saving time.
        - You can find the correct time zone formats for python [here](https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568).

## Upload the Code
- **Only perform these next steps after everything in the ‘AWS Environment Configuration’ has been completed.**
- The following assumes you have named everything exactly as told to above. If you have changed any of the script names or Lambda function names, the commands below will need to be tweaked accordingly. I’m also assuming you have each of the three folders containing the scripts on your systems desktop.
- Open terminal and type `cd desktop`
- Type `aws configure` and enter the ‘AWS Access Key ID’ and ‘AWS Secret Access Key’ for the LambdaUpdateFunctionCodeCLI user created earlier. Enter the region name you are operating in. Leave the ‘Default output format’ as ‘None’.
  - `cd RebootUnresponsiveInstancesBasedOnTime`
  - `cd package`
  - `zip -r9 ../RebootUnresponsiveInstancesBasedOnTime.zip .`
  - `cd ../`
  - `zip -g RebootUnresponsiveInstancesBasedOnTime.zip RebootUnresponsiveInstancesBasedOnTime.py
  - `aws lambda update-function-code --function-name RebootUnresponsiveInstancesBasedOnTime --zip-file fileb:// RebootUnresponsiveInstancesBasedOnTime.zip`


## Testing
- When testing this in your own AWS environment, you can force failed CloudWatch checks by setting your alarm threshold to be greater than or equal to zero, rather than just greater than zero.

- I would recommend testing against Linux instances because Windows instances are billed a minimum of an hour every time the instance is stopped and started. If you do test against a Linux instance, before changing the CloudWatch alarm threshold start a ping test to it's public IP because small Linux instances stop and start so fast that the EC2 console doesn't update the status in time.
