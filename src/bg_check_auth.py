import sys
from workflow import Workflow3, web, notify
import time


def main(wf):
    AUTH_CODE = wf.stored_data('AUTH_CODE')
    APP_KEY = wf.stored_data('APP_KEY')

    log.info('AUTH_CODE: ' + AUTH_CODE)
    log.info('APP_KEY:   ' + APP_KEY)

    start_time = time.time()
    elapsed_time = 0

    token_url = 'https://api.ecobee.com/token'
    params = dict(grant_type='ecobeePin', code=AUTH_CODE, client_id=APP_KEY)

    log.debug('Making query to {} with params {}'.format(token_url, params))
    code = 401

    log.info('Starting Loop')
    # Run timer for 10 mins
    while (elapsed_time < 10 * 60) and code != 200:
        time.sleep(5)

        log.info('Elapsed time {}'.format(elapsed_time))

        # Calculate elapsed time in seconds
        elapsed_time = int(time.time() - start_time)

        # Make request
        r = web.post(token_url, params)
        # Extract status code
        code = r.status_code
        
        log.info(token_url)
        log.info(params)
        log.info(r.status_code)
        

    if code == 200:
        log.info('Auth success')
        notify.notify('SUCCESS', 'Ecobee plugin authorization complete')

        wf.store_data('ACCESS_TOKEN', r.json()['access_token'])
        wf.store_data('REFRESH_TOKEN', r.json()['refresh_token'])

    else:
        log.debug('Auth timeout')
        notify.notify('Ecobee authorization: FAILED','The authorization task has timed out')
    

    log.info('Terminating background process')

if __name__ == u"__main__":
    wf = Workflow3()
    log = wf.logger
    log.info('BG Auth Check Started')
    sys.exit(wf.run(main))
