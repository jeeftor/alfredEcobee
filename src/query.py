import sys
from workflow import Workflow3, web, notify

from ecobee import Ecobee3



wf = Workflow3()
APP_KEY = wf.stored_data('APP_KEY')


e = Ecobee3()
