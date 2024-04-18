#!/bin/bash

# Author: Eshan Roy (Eshanized)

BRANCH=master
CMSG="⏳ @eshanized updated the repository!!!"

git add .
git commit -m "${CMSG}"
git push origin "${BRANCH}"