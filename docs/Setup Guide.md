## Hardware Setup:
- Connect the IR sensor to a GPIO pin 18 , 5V, and GND
- Connect the door sensor to another GPIO pin 17 and GND
## AWS IoT Setup:
- Go to AWS IoT Core → Manage → Things → Create a thing
- Register your device (Raspberry_Pi), and generate the following:
  - Device certificate
  - Private key
  - Public key
  - Amazon Root CA
## Configure AWS IoT Policy:
- Security → Policies
- Click on the policy then select Edit Active Version (if no policy create one)
- Configure Policy Document:
  - In Policy Document section, set wildcard (*) values for both Policy Action and Policy Resource
  - Click Allow for Policy Effect then click Save as new version or Create
- Attach policy to the certificate
  - navigate to Security → Certificates and click your certificate
  - In the Actions menu, select Attach Policy
  - Choose the policy you created from the list and click Attach Policies
## Raspberry Pi Setup:
- Place Certificates and key files to a folder on your raspberry pi named “cert”
- Transfer the following files from your computer to the cert folder and rename them to the following:
  - RootCA1.pem
  - RaspberryPi-cert.pem.crt
  - RaspberryPi-private.pem.key
- Downlaod the mailbox_pub.py script from the Source Code folder to your Raspberry Pi. Edit the file (can use nano) and modify the following:
  - host URL: AWS IoT Core → Domain configuration. Your device has a device data endpoint to connect to AWS. Copy the Domain name and replace where it says “YOUR HOST ADDRESS”
  - certPath: replace with the directory to your cert folder created earlier.
  - Change clientID to your AWS IoT device name
  - Change topic to PiMailbox – this is the MQTT topic to send sensor data
- Run code and navigate to Test in AWS IoT Core, click MQTT test client
  - In Subscribe to a topic field, enter the topic name (PiMailbox) then click Subscribe. The MQTT messages should appear.
## Setting up DynamDB:
- In AWS IoT Core, go to Manage → Message Routing → Rules
- Click Create Rule and in Rule properties, enter a new rule name (MailBoxLogging) then click Next to continue
- In the SQL Statement field, enter the following:
  - SELECT * FROM “PiMailbox”
- Set up the Rule actions to route the sensor data from AWS IoT Core to a DynamoDB table:
  - Open the list of rules in Action 1 and choose DynamoDBv2
  - Click Create DynamoDB table, this will open a new tab. Do not close previous tab
  - In the Table details section, enter a new Table name (MailLogging). Set Partition key to  sequence and Sort key to timestamp. Then click Create table
  - Return back to the original tab and click the refresh icon next to Table name. Select the DynamoDB table you just created.
  - In the IAM role section, choose Create new role. Enter a role name (IAMMailRole) and click Create
  - Finally, in the Review and create page, choose Create.
## Setting up Email Alerts with Amazon SNS
- Go to Amazon SNS
  - Click Topics → Create topic
  - Select Standard as the topic type
  - Enter a topic name (MailDetectAlert) then click Create topic
  - Repeat these steps for a topic named (DoorStateAlert)
- Subscribe to these SNS topics:
  - Go to Amazon SNS Console and click Topics
  - Click the topics you just created and click Create subscription
  - Set the Protocol to Email and Endpoint to the email address that you will be using to receive the alerts
  - After creating the subscription, go to your email to confirm the subscription
- Create new rules for the alerts:
  - Go to AWS IoT Core → Message Routing → Rules
  - Click Create rule and name the new rule MailDetectAlertRule
  - In the SQL Statement field, enter the following:
    - SELECT * FROM “PiMailbox” WHERE mail = ‘Mail Detected’ OR ‘Mailbox Empty’
  - Choose Add action → Simple Notification Service (SNS)
  - Select the SNS topic: MailDetectAlert
  - In Message format, click RAW
  - In the IAM role section, choose Create new role. Enter role name, MailAlertRole, and click Create. Select this IAM role
  - Click Create to finish new rule creation
  - Repeat the above steps for a new rule named DoorStateAlertRule
    - SQL: SELECT * FROM “PiMailbox” WHERE door ‘opened’ OR door ‘closed’
    - SNS topic: DoorStateAlert
    - IAM role: DoorAlertRole

Run mailbox_pub.py script again to test the email alert system. You should receive an email alert shortly after running the script. User will be notified after every state change of the system. 
## Demo Video
[Watch on Youtube] (https://youtube.com/shorts/i_-ORuXHe_s?si=MjLMxqKufRI1vxbC)
