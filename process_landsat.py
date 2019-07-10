#!/usr/bin/env python3

import datetime
import json
import logging
import os
import re
import shutil
import subprocess
from os.path import basename, dirname
from os.path import join as pjoin
from xml.etree import ElementTree
import copy

import boto3
import botocore
import rasterio

from cogeo import cog_translate

# COG profile
default_profile = {
    'driver': 'GTiff',
    'interleave': 'pixel',
    'tiled': True,
    'blockxsize': 512,
    'blockysize': 512,
    'compress': 'DEFLATE',
    'predictor': 2,
    'zlevel': 9
}

# Set us up some logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)

# Sort out variables
BUCKET = os.environ.get('IN_BUCKET', 'deafrica-staging-west')
BUCKET = os.environ.get('IN_BUCKET', 'in-test-results-deafrica-staging-west')
PATH = os.environ.get('IN_PATH', 'L5-Ghana_original')
OUT_BUCKET = os.environ.get('OUT_BUCKET', 'test-results-deafrica-staging-west')
OUT_PATH = os.environ.get('OUT_PATH', 'test')
QUEUE = os.environ.get('QUEUE', 'dsg-test-queue')
DLQUEUE = os.environ.get('DLQUEUE', 'l2c-dead-letter')
VISIBILITYTIMEOUT = os.environ.get('VISIBILITYTIMEOUT', 1000)

# FOR TESTING
# VISIBILITYTIMEOUT = os.environ.get('VISIBILITYTIMEOUT', 40)

# These probably don't need changing
WORKDIR = os.environ.get('WORKDIR', 'data/download')
OUTDIR = os.environ.get('OUTDIR', 'data/out')
# These might need changing
DO_OVERWRITE = os.environ.get('OVERWRITE', "True")
DO_CLEANUP = os.environ.get('CLEANUP', "True")
DO_UPLOAD = os.environ.get('UPLOAD', "True")

DO_OVERWRITE = DO_OVERWRITE == "True"
DO_CLEANUP = DO_CLEANUP == "True"
DO_UPLOAD = DO_UPLOAD == "True"

# Flag for testing...
DO_TEST = False

# Log the environment...
logging.info("Reading from {}/{} and writing to {}/{}".format(
    BUCKET,
    PATH,
    OUT_BUCKET,
    OUT_PATH
))
logging.info("Getting items from the queue: {}".format(QUEUE))
logging.info("Dead letter queue is: {}".format(DLQUEUE))

LIMIT = 9999
if DO_TEST:
    LIMIT = 1

# Set up some AWS stuff
s3 = boto3.client('s3')

s3r = boto3.resource('s3')
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName=QUEUE)
dlqueue = sqs.get_queue_by_name(QueueName=DLQUEUE)


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
    """
    Returns the pertinent fields in the XML file from USGS as a dict.
    """
    with open(local_file) as f:
        xmlstring = f.read()
    xmlstring = re.sub(r'\sxmlns="[^"]+"', '', xmlstring, count=1)
    doc = ElementTree.fromstring(xmlstring)


    satellite = doc.find('.//satellite').text
    acquisition_date = doc.find('.//acquisition_date').text
    pathrow = doc.find('global_metadata').find('wrs').attrib

    meta = {
        'datetime': datetime.datetime.strptime(acquisition_date, "%Y-%m-%d"),
        'satellite': satellite,
        'path': pathrow['path'],
        'row': pathrow['row']

    }

    return (meta)


def delete_files(file_path):
    """
    Delete all the files and directories below a directory.
    """
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
    """
    Only returns the first XML file found in a directory. Somewhat
    dodgy if there's more than one, so clean out your workspace, folks!
    """
    files = os.listdir(directory)
    for f in files:
        if ".xml" in f:
            return f


def run_command(command, work_dir): 
    """ 
    A simple utility to execute a subprocess command. 
    """ 
    try:
        subprocess.check_call(command, stderr=subprocess.STDOUT, cwd=work_dir)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))


