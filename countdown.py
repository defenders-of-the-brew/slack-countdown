#!/usr/bin/python
from flask.ext.script import Manager
from flask import Flask
from datetime import datetime
import json
import os
import requests
import workdays

app = Flask(__name__)


manager = Manager(app)

"""Creates web app to be deployed on Heroku."""

SLACK_URL = os.environ.get('SLACK_URL')
if not SLACK_URL:
    print("Missing environment variable SLACK_URL")
    exit(1)

def days_from_christmas():
    """Calculates the number of days between the current date and the next
    Christmas. Returns the string to displayed.
    """
    currentdate = datetime.now()
    christmas = datetime(datetime.today().year, 12, 25)
    if christmas < currentdate:
        christmas = date(datetime.today().year + 1, 12, 25)
    delta = christmas - currentdate
    days = delta.days
    if days == 1:
        return "%d day from the nearest Christmas" % days
    else:
        return "%d days from the nearest Christmas" % days


def days_from_date(strdate, business_days):
    """ Returns the number of days between strdate and today. Add one to date
    as date caclulate is relative to time
    """
    current_date = datetime.now()
    end_date = datetime.strptime(strdate, "%Y-%m-%d %H:%M:%S")
    delta = end_date - current_date
    if delta.days < 0:
        exit()
    return delta

def events(strdate, event, business_days):
    """ Returns string to be displayed with the event mentioned. Sends an error
    if date is incorrect
    """
    delta = days_from_date(strdate, False)
    days = delta.days
    hours = delta.seconds/60/60
    minutes = delta.seconds/60%60
    seconds = delta.seconds%60

    return "%02dD %02dH %02dM %02dS until %s" % (days, hours, minutes, seconds, event)


def date_only(strdate, business_days):
    """ Returns string to be displayed. Sends error message if date is
    in the past
    """
    delta = days_from_date(strdate)
    days = delta.days
    hours = delta.seconds/60/60
    minutes = delta.seconds/60%60
    seconds = delta.seconds%60
    return "%02dD %02dH %02dM %02dS until %s" % (days, hours, minutes, seconds, business_days)

def post(out):
    """ Posts a request to the slack webhook. Payload can be customized
    so the message in slack is customized. The variable out is the text
    to be displayed.
    """

    payload = {
        "attachments": [
            {
                "title": "COUNTDOWN!",
                "text": out,
                "color": "#7CD197"
            }
        ]
    }

    r = requests.post(SLACK_URL, data=json.dumps(payload))


def post_error():
    """Sends error message in Slack to alert the user
    about the incorrect date argument
    """

    payload = {
        "attachments": [
            {
                "title": "Error",
                "text": ("Date entered must be in the future. "
                        "\n Go to the <https://heroku.com|Heroku Scheduler> for you app and edit"
                        " the command"),
                        "color": "#525162"
            }
        ]
    }

    r = requests.post(SLACK_URL, data=json.dumps(payload))


@manager.option("-d", "--deadline", dest="date",
                      help="Specify the deadline in ISO format: yyyy-mm-dd",
                      metavar="DEADLINE")
@manager.option("-e", "--event", dest="event",
                      help="Name of the deadline event",metavar="EVENT")
@manager.option("-b", "--business-days", dest="business_days", action="store_true",
                      help="Give the count of business days only")
def deadline(date, event, business_days):
    """ Method takes two optional arguments. Displays in slack channel
    the number of days till the event. If no arguments are given,
    the number of days till Christmas is displayed.
    """
    result = ""
    if date:
        if event:
            result = events(date, event, business_days)
        else:
            result = date_only(date, business_days)
    else:
        result = days_from_christmas()
    post(result)



@manager.command
def initiate():
    payload = { "text": "App is now connected to your Slack Channel."}
    r = requests.post(SLACK_URL, data=json.dumps(payload))




if __name__ == "__main__":
    manager.run()


