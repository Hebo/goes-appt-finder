## GOES Appt finder thingy

AWS Lambda script to find openings for Global Entry appointments and send SNS notifications.

Based on [this post](https://www.reddit.com/r/churning/comments/3mqmjw/nonchurning_rant_global_entry_interviews_at_sfo/cvhdodc/)

Create Lambda function
```

make build

aws lambda create-function \
--region us-west-2 \
--function-name FindGoesAppt \
--zip-file fileb://deploy.zip \
--role arn:aws:iam::127015619127:role/service-role/LambdaRole \
--environment Variables="{LOGIN=addme,PASSWORD=addme}" \
--handler lambda_function.lambda_handler \
--runtime python2.7 \
--timeout 60
```


Update

`make deploy`

Update Credentials

```
aws lambda update-function-configuration \
--function-name FindGoesAppt \
--environment Variables="{LOGIN=addme,PASSWORD=addme}"
```


Add libs if needed
```
pip install mechanize -t .
```