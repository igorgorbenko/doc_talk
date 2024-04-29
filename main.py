import datetime
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendar:
    def __init__(self, credentials_file='credentials.json', token_file='token.json'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self.authenticate_google_calendar()

    def authenticate_google_calendar(self):
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, ["https://www.googleapis.com/auth/calendar"])
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file,
                                                                 ["https://www.googleapis.com/auth/calendar"])
                creds = flow.run_local_server(port=0)
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        return build("calendar", "v3", credentials=creds)

    def get_upcoming_events(self, max_results=10):
        now = datetime.datetime.utcnow().isoformat() + "Z"
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            events = events_result.get('items', [])
            if not events:
                print("No upcoming events found.")
            return events
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def check_for_overlaps(self, start_time, end_time):
        print(start_time, end_time)
        try:
            events = self.service.events().list(
                calendarId='primary',
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True
            ).execute().get('items', [])
            print('events', events)
            for event in events:
                if event['start'].get('dateTime') < end_time and event['end'].get('dateTime') > start_time:
                    return True
            return False
        except HttpError as error:
            print(f"An error occurred while checking for overlaps: {error}")
            return True  # Assume overlap in case of error to prevent duplicate event creation

    def add_new_event(self, event):
        start_time = event['start']['dateTime']
        end_time = event['end']['dateTime']

        if self.check_for_overlaps(start_time, end_time):
            print("Cannot create event. It overlaps with an existing event.")
            return None

        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))
            return event
        except HttpError as error:
            print(f"An error occurred: {error}")
            return None

    def find_free_slots(self):
        # Define the time range for the search: the next 30 days
        now = datetime.datetime.utcnow()
        end = now + datetime.timedelta(days=30)

        # Define working hours (local time, here assumed to be America/Los_Angeles)
        timezone = 'Gulf Standard Time'
        business_hours_start = datetime.time(8, 0, 0)  # 8:00 AM
        business_hours_end = datetime.time(20, 0, 0)  # 8:00 PM

        free_slots = []
        current_date = now

        while current_date < end:
            if current_date.weekday() < 5:  # Monday to Friday are 0 to 4
                start_datetime = datetime.datetime.combine(current_date, business_hours_start).isoformat() + 'Z'
                end_datetime = datetime.datetime.combine(current_date, business_hours_end).isoformat() + 'Z'
                body = {
                    "timeMin": start_datetime,
                    "timeMax": end_datetime,
                    "items": [{"id": "primary"}],
                    "timeZone": timezone
                }
                free_busy_response = self.service.freebusy().query(body=body).execute()
                print(free_busy_response)
                busy_times = free_busy_response['calendars']['primary']['busy']

                if not busy_times:
                    free_slots.append((start_datetime, end_datetime))
                else:
                    # Check for free slots between busy times
                    last_end_time = business_hours_start
                    for busy in busy_times:
                        busy_start = datetime.datetime.fromisoformat(busy['start'][:-1])  # remove the 'Z'
                        busy_end = datetime.datetime.fromisoformat(busy['end'][:-1])  # remove the 'Z'
                        if last_end_time < busy_start.time():
                            free_start = datetime.datetime.combine(current_date, last_end_time).isoformat() + 'Z'
                            free_end = datetime.datetime.combine(current_date, busy_start.time()).isoformat() + 'Z'
                            free_slots.append((free_start, free_end))
                        last_end_time = busy_end.time()
                    if last_end_time < business_hours_end:
                        free_start = datetime.datetime.combine(current_date, last_end_time).isoformat() + 'Z'
                        free_end = datetime.datetime.combine(current_date, business_hours_end).isoformat() + 'Z'
                        free_slots.append((free_start, free_end))

            current_date += datetime.timedelta(days=1)

        return free_slots



if __name__ == "__main__":
    calendar = GoogleCalendar()
    new_event = {
        'summary': 'NEWWW Meeting with Team',
        'location': 'Office',
        'description': 'Discuss project updates',
        'start': {
            'dateTime': '2024-05-01T10:00:00+04:00'
        },
        'end': {
            'dateTime': '2024-05-01T11:00:00+04:00'
        }
    }
    calendar.add_new_event(new_event)
    events = calendar.get_upcoming_events()
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event.get('summary'))

    free_slots = calendar.find_free_slots()
    for slot in free_slots:
        print("Free slot from", slot[0], "to", slot[1])