#!/usr/bin/env bash
#
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
# limitations under the License.

# Start a Docker-based build environment

set -e -u

cd "$(dirname "$0")"

# OS to build on
: ${BUILD_OS:=centos9}

# Directory with Ambari source
: ${AMBARI_DIR:=$(pwd -P)}

# Maven version
: ${MAVEN_VERSION:=3.9.9}

check_docker_image_exists() {
  local image=$1
  if docker image inspect "$image" > /dev/null 2>&1; then
    return 0  # exists
  else
    return 1  # not exists
  fi
}

if ! check_docker_image_exists ambari-build-base:${BUILD_OS}; then
  echo "Building base image for ${BUILD_OS}..."
  docker build -t ambari-build-base:${BUILD_OS} dev-support/docker/${BUILD_OS}
else
  echo "Base image for ${BUILD_OS} already exists."
fi

if ! check_docker_image_exists ambari-build:${BUILD_OS}; then
  echo "Building build image for ${BUILD_OS}..."
  docker build -t ambari-build:${BUILD_OS} --build-arg BUILD_OS="${BUILD_OS}" --build-arg MAVEN_VERSION="${MAVEN_VERSION}" dev-support/docker/common
else
  echo "Build image for ${BUILD_OS} already exists."
fi

# USER_NAME=${SUDO_USER:=$USER}
# USER_ID=$(id -u "${USER_NAME}")
# GROUP_ID=$(id -g "${USER_NAME}")
# USER_TAG="ambari-build-${USER_NAME}-${USER_ID}:${BUILD_OS}"

# if check_docker_image_exists "$USER_TAG"; then
#   echo "User image $USER_TAG already exists."
# else
#   echo "Building user image $USER_TAG..."
#   # Create a user in the container with the same UID as the current user
#   # This allows us to run the container as that user and avoid permission issues
#   # when mounting directories from the host.
#   # The group ID is also set to match the current user's group ID.
#   docker build -t "$USER_TAG" - <<UserSpecificDocker
# FROM ambari-build:${BUILD_OS}
# RUN groupadd --non-unique -g ${GROUP_ID} ${USER_NAME}
# RUN useradd -g ${GROUP_ID} -u ${USER_ID} -k /root -m ${USER_NAME}
# ENV HOME /home/${USER_NAME}
# UserSpecificDocker

TTY_MODE="-t -i"
if [ "$#" -gt 0 ]; then
  TTY_MODE=""
fi

# echo "Run container $TTY_MODE $USER_TAG"
echo "Run container $TTY_MODE ambari-build:${BUILD_OS}" 
# By mapping the .m2 directory you can do an mvn install from
# within the container and use the result on your normal
# system.  This also allows a significant speedup in subsequent
# builds, because the dependencies are downloaded only once.

if docker inspect ambari-build-container > /dev/null 2>&1; then
  echo "Container ambari-build-container already exists. Starting it..."
  docker start ambari-build-container
  echo "To attach to the container, run:"
  echo "docker exec -it ambari-build-container bash"
else
  echo "Creating and starting container ambari-build-container..."
  docker run \
  --name ambari-build-container \
  -u root \
  -h "${BUILD_OS}" \
  -v "${AMBARI_DIR}:/root/src:delegated" \
  -v "${HOME}/.m2:/root/.m2:cached" \
  -w "/root/src" \
  -d \
  ambari-build:${BUILD_OS} \
  sleep infinity
  echo "To attach to the container, run:"
  echo "docker exec -it ambari-build-container bash"
fi


