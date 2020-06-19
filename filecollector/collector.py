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
import logging
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
import socket
import time
from fluent import sender
from fluent import event
from pid import PidFile

def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Python script to collect logs to specific folder')
    parser.add_argument('--config', type=str, required=True,
                        help='Path to logcollector configuration')
    parser.add_argument('--labels', type=str, required=False,
                        help='Comma separated list of labels for filtering files for collection')
    args = parser.parse_args(args)
    return args

def main(args):
    args = parse_args(args)
    filteredLabels = args.labels.split(',') if args.labels else []
    with open(args.config) as file:
        config = yaml.load(file, yaml.SafeLoader)
        if config and "collector" in config:
            logger=__setup_logger(config)
            outputLocation=config["collector"]["outputLocation"]
            outputScript=__get_str_key("outputScript", config["collector"])
            preProcessScript=__get_str_key("preProcessScript", config["collector"])
            processFileScript=__get_str_key("processFileScript", config["collector"])
            files=config["collector"]["files"]
            useFullPath=__get_bool_key("useFullPath", config["collector"], True)
            compressFormat=__get_str_key("compressFormat", config["collector"], "zip")
            now = datetime.datetime.today()
            nTime = now.strftime("%Y-%m-%d-%H-%M-%S-%f")
            hostname=None
            if socket.gethostname().find('.')>=0:
                hostname=socket.gethostname()
            else:
                hostname=socket.gethostbyaddr(socket.gethostname())[0]
            zipfile_name = nTime + "-" + hostname.replace(".", "-")
            tmp_folder=os.path.abspath(os.path.join(outputLocation, "tmp", zipfile_name))
            if preProcessScript:
                subprocess.call([preProcessScript, tmp_folder])
            
            fluentEventProcessor = None
            if "fluentProcessor" in config["collector"]:
                fluent_host=__get_str_key("host", config["collector"]["fluentProcessor"], "localhost")
                fluent_port=__get_int_key("port", config["collector"]["fluentProcessor"], 24224)
                fluent_tag=__get_str_key("tag", config["collector"]["fluentProcessor"])
                identifier=__get_str_key("identifier", config["collector"]["fluentProcessor"])
                message_field=__get_str_key("messageField", config["collector"]["fluentProcessor"], "message")
                include_time=__get_bool_key("includeTime", config["collector"]["fluentProcessor"])
                fluentEventProcessor=EventProcessor(fluent_host, int(fluent_port), fluent_tag, identifier, message_field, include_time)
            if not os.path.exists(tmp_folder):
                os.makedirs(tmp_folder)
            __disk_check(files, filteredLabels, outputLocation, config["collector"], logger)
            for fileObject in files:
                if filteredLabels and fileObject["label"] not in filteredLabels:
                    continue
                sortFilesByDate=not "sortFilesByDate" in config["collector"] or bool(config["collector"]["sortFilesByDate"])
                allfiles=sorted(glob.glob(fileObject["path"]), key=os.path.getmtime) if sortFilesByDate else glob.glob(fileObject["path"])
                exclude_files=__get_excludes(fileObject["excludes"] if "excludes" in fileObject else [], logger)
                for file in allfiles:
                    if file in exclude_files:
                        continue
                    logger.debug("process file: %s" % os.path.abspath(file))
                    dest_folder=None
                    if "folderPrefix" in fileObject:
                        dest_folder=os.path.join(tmp_folder, fileObject["folderPrefix"], fileObject["label"].lower())
                    else:
                        dest_folder=os.path.join(tmp_folder, fileObject["label"].lower())
                    dest_folder=os.path.join(tmp_folder, fileObject["label"])
                    useFullPathPerFile=__get_bool_key("useFullPath", fileObject, True) if "useFullPath" in fileObject else useFullPath
                    dest=os.path.join(dest_folder, os.path.abspath(file).lstrip(os.sep)) if useFullPathPerFile else os.path.join(dest_folder, os.path.basename(file))
                    dest_parent=os.path.dirname(dest)
                    if not os.path.exists(dest_parent):
                        os.makedirs(dest_parent)
                    if os.path.isfile(file):
                        shutil.copy(file, dest)
                    if "rules" in config["collector"] and config["collector"]["rules"]:
                        for line in fileinput.input(dest, inplace=1):
                            for rule in config["collector"]["rules"]:
                                line = re.sub(rule["pattern"], rule["replacement"], line.rstrip())
                                print(line)
                    if processFileScript:
                        subprocess.call([processFileScript, dest, fileObject["label"]])
                    if fluentEventProcessor:
                        fluentEventProcessor.process(fileObject["label"], os.path.abspath(file), dest)
                    deleteProcessedTempFilesOneByOne=__get_bool_key("deleteProcessedTempFilesOneByOne", config["collector"])
                    if deleteProcessedTempFilesOneByOne:
                        os.remove(dest)
                    
            processFilesFolderScript=__get_str_key("processFilesFolderScript", config["collector"])
            if processFilesFolderScript:
                subprocess.call([processFilesFolderScript, tmp_folder])
            
            skip_compress=not __get_bool_key("compress", config["collector"], True)
            keep_processed_files=not __get_bool_key("deleteProcessedTempFiles", config["collector"], True)
            if skip_compress:
                print("skipping file compression")
            else:
                extension = "zip"
                if compressFormat == "tar":
                    extension = "tar"
                elif compressFormat == "gztar":
                    extension = "tar.gz"
                elif compressFormat == "bztar":
                    extension = "tar.bz2"

                output_file=os.path.join(outputLocation, zipfile_name)
                make_archive(tmp_folder, output_file, compressFormat, extension)
            
            if keep_processed_files:
                print("keep processed files in '%s' folder" % os.path.join(outputLocation, "tmp"))
            else:
                shutil.rmtree(os.path.join(outputLocation, "tmp"))
            
            if not skip_compress and outputScript:
                output_compressed_file="%s.%s" % (output_file, extension)
                subprocess.call([outputScript, output_compressed_file])
                deleteCompressedFile=__get_bool_key("deleteCompressedFile", config["collector"])
                if deleteCompressedFile:
                   os.remove(output_compressed_file)
            if fluentEventProcessor:
                fluentEventProcessor.close()

