from errors import *

class ActionBase(object):
	def __init__(self, browser_driver, language):
		self.browser_driver = browser_driver
		self.language = language
		
	def is_element_visible(self, selector):
		is_visible = self.browser_driver.is_element_visible(selector)
		return is_visible
	
	def raise_action_failed_error(self, message):
		raise ActionFailedError(message)
	
	def assert_element_is_visible(self, selector, message):
		if not self.is_element_visible(selector):
			self.raise_action_failed_error(message)