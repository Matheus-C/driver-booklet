#!/bin/bash
docker stop driver-booklet;
docker rm -f driver-booklet;
docker image rm -f driver-booklet;
docker-compose up -d;