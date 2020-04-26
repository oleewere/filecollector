#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

import argparse
import sys
import os
import yaml
import glob
import gzip
import shutil
import datetime
import tarfile
import fileinput
import re
import zipfile
import subprocess
from pid import PidFile

def parse_args():
    parser = argparse.ArgumentParser(
        description='Python script to collect logs to specific folder')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to logcollector configuration')
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    with open(args.config) as file:
        config = yaml.load(file, yaml.SafeLoader)
        if "collector" in config:
            outputLocation=config["collector"]["outputLocation"]
            outputScript=config["collector"]["outputScript"]
            processFileScript=config["collector"]["processFileScript"]
            files=config["collector"]["files"]
            now = datetime.datetime.today() 
            nTime = now.strftime("%Y-%m-%d-%h-%M-%S-%f")
            tmp_folder=os.path.abspath(os.path.join(outputLocation, "tmp", nTime))
            for fileObject in files:
                for file in glob.glob(fileObject["path"]):
                    if not os.path.exists(tmp_folder):
                        os.makedirs(tmp_folder)
                    dest_folder=os.path.join(tmp_folder, fileObject["label"])
                    if not os.path.exists(dest_folder):
                        os.makedirs(dest_folder)
                    dest=os.path.join(dest_folder, os.path.basename(file))
                    if os.path.isfile(file):
                        shutil.copy(file, dest)
                    if "rules" in config["collector"] and config["collector"]["rules"]:
                        for line in fileinput.input(dest, inplace=1):
                            for rule in config["collector"]["rules"]:
                                line = re.sub(rule["pattern"], rule["replacement"], line.rstrip())
                                print(line)
                    if processFileScript:
                        subprocess.call([processFileScript, dest, fileObject["label"]])
            processFilesFolderScript=config["collector"]["processFilesFolderScript"] if "processFilesFolderScript" in config["collector"] else None
            if processFilesFolderScript:
                subprocess.call([processFilesFolderScript, tmp_folder])
            
            skip_compress="compress" in config["collector"] and not bool(config["collector"]["compress"])
            keep_processed_files="deleteProcessedTemplateFiles" in config["collector"] and not bool(config["collector"]["deleteProcessedTemplateFiles"])
            if skip_compress:
                print("skipping file compression")
            else:
                output_file=os.path.join(outputLocation, nTime + ".zip")
                make_archive(tmp_folder, output_file)
            
            if keep_processed_files:
                print("keep processed files in '%s' folder" % os.path.join(outputLocation, "tmp"))
            else:
                shutil.rmtree(os.path.join(outputLocation, "tmp"))
            
            if not skip_compress and outputScript:
                subprocess.call([outputScript, output_file])

def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s'%(name,format), destination)

if __name__ == "__main__":
    pidfile=os.environ.get('FILECOLLECTOR_PIDFILE', 'filecollector-collector.pid')
    with PidFile(pidfile) as p:
        main()