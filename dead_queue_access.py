#!/usr/bin/env python3

import os
import boto3

QUEUE = os.environ.get('QUEUE', 'dsg-test-queue')
DLQUEUE = os.environ.get('DLQUEUE', 'l2c-dead-letter')

# Set up some AWS stuff
# s3 = boto3.client('s3')
# s3r = boto3.resource('s3')
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=QUEUE)
dlqueue = sqs.get_queue_by_name(QueueName=DLQUEUE)

messages = queue.receive_messages(
        VisibilityTimeout=10,
        MaxNumberOfMessages=1
    )
message = messages[0]
print ('standard queue')
print (message)

dlqueue.send_message(MessageBody=message.body)

messages = dlqueue.receive_messages(
        VisibilityTimeout=10,
        MaxNumberOfMessages=1
    )
print ('dead queue')
message = messages[0]
print (message)
print('ran ok')
