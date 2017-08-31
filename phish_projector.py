# -*- coding: utf-8 -*-

import requests
import sys
import argparse
import json
import base64
import csv
import ConfigParser
import os

def CreateGroup(email):
    json_data = {
                    "name": email,
                    "targets": [
                      {
                        "first_name": "",
                        "last_name": "",
                        "email": email,
                        "position": ""
                      }
                    ]
                }
    json_payload = json.dumps(json_data)

    try:
        print("Creating group: " + email)
        res = requests.post(admin_url + "/api/groups/?api_key=" + api_key, data=json_payload)
    except requests.exceptions.RequestException:
        print "some HTTP exception, please repeat"


def CreateMailTemplate(attachement_filepath):
    with open(os.path.abspath(attachement_dir + "/" + attachement_filepath),"rb") as f:
        encoded_file_content = base64.b64encode(f.read())



    json_data = {
                    "name": attachement_filepath,
                    "subject": subject,
                    "text": "",
                    "html": html_body,
                    "attachments": [
                        {
                            "name": attachement_filename,
                            "content": encoded_file_content,
                            # make type autodetection
                            "type":"application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        }
                    ],
                }

    # get images from settings
    for image_filepath in images_list:
        with open(os.path.abspath(attachement_dir + "/" + image_filepath),"rb") as f:
            encoded_image_content = base64.b64encode(f.read())
            image_data = {
                            "name": image_filepath,
                            "content": encoded_image_content,
                            # make type autodetection
                            "type":"image/png"
                         }
            json_data["attachments"].append(image_data)

    json_payload = json.dumps(json_data)

    try:
        print("Creating template: " + attachement_filepath)
        res = requests.post(admin_url + "/api/templates/?api_key=" + api_key, data=json_payload)
    except requests.exceptions.RequestException:
        print "some HTTP exception, please repeat"


def CreateCampaign(email, attachement_filepath):

    CreateGroup(email)
    CreateMailTemplate(attachement_filepath)
    json_data = {
                    "name": email,
                    "template": {
                      "name": attachement_filepath,
                    },
                    "page": {
                      "name": "ya"
                    },
                    "smtp": {
                      "name": sending_profile
                    },
                    "url": "",
                    "groups": [
                      {
                        "name": email,
                      }
                    ]
                }
    if launch_date is not "":
        json_data["launch_date"] = launch_date

    json_payload = json.dumps(json_data, ensure_ascii=False, encoding="utf-8")

    try:
        print("Creating campaign: " + email)
        res = requests.post(admin_url + "/api/campaigns/?api_key=" + api_key, data=json_payload)
    except requests.exceptions.RequestException:
        print "some HTTP exception, please repeat"


def DeleteAll():
    # delete campaigns
    try:
        res = requests.get(admin_url + "/api/campaigns/summary?api_key=" + api_key)
        res = json.loads(res.text)
    except requests.exceptions.RequestException:
        print "some HTTP exception, please repeat"
    total = res["total"]
    if total > 0:
        first_id = res["campaigns"][0]["id"]
        for i in range (first_id, first_id+total):
            try:
                print("Deleting campaign: " + str(i))
                res = requests.delete(admin_url + "/api/campaigns/" + str(i) + "?api_key=" + api_key)
            except requests.exceptions.RequestException:
                print "some HTTP exception, please repeat"

    # delete groups
    try:
        res = requests.get(admin_url + "/api/groups/summary?api_key=" + api_key)
        res = json.loads(res.text)
    except requests.exceptions.RequestException:
        print "some HTTP exception, please repeat"
    total = res["total"]
    if total > 0:
        first_id = res["groups"][0]["id"]
        for i in range (first_id, first_id+total):
            try:
                print("Deleting group: " + str(i))
                res = requests.delete(admin_url + "/api/groups/" + str(i) + "?api_key=" + api_key)
            except requests.exceptions.RequestException:
                print "some HTTP exception, please repeat"

    # delete templates
    try:
        res = requests.get(admin_url + "/api/templates/?api_key=" + api_key)
        res = json.loads(res.text)
    except requests.exceptions.RequestException:
        print "some HTTP exception, please repeat"
    for template in res:
        template_id = template["id"]
        try:
            print("Deleting template: " + str(template_id))
            res = requests.delete(admin_url + "/api/templates/" + str(template_id) + "?api_key=" + api_key)
        except requests.exceptions.RequestException:
            print "some HTTP exception, please repeat"


# add arguments
parser = argparse.ArgumentParser()
parser.add_argument("--delete-all", help="action: delete campaings,email templates,groups", action="store_true")
args = parser.parse_args()


#parse arguments
flag_delete_all = args.delete_all


#parse config
config = ConfigParser.RawConfigParser()
config.read('projector.cfg')
admin_url = config.get('DEFAULT',"admin_url")
api_key = config.get('DEFAULT',"key")
pairs_file = config.get('DEFAULT',"pairs_file")
html_file = config.get('DEFAULT',"html_file")
images_list = json.loads(config.get('DEFAULT','images'))
sending_profile = config.get('DEFAULT','sending_profile')
launch_date = config.get('DEFAULT','launch_date')
attachement_dir = config.get('DEFAULT','attachement_dir')
subject = config.get('DEFAULT','subject')
attachement_filename = config.get('DEFAULT','attachement_filename')

if  flag_delete_all:
    DeleteAll()
    sys.exit()

with open(html_file,"rb") as f:
    html_body = f.read()

with open(pairs_file,"rb") as csvfile:
    pairs = csv.reader(csvfile)
    for pair in pairs:
        CreateCampaign(pair[0],pair[1])





