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

import setuptools

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name="filecollector",
    version="0.1.1",
    author="Oliver Szabo",
    author_email="oleewere@gmail.com",
    description="Simple file collector - compress/serve/send/anonymizie files",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/oleewere/filecollector",
    scripts=["bin/filecollector"],
    packages=setuptools.find_packages(),
    install_requires=['PyYAML>=5.3.1', 'pid>=3.0.3', 'fluent-logger>=0.9.6'],
    license='Apache 2.0',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)