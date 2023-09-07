#!/usr/bin/env bash
docker build -t ossimyllymaki/bank-transaction-analyzer -f Dockerfile_base .
docker push ossimyllymaki/bank-transaction-analyzer