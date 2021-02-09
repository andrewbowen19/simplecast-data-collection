# Script to export CSV file for Maggie
# Export for each pod over past 30 days:
	# Downloads
	# # of episodes published per week

import pandas as pd
import json
import os
import http.client
import datetime


def getSimplecastResponse(query_params):
    '''
    Method to establish connection to Simplecast API
    query_params - string for HTTP request params
    Check Simplecast docs for this
    '''
    # Figure out how to set this as an env variable
    auth = os.environ['SIMPLECAST_TOKEN']
    payload = ''
    url = "api.simplecast.com"
    headers = {'authorization': auth}
    conn = http.client.HTTPSConnection(url)
    conn.request("GET", query_params, payload, headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()

    return data.decode('utf-8')

def simplecast_data_collector():
	'''
	Function to get downloads/# of episodes per podcast
	'''
	# Default is 30 days ago
	account_id = os.environ['SC_ACCOUNT_ID']
	days_ago = 30
	start_date = start_date = (datetime.datetime.now() - datetime.timedelta(days_ago)).date()

	print('Getting all podcast download data!')
	dat = json.loads(getSimplecastResponse(f'/analytics/podcasts?account={account_id}&start_date={start_date}&limit=500')) # Change to 500 for real deal
	collection = dat['collection']
	print(collection)
	df = pd.DataFrame(collection)

	df = df.drop(['href', 'published_at', 'rank'], axis=1)
	df['downloads'] = [x['total'] for x in df['downloads']]

	# Getting episode #s
	avg_episodes = []
	for p in collection:
		print('Re-formatting dataframe for: ', p['title'])
		# p['downloads'] = p['downloads']['total']

		# Getting N_episodes
		pod_title = p['title']
		pod_id = p['id']

		print('Grabbing episode data...')
		ep_dat = json.loads(getSimplecastResponse(f'/podcasts/{pod_id}/episodes?&sort=published_at_desc&start_date={start_date}&limit=60'))

		print(f'Counting episodes for {pod_title}')
		n = 0
		for e in ep_dat['collection']:
			
			days_since_release = e['days_since_release']
			if days_since_release < 31:
				n += 1
			else:
				pass

		
		avg = n/4
		avg_episodes.append(avg)
		print(f'# of EPISODES: {n}') 
		print(f'Average # of episodes per week: {avg}')
		print('#################################')
		print('#################################')

	df['episodes_per_week'] = avg_episodes

	print(df.head())

	# Export to csv
	today = (datetime.datetime.now()).date()
	path = os.path.join('.','output',f'pod-export-{today}.csv')
	df.to_csv(path)

	return df



if __name__ =="__main__":
	simplecast_data_collector()



