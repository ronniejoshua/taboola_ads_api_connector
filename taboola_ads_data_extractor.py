import requests
import datetime as dt
import pytz


class TaboolaAdsApi(object):
    def __init__(self):
        self.BASE_URL = 'https://backstage.taboola.com'

    def generate_access_token(self, client_id, client_secret, username, password):
        URL = '{}/backstage/oauth/token'.format(self.BASE_URL)
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'username': username,
            'password': password,
            'grant_type': 'password',
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                                            'Accept': 'application/json'}
        response = requests.post(
                                    URL,
                                    headers=headers,
                                    params=payload
                                )
        if response.status_code == 200:
            print("Got an access token.")
        elif response.status_code >= 400 and response.status_code < 500:
            print('{}: {}'.format(
                                    response.json().get('error'),
                                    response.json().get('error_description')
                                  )
                    )
            raise RuntimeError
        return response.json().get('access_token', None)

    def get_campaign_day_breakdown_stats(self, access_token, account_id, _start_date, _end_date):
        PATH = '/backstage/api/1.0/{}/reports/campaign-summary/dimensions/campaign_day_breakdown'.format(account_id)
        taboola_token = access_token
        URL = self.BASE_URL + PATH
        payload = {
            'start_date': _start_date,
            'end_date': _end_date
        }
        headers = {'Authorization': 'Bearer {}'.format(taboola_token),
                   'Accept': 'application/json'}
        response = requests.get(URL, headers=headers, params=payload)
        # return json.dumps(response.json()['results'])
        return response.json()['results']

    @staticmethod
    def gen_params_dates(num_weeks_back, num_weeks_skip, to_today=False):
        TZ = 'Asia/Jerusalem'
        result = list()
        for weeks_back in range(num_weeks_skip, num_weeks_back):

            today = dt.datetime.now(pytz.timezone(TZ))
            yesterday = today - dt.timedelta(1)

            # date_start : Make it a sunday
            date_start = yesterday - dt.timedelta((yesterday.weekday() + 1) % 7)
            date_start = date_start - dt.timedelta(weeks_back * 7)

            # If num_weeks_skip == 0
            if weeks_back == 0:

                # If to_today=True & today is not a sunday
                if to_today and (today.weekday() != 6):
                    date_end = today
                else:
                    date_end = yesterday

            # num_weeks_skip != 0
            else:
                date_end = date_start + dt.timedelta(6)

            record = {'date_from': date_start.strftime('%Y-%m-%d'), 'date_to': date_end.strftime('%Y-%m-%d')}
            result.append(record)

            if to_today and weeks_back == 0 and today.weekday() == 6:
                record = {'date_from': today.strftime('%Y-%m-%d'), 'date_to': today.strftime('%Y-%m-%d')}
                result.append(record)
        return result



if __name__ == "__main__":
    my_client_id = 'provide-your-client-id'
    my_client_secret = 'provide-your-client-secret'
    my_username = 'provide-your-username-email'
    my_password = 'provide-your-password'
    my_account_id = 'provide-your-account-id'

    ads_extractor = TaboolaAdsApi()
    taboola_access_token = ads_extractor.generate_access_token(
                            my_client_id, 
                            my_client_secret, 
                            my_username, 
                            my_password
                            )

    date_intervals = ads_extractor.gen_params_dates(2, 0, 0)

    aggregated_data = list()
    for date_interval in date_intervals:
        extracted_data = ads_extractor.get_campaign_day_breakdown_stats(
                                                                        taboola_access_token,
                                                                        my_account_id,
                                                                        date_interval['date_from'],
                                                                        date_interval['date_to']
                                                                        )
        if len(extracted_data) > 0:
            data_period = date_interval['date_from'].replace('-', '')
            # Creates a list of {date} & {data} for each date interval
            aggregated_data.append({'data_period': data_period, 'extracted_data': extracted_data})