def check_dir(fname):
    file_name = fname.split('/')
    rel_path = pjoin(*file_name[-2:])
    return rel_path


def getfilename(fname, outdir):
    """ To create a temporary filename to add overviews and convert to COG
        and create a file name just as source but without '.TIF' extension
    """
    rel_path = check_dir(fname)
    out_fname = pjoin(outdir, rel_path)

    if not os.path.exists(dirname(out_fname)): 
        os.makedirs(dirname(out_fname)) 
    return out_fname


# from https://stackoverflow.com/questions/33842944/check-if-a-key-exists-in-a-bucket-in-s3-using-boto3
def check_processed(key):
    try:
        s3r.Object(OUT_BUCKET, key).load()
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            # The object does not exist.
            return False
        else:
            # Something else has gone wrong.
            raise
    else:
        # The object does exist.
        return True


def process_one(overwrite=False, cleanup=False, test=False, upload=True):
    process_failed = False

    logging.info("Starting up a run")
    # Get next file
    file_to_process = None
    messages = queue.receive_messages(
        VisibilityTimeout=VISIBILITYTIMEOUT,
        MaxNumberOfMessages=1
    )
    message = None
    if len(messages) > 0 and not test:
        # Example: from-tony/alex1129/espa-tonybutzer@gmail.com-11292018-115452-258/LE072110481999070901T1-SC20181129142650.tar.gz
        message = messages[0]
        file_to_process = message.body
        logging.info("Found file to process: {}".format(file_to_process))
    else:
        logging.warning("No messages!")
        if test:
            file_to_process = "raw/fiji/espa-tonybutzer@gmail.com-05032019-012123-847/LE070750722000051501T1-SC20190503034411.tar.gz"
        else:
            logging.warning("Bailing because there's no messages and we're not testing.")
            return

    # Download the file
    local_file = file_to_process.split('/')[-1]
    local_file_full = os.path.join(WORKDIR, local_file)
    logging.debug("Local file is: {}".format(local_file))

    if not os.path.isfile(local_file_full):
        logging.info("Downloading file to {}".format(local_file_full))

        try:
            s3r.Bucket(BUCKET).download_file(file_to_process, local_file_full)
        except NotADirectoryError as e:
            logging.warning("Failed to download the Bucket: {}".format(BUCKET))
            logging.warning("Error: {}".format(e))
            process_failed = True
            dlqueue.send_message(MessageBody=message.body)
            logging.warning("message moved to dead letter queue: {}".format(message.body))
        except FileNotFoundError as e:
            logging.warning("File Not Found: {}".format(file_to_process))
            logging.warning("{}".format(e))
            process_failed = True
            dlqueue.send_message(MessageBody=message.body)
            logging.warning("message moved to dead letter queue: {}".format(message.body))

            # Create a big list of items we're processing.
            # dlqueue.send_message(MessageBody=item)
    else:
        logging.info("File found locally, not downloading")

    if not process_failed:
        # Unzip the file
        logging.info("Unzipping the file {} into {}".format(local_file, WORKDIR))
        try:
            run_command(['tar', '-xzvf', local_file], WORKDIR)
        except RuntimeError as e:
            logging.warning("Failed to untar the file with error: {}".format(e))
            process_failed = True
            dlqueue.send_message(MessageBody=message.body)
            logging.warning("message moved to dead letter queue: {}".format(message.body))

    # Handle metadata
    if not process_failed:
        xml_file = os.path.join(WORKDIR, get_xmlfile(WORKDIR))
        metadata = get_metadata(xml_file)
        out_file_path = '{directory}/{satellite}/{path}/{row}/{date}'.format(
            directory=OUT_PATH,
            satellite=metadata['satellite'],
            path=metadata['path'],
            row=metadata['row'],
            date=metadata['datetime'].strftime("%Y/%m/%d")
        ) 
        xml_key = "{}/{}".format(out_file_path, basename(xml_file))
    
        # Check if we've already processed the file
        processed_already = check_processed(xml_key)
        if processed_already:
            logging.warning("This file has been processed already.")

        # Process data
        if overwrite or not processed_already:
            out_files = []
            gtiff_path = os.path.abspath(WORKDIR)
            output_dir = os.path.abspath(OUTDIR)
            count = 0
            for path, subdirs, files in os.walk(gtiff_path):
                for fname in files:
                    if fname.endswith('.tif') and ('_sr_' in fname or '_qa' in fname):
                        in_filename = os.path.join(path, fname)
                        logging.info("Reading %s", basename(in_filename))
                        out_filename = getfilename(in_filename, output_dir)
                        out_files.append(out_filename)

                        cog_profile = copy.deepcopy(default_profile)

                        # Transfer NODATA over if it's not pixel QA (which has no nodata)
                        if not '_qa' in fname:
                            src = rasterio.open(in_filename)
                            logging.info("NODATA is: {}".format(src.nodata))
                            if src.nodata and src.nodata is not 'None':
                                cog_profile['nodata'] = int(src.nodata)

                        cog_translate(
                            in_filename,
                            out_filename,
                            cog_profile,
                            overview_level=5,
                            overview_resampling='average'
                        )

                        # _write_cogtiff(f_name, filename, output_dir)
                        count = count+1
                        logging.info("Writing COG number {} to {}".format(count, dirname(out_filename)))

            # If all went well, upload everything
            if len(out_files) >= 7:
                if upload:
                    # Upload data
                    for out_file in out_files:
                        data = open(out_file, 'rb')
                        key = "{}/{}".format(out_file_path, basename(out_file))
                        logging.info("Uploading geotiff to {}".format(key))
                        s3r.Bucket(OUT_BUCKET).put_object(Key=key, Body=data)
                    
                    # Upload metadata
                    data = open(xml_file, 'rb')
                    logging.info("Uploading metadata file to {}".format(xml_key))
                    s3r.Bucket(OUT_BUCKET).put_object(Key=xml_key, Body=data)
                else:
                    logging.warning("DO_UPLOAD is false, not uploading.")
            else:
                logging.error("Only processed {} files. We need 8 or more for a valid dataset.".format(
                    len(out_files)
                ))
                process_failed = True
        else:
            logging.warning("Not processing the file because the `DO_OVERWRITE` flag is not set.")

    # Cleanup
    if cleanup:
        logging.info("Cleaning up workdir and outdir")
        delete_files(WORKDIR)
        delete_files(OUTDIR)

    # And we're finished
    if not process_failed:
        logging.info("Finished processing and now deleting the message.")
    else:
        logging.warning("The process to download {} FAILED!".format(
            local_file
        ))
    message.delete()
    logging.info("message deleted from queue: {}".format(message.body))


def get_items(LIMIT=10, filter=None):
    count = 0
    logging.info("Adding {} items from: {}/{} to the queue {}".format(LIMIT, BUCKET, PATH, QUEUE))
    items = get_matching_s3_keys(BUCKET, PATH)
    for item in items:
        # logging.info("Adding item {} which is the {}st item".format(item, count))
        if not filter or filter in item:
            count += 1
            if count >= LIMIT:
                break

            if count % 100 == 0:
                logging.info("Pushed {} items...".format(count))

            # Create a big list of items we're processing.
            queue.send_message(MessageBody=item)


def count_messages():
    logging.info("There are {} messages on the queue.".format(queue.attributes["ApproximateNumberOfMessages"]))
    return int(queue.attributes["ApproximateNumberOfMessages"])


if __name__ == "__main__": 
    n_messages = count_messages()
    logging.info("Upload is: {}, Overwrite is: {}, Cleanup is: {}".format(
        DO_UPLOAD, DO_OVERWRITE, DO_CLEANUP
    ))
    while n_messages > 0:
        process_one(test=DO_TEST, overwrite=DO_OVERWRITE, cleanup=DO_CLEANUP, upload=DO_UPLOAD)
        n_messages = count_messages()
