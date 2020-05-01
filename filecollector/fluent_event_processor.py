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

import time
from fluent import sender
from fluent import event

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
            for line in infile:
                if self.include_time:
                    self.fluentSender.emit_with_time(name, time.time(), {self.message_field: line})
                else:
                    self.fluentSender.emit(name, {self.message_field: line})

    def close(self):
        self.fluentSender.close()

    
