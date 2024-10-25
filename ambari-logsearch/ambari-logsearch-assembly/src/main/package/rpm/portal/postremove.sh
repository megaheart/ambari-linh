#!/bin/bash
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

LOGSEARCH_SCRIPT_LINK_NAME="/usr/bin/logsearch"
LOGSEARCH_ETC_FOLDER="/etc/ambari-logsearch-portal"
LOGSEARCH_CONF_DIR_LINK="$LOGSEARCH_ETC_FOLDER/conf"

rm -f $LOGSEARCH_SCRIPT_LINK_NAME
if [ -f "$LOGSEARCH_CONF_DIR_LINK" ]; then
  rm -f $LOGSEARCH_CONF_DIR_LINK
fi
if [ -d "$LOGSEARCH_CONF_DIR_LINK" ]; then
  rm -rf $LOGSEARCH_CONF_DIR_LINK
fi

if [ -d "$LOGSEARCH_ETC_FOLDER" ]; then
  rm -rf $LOGSEARCH_ETC_FOLDER
fi