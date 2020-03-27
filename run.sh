#!/bin/sh

if [ -n "$AMO_STORAGE_VERSION" ]; then
  AMO_STORAGE_VERSION="${AMO_STORAGE_VERSION}"
else
  AMO_STORAGE_VERSION=1.1-rc2
fi

AMO_STORAGE_PREFIX=/tmp/amo-storage

if [ ! -d "${AMO_STORAGE_PREFIX}/amo-storage-${AMO_STORAGE_VERSION}" ]; then
  AMO_STORAGE_RELEASE_URL=https://github.com/amolabs/amo-storage/archive/v${AMO_STORAGE_VERSION}.tar.gz
  mkdir $AMO_STORAGE_PREFIX
  wget -O $AMO_STORAGE_PREFIX/$AMO_STORAGE_VERSION.tar.gz $AMO_STORAGE_RELEASE_URL
  tar -C $AMO_STORAGE_PREFIX -xzvf $AMO_STORAGE_PREFIX/$AMO_STORAGE_VERSION.tar.gz
else
  echo "Repo amo-stroage-v${AMO_STORAGE_VERSION} exists"
fi

if [ -z "$(docker images -q amo-storage:${AMO_STORAGE_VERSION})" ]; then
  echo "Build amo-storage:${AMO_STORAGE_VERSION}"
  docker build -t amo-storage:${AMO_STORAGE_VERSION} -t amo-storage:latest $AMO_STORAGE_PREFIX/amo-storage-$AMO_STORAGE_VERSION
else
  echo "Docker image amo-storage:${AMO_STORAGE_VERSION} exists"
fi

docker-compose up -d