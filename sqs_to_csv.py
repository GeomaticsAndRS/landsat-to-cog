#!/usr/bin/env python3

import os
import boto3
import logging
import csv

# Set us up some logging                                                       
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

DLQUEUE = os.environ.get('DLQUEUE', 'alex-dead-queue')

# Set up some AWS stuff
s3 = boto3.client('s3')
s3r = boto3.resource('s3')
sqs = boto3.resource('sqs', region_name='us-west-2')
dlqueue = sqs.get_queue_by_name(QueueName=DLQUEUE)


def dump_messages():
    messages = dlqueue.receive_messages(
        VisibilityTimeout=120,
        MaxNumberOfMessages=10,
        MessageAttributeNames=['All']
    )
    if not messages:
        return
    
    with open('broken_scenes.csv', 'a', newline='\n') as csvfile:
        spamwriter = csv.writer(csvfile)
        for message in messages:
            spamwriter.writerow([message.body])
            # logging.info("Message is {}.".format(message.body))


def count_messages(a_queue):
    message_count = a_queue.attributes["ApproximateNumberOfMessages"]
    logging.info("There are {} messages on the queue.".format(message_count))
    return int(message_count)


if __name__ == "__main__":
    n_messages = count_messages(dlqueue)
    while n_messages > 0:
        dump_messages()
        n_messages = count_messages(dlqueue)
