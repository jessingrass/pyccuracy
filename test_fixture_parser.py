from locator import *
from test_fixture import *
import re

class test_fixture_parser:
	def __init__(self, browser_driver, language):
		self.language = language
		self.story_lines = (language["as_a"], language["i_want_to"], language["so_that"],)
		self.scenario_starter_lines = (language["scenario"],)
		self.scenario_lines = (language["given"], language["when"], language["then"],)
		self.browser_driver = browser_driver
		
	#helper methods for defining special cases
	def __is_story_line(self, line):
		return self.__is_special_item(line, self.story_lines)
	
	def __is_scenario_starter_line(self, line):
		return self.__is_special_item(line, self.scenario_starter_lines)
	
	def __is_scenario_line(self, line):
		return self.__is_special_item(line, self.scenario_lines)
		
	def __is_special_item(self, line, collection):
		for item in collection:
			if line.startswith(item):
				return 1
		return 0
		
	def get_fixture(self, files):
		fixture = test_fixture(self.language)
		for file_path in files:
			self.__process_file(fixture, file_path)
		return fixture
	
	def __process_file(self, fixture, file_path):
		try:
			fsock = open(file_path)
			lines = fsock.readlines()
			fsock.close()
		except IoError:
			fixture.add_invalid_test_file(file_path)
		
		self.__process_lines(fixture, file_path, [line.strip() for line in lines if line.strip()])
			
	def __process_lines(self, fixture, file_path, lines):
		if not self.__is_story_line(lines[0]) and not self.__is_story_line(lines[1]) and not self.__is_story_line(lines[2]): 
			fixture.add_no_story_definition(file_path)
		else:
			current_story = self.__process_story_lines(fixture, lines[0], lines[1], lines[2])
			for line in lines:
				if (self.__is_story_line(line)): pass
				elif (self.__is_scenario_starter_line(line)): current_scenario = self.__process_scenario_starter_line(fixture, current_story, line)
				elif (self.__is_scenario_line(line)): action_under = self.__process_given_when_then_line(line)
				else: self.__process_action_line(fixture, current_scenario, action_under, line)
	
	def __process_story_lines(self, fixture, as_a, i_want_to, so_that):
		return fixture.start_story(as_a.replace(self.story_lines[0],""), 
								   i_want_to.replace(self.story_lines[1],""), 
								   so_that.replace(self.story_lines[2],""))
	
	def __process_scenario_starter_line(self, fixture, current_story, line):
		reg = self.language["scenario_starter_regex"]
		match = reg.search(line)
		values = match.groups()
		scenario_index = values[0]
		scenario_title = values[1]
		current_scenario = current_story.start_scenario(scenario_index, scenario_title)
		return current_scenario
		
	def __process_given_when_then_line(self, line):
		if (line == self.language["given"]): return "given"
		if (line == self.language["when"]): return "when"
		if (line == self.language["then"]): return "then"
	
	def __process_action_line(self, fixture, current_scenario, action_under, line):
		method = getattr(current_scenario, "add_" + action_under)
		action = self.__get_action(line)
		method(line, action[0], action[1])

	def __get_action(self, line):
		if not hasattr(self, "all_actions"): self.all_actions = self.__get_actions()
		
		for action in self.all_actions:
			act = action(self.browser_driver, self.language)
			if act.matches(line):
				return (act.execute, act.values_for(line))
	
	def __get_actions(self):
		all_actions = []
		for action_name in locate("*_action.py"):
			action_module_name = os.path.splitext(os.path.split(action_name)[-1])[0]
			action_package = __import__("actions." + action_module_name)
			action_module = getattr(action_package, action_module_name)
			action = getattr(action_module, action_module_name)
			all_actions.append(action)
		return all_actions