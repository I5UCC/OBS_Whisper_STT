import obsws_python as obs
import logging
import time

logging.basicConfig(level=logging.DEBUG)

cl = obs.ReqClient(host='localhost', port=4455, password='secret')

cl.set_input_settings('STT', {'text': 'testtext'}, True)
time.sleep(3)
cl.set_input_settings('STT', {'text': '123456'}, True)
time.sleep(3)
cl.set_input_settings('STT', {'text': '7891011'}, True)
time.sleep(3)
cl.set_input_settings('STT', {'text': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.'}, True)