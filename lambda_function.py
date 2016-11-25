from __future__ import print_function

import os
import re

import mechanize
import boto3

SNS_TOPIC_ARN = "arn:aws:sns:us-west-2:127015619127:GoesAppts"

CENTERS = [
    {
        "id": "5446",
        "name": "SFO",
        "mindate": 0,
        "maxdate": 201705251015 # 2017-05-25 10:15
    }
]

def find_appointment(login, password):
    """Find an appointment"""
    found = []
    for center in CENTERS:
        br = mechanize.Browser()
        br.open("https://goes-app.cbp.dhs.gov/main/goes")
        br.select_form(nr=1)
        br["j_username"] = login
        br["j_password"] = password
        br.submit()

        # br.follow_link(text='Enter')
        # Skip "human check" interstitial
        br.open("https://goes-app.cbp.dhs.gov/goes/HomePagePreAction.do")

        data = br.response().read()

        br.select_form('ApplicationActionForm')
        br.form.set_all_readonly(False)
        br['actionFlag'] = 'existingApplication'
        br['homepageProgramIndex'] = '0'
        resp = br.submit()

        br.select_form('ConfirmationForm')
        br.form.set_all_readonly(False)
        br['actionFlag'] = 'reschedule'
        resp = br.submit()

        br.select_form('ApplicationActionForm')
        br.form.set_all_readonly(False)
        br['forwardFlag'] = 'next'
        br['selectedEnrollmentCenter'] = [center["id"]]
        resp = br.submit()

        data = resp.get_data()

        matches = re.findall(r"'scheduleForm', 'scheduleForm:schedule1', '(\d{12})'", data)
        first = matches[0]
        timeformat = first[:4]+'-'+first[4:6]+'-'+first[6:8]+'T'+first[8:10]+':'+first[10:12]
        first = int(first)

        if center["mindate"] < first < center["maxdate"]:
            found.append({
                "center_id": center["id"],
                "center_name": center["name"],
                "time": timeformat
            })
            print('New appt avail', timeformat, center["name"])

    return found

def lambda_handler(event, context):
    """Do some shit"""
    #print("Received event: " + json.dumps(event, indent=2))
    login = os.environ['LOGIN']
    password = os.environ['PASSWORD']
    sns_client = boto3.client('sns')

    found = find_appointment(login, password)
    if found:
        message = ""
        for appt in found:
            message += ("Date: {}, Center: {}\n".format(appt["time"], appt["center_name"]))
        message += "Login: https://goes-app.cbp.dhs.gov/goes/jsp/login.jsp"

        print("Publishing message: {}".format(message))

        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="GOES Appointments Found",
            Message=message
        )
    else:
        print("No appointments found")

    return "Ayy"
