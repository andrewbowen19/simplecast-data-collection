# Script to export CSV file for Maggie
# Export for each pod over past 30 days:
	# Downloads
	# # of episodes published per week

import pandas as pd
import json
import os
import http.client
import datetime

# Email imports
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

days_ago = 30
start_date = start_date = (datetime.datetime.now() - datetime.timedelta(days_ago)).date()
today = (datetime.datetime.now()).date()

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
	
	path = os.path.join('.','output',f'pod-export-{today}.csv')
	df.to_csv(path)

	return df

def send_export(send_from, send_to, subject, text, files=None,
			  server="127.0.0.1"):
	'''
	Sends exported file in an email
	recipient_emails - list-like, emails of recipients to send export to
	'''
	assert isinstance(send_to, list)

	msg = MIMEMultipart()
	msg['From'] = send_from
	msg['To'] = COMMASPACE.join(send_to)
	msg['Date'] = formatdate(localtime=True)
	msg['Subject'] = subject

	msg.attach(MIMEText(text))

	for f in files or []:
		with open(f, "rb") as fil:
			part = MIMEApplication(
				fil.read(),
				Name=basename(f)
			)
		# After the file is closed
		part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
		msg.attach(part)


	smtp = smtplib.SMTP('andrew@bluewirepods.com', server)
	smtp.sendmail(send_from, send_to, msg.as_string())
	smtp.close()


if __name__ =="__main__":
	simplecast_data_collector()
	# export_path = [os.path.join('output', f) for f in os.listdir('output')]
	# send_export('andrew@bluewirepods.com',
	# 			['andrew@bluewirepods.com'],
	# 			'TEST PY', 'Testing our scheduler system...',
	# 			files=export_path, server="127.0.0.1")



