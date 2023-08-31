from __future__ import print_function
import os
import os.path
from dotenv import load_dotenv
from tabulate import *
from table2ascii import table2ascii as t2a, PresetStyle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
EVERYTHING_FILE = os.getenv("EVERYTHINGSHEET")
ME_ID = os.getenv("ME_ID")
ME = os.getenv("ME")
PERSON_ID = os.getenv("PERSON_ID")
PERSON = os.getenv("PERSON")
BOTFILE = os.getenv("BOTSHEET")

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/spreadsheets.readonly', 'https://www.googleapis.com/auth/contacts.readonly',
          'https://www.googleapis.com/auth/drive.metadata.readonly', 'https://www.googleapis.com/auth/drive.activity.readonly']


"""Shows basic usage of the People API.
Prints the name of the first 10 connections.
"""
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('global-token.json'):
    creds = Credentials.from_authorized_user_file('global-token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('global-token.json', 'w') as token:
        token.write(creds.to_json())


def main():
    try:
        serviceDrive = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        # results = service.files().list(
        #     pageSize=10, fields="nextPageToken, files(id, name)").execute()
        # items = results.get('files', [])
        # fileId = ""
        # getActivity()
        getSpreadsheetInfo("Things to Do")
        # updateSpreadsheetInfo("Sheet1")
        # response = serviceDrive.permissions().list(fileId = "").execute()
        # print(response)
        # if not items:
        #     print('No files found.')
        #     return
        # print('Files:')

        # for item in items:
        #     print(item)
        # print(u'{0} ({1})'.format(item['name'], item['id']))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


def updateSpreadsheetInfo(sheetname):
    try:

        serviceSheet = build('sheets', 'v4', credentials=creds)
        sheet = serviceSheet.spreadsheets()

        RANGE = f"{sheetname}!A:K"
        # SAMPLE_RANGE_NAME = "Things to Do!A:"
        # SAMPLE_SPREADSHEET_ID = ''
        # SAMPLE_RANGE_NAME = 'Class Data!A2:E'
        # Call the Sheets API
        setNote = {
            "updateCells": {
                "range": {
                    "sheetId": 0,
                    "startRowIndex": 0,
                    "endRowIndex": 3,
                    "startColumnIndex": 0,
                    "endColumnIndex": 3
                },
                "rows": [
                    {
                        "values": [
                            {
                                "userEnteredValue": {
                                    "stringValue": "update0"
                                }

                            },
                            {
                                "userEnteredValue": {
                                    "stringValue": "update0-1"
                                }

                            },
                            {
                                "userEnteredValue": {
                                    "stringValue": "update0-2"
                                }

                            }
                        ]
                    }
                ],
                "fields": "userEnteredValue"
            }
        }

        result = sheet.batchUpdate(spreadsheetId=BOTFILE, body={
                                   "requests": [setNote]}).execute()
        # jsonValues = {"sheetId": sheetname,"Sheel1": [{"values": [4,5,6]}] ,"fields": "StringValue"}
        # sheet = serviceSheet.spreadsheets()
        # result = sheet.values.batchUpdate(spreadsheetId=EVERYTHINGSHEET, requests = [{"appendCells": jsonValues}]).execute()

        return result

    except HttpError as err:
        print(err)


def getSpreadsheetInfo(sheetname):
    try:
        serviceSheet = build('sheets', 'v4', credentials=creds)
        RANGE = f"{sheetname}!A:G"
        # Call the Sheets API
        sheet = serviceSheet.spreadsheets()
        # print(sheet.get(spreadsheetId="").execute())

        result = sheet.values().get(spreadsheetId=EVERYTHING_FILE,
                                    range=RANGE).execute()
        values = result.get('values', [])
        # print(tabulate(values))

        # for value in values:
        #     print("row: ", value)

        # headers = values[2]
        # data = values[3:]

        # for header in range(0, len(headers)):
        #     if headers[header] == "":
        #         headers[header] = None

        # for line in data:
        #     for value in range(0, len(line)):
        #         if line[value] == "":
        #             line[value] = None
        # data[-1].append(None)
        # print(headers)
        # print(data)
        # output = t2a(
        #     header=headers,
        #     body=data,
        #     style=PresetStyle.thin_compact
        # )
        if not values:
            print('No data found.')
            return

        # print(tabulate(values))

        return values
    except HttpError as err:
        print(err)


def getActivity():

    # Call the Drive Activity API
    try:

        serviceActivity = build('driveactivity', 'v2', credentials=creds)
        results = serviceActivity.activity().query(body={
            'pageSize': 2
        }).execute()
        activities = results.get('activities', [])

        if not activities:
            print('No activity.')
        else:

            print('Recent activity:')
            # print(activities)
            # for activity in activities:
            #     if "Everything Sheet" in activity["targets"][0]["driveItem"]["title"]:
            #         print(activity)
            for activity in activities:
                time = getTimeInfo(activity)
                action = getActionInfo(activity['primaryActionDetail'])
                actors = map(getActorInfo, activity['actors'])
                targets = map(getTargetInfo, activity['targets'])
                actors_str, targets_str = "", ""
                actor_name = getUserName(actors_str.join(actors))
                target_name = targets_str.join(targets)
                # print(target_name)

                # Print the action occurred on drive with actor, target item and timestamp
                print(u'{0}: {1}, {2}, {3}'.format(
                    time, action, actor_name, target_name))

        return activities

    except HttpError as error:
        # TODO(developer) - Handleerrors from drive activity API.
        print(f'An error occurred: {error}')


def getUserName(id):

    try:
        if id == PERSON_ID:
            return PERSON
        elif id == ME_ID:
            return ME
        else:
            servicePeople = build('people', 'v1', credentials=creds, )
            response = servicePeople.people().get(
                resourceName=id, personFields="names").execute()
            # print(response.get("names")[0]["displayName"])
            return response.get("names")[0]["displayName"]

    except HttpError as err:
        print(err)


# Returns the name of a set property in an object, or else "unknown".
def getOneOf(obj):
    for key in obj:
        return key
    return 'unknown'


# Returns a time associated with an activity.
def getTimeInfo(activity):
    if 'timestamp' in activity:
        timestamp = activity["timestamp"].split("T")
        date = timestamp[0]
        time = timestamp[1]
        return f"{date} {time[0:-1]}"
        # return activity["timestamp"]
    if 'timeRange' in activity:
        return activity['timeRange']['endTime']
    return 'unknown'


# Returns the type of action.
def getActionInfo(actionDetail):
    return getOneOf(actionDetail)


# Returns user information, or the type of user if not a known user.
def getUserInfo(user):
    if 'knownUser' in user:
        knownUser = user['knownUser']
        isMe = knownUser.get('isCurrentUser', False)
        return u'people/me' if isMe else knownUser['personName']
    return getOneOf(user)


# Returns actor information, or the type of actor if not a user.
def getActorInfo(actor):
    if 'user' in actor:
        return getUserInfo(actor['user'])
    return getOneOf(actor)


# Returns the type of a target and an associated title.
def getTargetInfo(target):
    if 'driveItem' in target:
        title = target['driveItem'].get('title', 'unknown')
        return 'driveItem:"{0}"'.format(title)
    if 'drive' in target:
        title = target['drive'].get('title', 'unknown')
        return 'drive:"{0}"'.format(title)
    if 'fileComment' in target:
        parent = target['fileComment'].get('parent', {})
        title = parent.get('title', 'unknown')
        return 'fileComment:"{0}"'.format(title)
    return '{0}:unknown'.format(getOneOf(target))


if __name__ == '__main__':
    main()
