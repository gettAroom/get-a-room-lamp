import requests
import time
import urlparse
import json
import argparse
from datetime import datetime, timedelta

class InvalidTimeError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def _change_lamp_status(action, payload):
    lampUrl = 'https://api.lifx.com/v1/lights/all/{0}'
    token = "c01bb16534226e6db29442481708067a010731ff0d2d1202da2aef438d6184b7"

    headers = { "Authorization": "Bearer %s" % token, }
    r = requests.put(lampUrl.format(action), data=payload, headers=headers)

# available section
def set_pending_status():
    print 'start set_pending_status'
    payload = {
            "power": "on",
            "color": "yellow",
            "brightness": 0.6
        }
    _change_lamp_status('state', payload)
    print 'finish set_pending_status'

def set_available_status():
    print 'start set_available_status'
    payload = {
            "power": "on",
            "color": "green",
            "brightness": 0.6
        }
    _change_lamp_status('state', payload)
    print 'finish set_available_status'
# available section

# occupied section
def set_ending_status():
    print 'start set_ending_status'
    payload = {
            "power": "off",
        }
    _change_lamp_status('state', payload)

    payload = {
            "power": "on",
            "color": "red",
            "brightness": 0.7
        }
    _change_lamp_status('state', payload)

    payload = {
            "power": "off",
        }
    _change_lamp_status('state', payload)
    print 'finish set_ending_status'

def set_occupied_status():
    print 'start set_occupied_status'
    payload = {
            "power": "on",
            "color": "red",
            "brightness": 0.6
        }
    _change_lamp_status('state', payload)
    print 'finish set_occupied_status'
# occupied section

def is_room_available(id):
    print "start get_room_status"
    global roomResponse

    awsUrl = 'http://ec2-54-186-191-127.us-west-2.compute.amazonaws.com:9090/api/rooms/'
    response = requests.get(urlparse.urljoin(awsUrl, id))
    roomResponse = json.loads(response.text)

    fromTime = datetime.strptime(roomResponse["nextMeeting"]["from"], "%Y-%m-%dT%H:%M:%S.%fZ")
    fromTime = fromTime + timedelta(hours=3)

    toTime = datetime.strptime(roomResponse["nextMeeting"]["to"], "%Y-%m-%dT%H:%M:%S.%fZ")
    toTime = toTime + timedelta(hours=3)

    now = datetime.now()

    if (fromTime <= now and now <= toTime):
        print 'occupied'
        return False
    else:
        print 'available'
        return True

def does_meeting_start(thresholdInMinutes):
    print "start does_meeting_start"
    thresholdInSeconds = thresholdInMinutes * 60

    # TimeStamp format from JSON: '2016-07-20T01:30:00.000Z'
    fromTime = datetime.strptime(roomResponse["nextMeeting"]["from"], "%Y-%m-%dT%H:%M:%S.%fZ")
    fromTime = fromTime + timedelta(hours=3)
    now = datetime.now()
    print 'fromTime: {0}; now:{1}'.format(fromTime, now)

    if (now > fromTime):
        raise InvalidTimeError("Now time is greater then next meeting 'FromTime'")

    deltaInSeconds = (fromTime - now).total_seconds()

    if (deltaInSeconds <= thresholdInSeconds):
        print 'True'
        return True
    else:
        print 'False'
        return False

def does_meeting_end(thresholdInMinutes):
    print "start does_meeting_end"
    thresholdInSeconds = thresholdInMinutes * 60

    # TimeStamp format from JSON: '2016-07-20T01:30:00.000Z'
    toTime = datetime.strptime(roomResponse["nextMeeting"]["to"], "%Y-%m-%dT%H:%M:%S.%fZ")
    toTime = toTime + timedelta(hours=3)
    now = datetime.now()
    print 'toTime: {0}; now:{1}'.format(toTime, now)

    deltaInSeconds = (toTime - now).total_seconds()
    if (deltaInSeconds <= thresholdInSeconds):
        print 'True'
        return True
    else:
        print 'False'
        return False

def main():
    print 'Welcome to the LampClient!'

    parser = argparse.ArgumentParser(description='LampClient for GettARoom application!')
    parser.add_argument('-roomId', nargs='?', type=str, help='The room id')
    parser.add_argument('-startThreshold', nargs='?', type=int, help='Meeting is about to start threshold')
    parser.add_argument('-endThreshold', nargs='?', type=int, help='Meeting is about to end threshold')
    args = parser.parse_args()

    while True:
        isAvailable = is_room_available(args.roomId)
        if (isAvailable):
            print 'Room "{0}" is available'.format(args.roomId)
            try:
                if (does_meeting_start(args.startThreshold)):
                    set_pending_status()
                else:
                    set_available_status()
            except InvalidTimeError as e:
                print 'InvalidTimeError occurred, message:', e.value
                set_available_status()
        else:
            print 'Room "{0}" is occupied'.format(args.roomId)
            if (does_meeting_end(args.endThreshold)):
                set_ending_status()
            else:
                set_occupied_status()
        print 'sleeping for 4 seconds'
        time.sleep(4)

if __name__ == "__main__": main()
