#!/bin/bash

#stage=dev
echo "running deployment for " $stage
# run sls deploy
echo "starting serverless deploy"
npx sls deploy --stage $stage
SLS_DEPLOY_RESULT=$?
if [ $SLS_DEPLOY_RESULT -ne 0 ]; then
    echo "serverless failed"
    exit $SLS_DEPLOY_RESULT
fi
