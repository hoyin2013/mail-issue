#!/usr/bin/env bash

# 强制覆盖本地代码
# git fetch --all && git reset --hard origin/master && git pull

# 删除容器并重建容器
docker rm -f mailissue
docker run --name mailissue -v "$PWD":/usr/src/app -w /usr/src/app -p 8000:8000 -d django:3


