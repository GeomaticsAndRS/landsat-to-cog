#!/usr/bin/env python3

import datetime
import logging
import os
import re
from xml.etree import ElementTree
from os.path import join as pjoin, basename, dirname
import shutil

import boto3

from geotiffcog import run_command, _write_cogtiff, getfilename

# Set us up some logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

# Sort out variables
BUCKET = os.environ.get('IN_BUCKET', 'frontiersi-odc-test')
PATH = os.environ.get('IN_PATH', 'from-tony/alex1129')
OUT_BUCKET = os.environ.get('OUT_BUCKET', BUCKET)
OUT_PATH = 'test'
QUEUE = os.environ.get('QUEUE', 'landsat-to-cog-queue-test')

# These probably don't need changing
WORKDIR = os.environ.get('WORKDIR', 'data/download')
OUTDIR = os.environ.get('OUTDIR', 'data/out')
DO_TEST = False
DO_OVERWRITE = os.environ.get('OVERWRITE', True)
DO_CLEANUP = os.environ.get('CLEANUP', False)

if DO_TEST:
    LIMIT = 10
else:
    LIMIT = 9999999

# Set up some AWS stuff
s3 = boto3.client('s3')

s3r = boto3.resource('s3')
sqs = boto3.resource('sqs', "ap-southeast-2")
queue = sqs.get_queue_by_name(QueueName=QUEUE)


def get_matching_s3_keys(bucket, prefix='', suffix=''):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    kwargs = {'Bucket': bucket, 'Prefix': prefix}
    while True:
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp['Contents']:
            key = obj['Key']
            if key.endswith(suffix):
                yield key
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break

def get_metadata(local_file):
    with open(local_file) as f:
        xmlstring = f.read()
    xmlstring = re.sub(r'\sxmlns="[^"]+"', '', xmlstring, count=1)
    doc = ElementTree.fromstring(xmlstring)


    satellite = doc.find('.//satellite').text
    acquisition_date = doc.find('.//acquisition_date').text

    meta = {
        'datetime': datetime.datetime.strptime(acquisition_date, "%Y-%m-%d"),
        'satellite': satellite
    }

    return (meta)


def delete_files(file_path):
    logging.info("Deleting files from {}".format(file_path))
    for the_file in os.listdir(file_path):
        a_file = os.path.join(file_path, the_file)
        if os.path.isfile(a_file):
            logging.debug("Deleting file: {}".format(a_file))
            os.unlink(a_file)
        elif os.path.isdir(a_file):
            logging.debug("Deleting directory: {}".format(a_file))
            shutil.rmtree(a_file)


def get_xmlfile(directory):
    files = os.listdir(directory)
    for f in files:
        if ".xml" in f:
            return f

def process_one(overwrite=False, cleanup=False, test=False):
    process_failed = False

    logging.debug("Starting to process")
    # Get next file
    file_to_process = None
    messages = queue.receive_messages()
    message = None
    if len(messages) > 0 and not test:
        # Example: from-tony/alex1129/espa-tonybutzer@gmail.com-11292018-115452-258/LE072110481999070901T1-SC20181129142650.tar.gz
        message = messages[0]
        file_to_process = message.body
        logging.info("Found file to process: {}".format(file_to_process))
    else:
        logging.warning("No messages!")
        if test:
            file_to_process = "from-tony/alex1129/espa-tonybutzer@gmail.com-11292018-115452-258/LE072110482001051101T1-SC20181129141358.tar.gz"
        else:
            logging.warning("Bailing because there's no messages and we're not testing.")
            return

    # Download the file
    local_file = file_to_process.split('/')[-1]
    local_file_full = os.path.join(WORKDIR, local_file)
    logging.debug("Local file is: {}".format(local_file))

    if not os.path.isfile(local_file_full):
        logging.info("Downloading file to {}".format(local_file_full))
        s3r.Bucket(BUCKET).download_file(file_to_process, local_file_full)
    else:
        logging.info("File found locally, not downloading")

    # Unzip the file
    logging.info("Unzipping the file {} into {}".format(local_file, WORKDIR))
    run_command(['tar', '-xzvf', local_file], WORKDIR)

    # Handle metadata
    xml_file = os.path.join(WORKDIR, get_xmlfile(WORKDIR))
    metadata = get_metadata(xml_file)
    out_file_path = OUT_PATH + '/' + metadata['datetime'].strftime("%Y/%m/%d")

    # TODO: check whether we've processed this file yet
    processed_already = False

    # # Process data
    if overwrite and not processed_already:
        out_files = []
        gtiff_path = os.path.abspath(WORKDIR)
        output_dir = os.path.abspath(OUTDIR)
        count = 0
        for path, subdirs, files in os.walk(gtiff_path):
            for fname in files:
                if fname.endswith('.tif') and '_sr_' in fname:
                    f_name = os.path.join(path, fname)
                    logging.info("Reading %s", basename(f_name))
                    filename = getfilename(f_name, output_dir)
                    out_files.append(filename)
                    _write_cogtiff(f_name, filename, output_dir)
                    count = count+1
                    logging.info("Writing COG to %s, %i", dirname(filename), count)

        # Upload data
        for out_file in out_files:
            data = open(out_file, 'rb')
            key = "{}/{}".format(out_file_path, basename(out_file))
            logging.info("Uploading geotiff to {}".format(key))
            s3r.Bucket(OUT_BUCKET).put_object(Key=key, Body=data)
    
        # If all went well, upload metadata
        if len(out_files) > 0:
            data = open(xml_file, 'rb')
            key = "{}/{}".format(out_file_path, basename(xml_file))
            logging.info("Uploading metadata file to {}".format(key))
            s3r.Bucket(OUT_BUCKET).put_object(Key=key, Body=data)
        else:
            logging.error("Failed to find any surface reflectance files... weird!")
            process_failed = True

    # Cleanup
    if cleanup:
        logging.info("Cleaning up workdir and outdir")
        delete_files(WORKDIR)
        delete_files(OUTDIR)

    # And we're finished
    if not process_failed:
        message.delete()
    else:
        logging.warning("The process to download {} failed. Careful, this may stay on the list of jobs.".format(
            local_file
        ))


def get_items():
    count = 0
    print(BUCKET, PATH)
    items = get_matching_s3_keys(BUCKET, PATH)
    for item in items:
        count += 1
        if count >= LIMIT:
            break

        # Create a big list of items we're processing.
        queue.send_message(MessageBody=item)


def count_messages():
    print("There are {} messages on the queue.".format(queue.attributes["ApproximateNumberOfMessages"]))


if __name__ == "__main__": 
    count_messages()
    # get_items()
    process_one(test=DO_TEST, overwrite=DO_OVERWRITE, cleanup=DO_CLEANUP)
