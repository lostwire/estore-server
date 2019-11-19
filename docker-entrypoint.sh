#!/bin/bash
while ! $1 initialize; do sleep 10; done
python3 -m $1
