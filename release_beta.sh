#! /bin/sh
git tag -d latest_beta
git tag latest_beta -m "`date`: $1"
git push --tags 
