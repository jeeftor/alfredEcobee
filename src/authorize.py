import sys
import requests
from workflow import Workflow3, web, notify
from workflow.background import run_in_background, is_running



APP_KEY = 'CC1mvejObvFwoAqPn8VfVe7OfTFaPDEp'

def main(wf):

	# Store APP_KEY for use by othe rparts of the code
	wf.store_data('APP_KEY', APP_KEY, serializer='json')
	
	auth_url = 'https://api.ecobee.com/authorize'
	params = dict(response_type='ecobeePin', client_id=APP_KEY, scope='smartWrite')

	r = web.get(auth_url,params)
	r.raise_for_status()
	
	code = r.json()['code']
	pin =  r.json()['ecobeePin']

	# Use the JSON serializer only for these data
	wf.store_data('pin', pin, serializer='json')
	wf.store_data('AUTH_CODE', code, serializer='json')

	wf.add_item('Authorization Pin: ' + pin, 'You must use this pin for authorization')

	# Start background listener:
	if not is_running('check_auth_code'):
		run_in_background('check_auth_code',
					  ['/usr/bin/python',
					   wf.workflowfile('src/bg_check_auth.py')])

		notify.notify('Starting bg task')
	else:
		notify.notify('Background task already started')

	wf.send_feedback()


if __name__ == u"__main__":
	wf = Workflow3()
	sys.exit(wf.run(main))

