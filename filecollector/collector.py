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
            output_file=os.path.join(outputLocation, nTime + ".zip")
            make_archive(tmp_folder, output_file)
            shutil.rmtree(os.path.join(outputLocation, "tmp"))
            if outputScript:
                pass            

def make_archive(source, destination):
    base = os.path.basename(destination)
    name = base.split('.')[0]
    format = base.split('.')[1]
    archive_from = os.path.dirname(source)
    archive_to = os.path.basename(source.strip(os.sep))
    shutil.make_archive(name, format, archive_from, archive_to)
    shutil.move('%s.%s'%(name,format), destination)

if __name__ == "__main__":
    main()