def make_archive(source, destination, format, extension):
    name = os.path.basename(destination)
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move("%s.%s" % (name, extension), "%s.%s" % (destination, extension))

def __get_str_key(key, map, default=None):
    if default:
        return map[key] if key in map else str(default)
    else:
        return map[key] if key in map else None

def __get_int_key(key, map, default=None):
    if default:
        return int(map[key]) if key in map else int(default)
    else:
        return map[key] if key in map else None

def __get_float_key(key, map, default=None):
    if default:
        return float(map[key]) if key in map else float(default)
    else:
        return map[key] if key in map else None

def __get_bool_key(key, map, default=False):
    return bool(map[key]) if key in map else bool(default)

def __setup_logger(config):
    logger = logging.getLogger('filecollector')
    consoleHandler = logging.StreamHandler(sys.stdout)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    if "logger" in config["collector"]:
        logger.setLevel(__get_str_key("level", config["collector"]["logger"], "INFO"))
        formatter = logging.Formatter(__get_str_key("format", config["collector"]["logger"], "%(message)s"))
        if "file" in config["collector"]["logger"] and config["collector"]["logger"]["file"]:
            fileHandler = logging.RotatingFileHandler(config["collector"]["logger"]["file"], maxBytes=(1048576*5), backupCount=5)
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    return logger

def __get_excludes(paths, logger):
    exclude_files=[]
    for filepath in paths:
        files=glob.glob(filepath)
        for file in files:
            exclude_files.append(file)
            logger.debug("file %s will be excluded from processing." % file)
    return exclude_files

def __disk_check(files, filteredLabels, outputLocation, config, logger):
    checkDiskSpace=__get_bool_key("checkDiskSpace", config, True)
    requiredDiskSpaceRatio=__get_float_key("requiredDiskSpaceRatio", config, 1.0)
    if checkDiskSpace:
        logger.debug("disk space check is enabled")
        fullSize=0
        for fileObject in files:
            if filteredLabels and fileObject["label"] not in filteredLabels:
                continue
            filePaths=glob.glob(fileObject["path"])
            for file in filePaths:
                fullSize = fullSize + os.stat(file).st_size
        freeSpace=0
        requiredFreeSpace=0
        total, used, freeSpace = shutil.disk_usage(outputLocation)
        requiredFreeSpace=int(fullSize * requiredDiskSpaceRatio)
        if fullSize > freeSpace:
            logger.error("there is not enough free space for file collection - free space: %d, required space: %d" % (freeSpace, requiredFreeSpace))
            sys.exit(1)
        else:
            logger.debug("free disk space: %d, required disk space: %d" % (freeSpace, requiredFreeSpace))
    else:
        logger.debug("disk space check is disabled")

class EventProcessor:
    
    def __init__(self, host, port, base_tag, identifier, message_field="message", include_time=False):
        self.host = host
        self.port = port
        self.base_tag = base_tag
        self.identifier = identifier
        self.message_field = message_field
        self.include_time = include_time
        if host and port:
            self.fluentSender = sender.FluentSender(base_tag, host=host, port=port)
        else:
            self.fluentSender = sender.FluentSender(base_tag)

    def process(self, name, path, real_path):
        with open(real_path, 'r', buffering=100000) as infile:
            if "*" in name:
                replaced_path=path.replace(os.sep, ".")
                name=name.replace("*", replaced_path)
            for line in infile:
                if self.include_time:
                    self.fluentSender.emit_with_time(name, time.time(), {self.message_field: line})
                else:
                    self.fluentSender.emit(name, {self.message_field: line})

    def close(self):
        self.fluentSender.close()

if __name__ == "__main__":
    pidfile=os.environ.get('FILECOLLECTOR_PIDFILE', 'filecollector-collector.pid')
    with PidFile(pidfile) as p:
        main(sys.argv[1:])