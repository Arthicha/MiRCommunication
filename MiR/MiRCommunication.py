import requests
import json


class MIR: # MIR REST api

	def __init__(self, auth_=None, auth_file=None):
		"""
		constructor: setup connection/interface. In order to set up a connection an Authorization must be passed.
		Args:
			auth_ (str): The Authorization string.
			auth_file (str): The file where the Authorization is contained in a json format.
		"""

		if auth_file is None and auth_ is None:
			raise Exception("You have to pass either the Authorization or the json file that contains it.")

		self.host = 'http://mir.com/api/v2.0.0/'

		if auth_ is None:
			with open(auth_file) as f:
				res_dic = json.load(f)

				if "auth" in res_dic:
					auth_ = res_dic["auth"]
				else:
					raise Exception("The json has not the correct format")

		self.__todolist__ = [] # to do list (so that MiR mission queue has 1 mission in maximum)
		self.headers = {'Content-Type': 'application/json', 'Authorization': auth_}

		self.mission_tex_executing = "Waiting for obstacles to be removed."
		self.states = {10: "Emergency stop", 4: "Pause", 3: "Ready", 5: "Executing", 12: "Error"}
		self.position_type = {"L-marker entry position": 14, "L-marker": 13, "Robot position": 0}
		self.error_type = {""}
		print("MIR COMMUNICATION INITIALIZED")

	# -----------------------------------------------------------------------------------
	# mission queue 

	def start_mission_queue(self) -> None:
		"""
			Start the mission queue changing the state of the robot to Ready.
			"""
		self.change_state_id(3)

	def stop_mission_queue(self) -> None:
		"""
			Stop the mission queue changing the state of the robot to Pause.
			"""
		self.change_state_id(4)


	def mission_queue_add(self, mission_id) -> dict:
		"""
			Add a mission to the mission queue (not execute the mission)

			Args:
				mission_id (str): the mission ID to be put in the queue.
			"""

		dict_post = {"mission_id": mission_id, "priority": 0}
		return self.write('mission_queue', elements=dict_post)

	def todolist_add(self, mission_function, args=None):
		"""
			Add a mission function to the mission queue (not execute the mission)

			Args:
				mission_id (str): the mission ID to be put in the queue.
			"""

		self.__todolist__.append([mission_function,args])

	def handle(self):
		"""
			update function, do new task from todolist if previous mission is done
		"""
		if self.get_mission_history()[-1]['state'] in ['Done','Aborted']:
			if len(self.__todolist__) > 0:
				task = self.__todolist__.pop(0)
				missionid = task[0](task[1])
				self.mission_queue_add(missionid)
				return 1
			else:
				return 0
		else:
			return 1

	# -----------------------------------------------------------------------------------
	# robot navigation

	def move_to(self, point_name) -> (str):
		"""
			return a mission moving the robot to a predefined point

			Args:
				point_name (str): The name of the point to go.
		"""
		guid_point, _ = self.get_guid_point(point_name)
		return self.__create_mission('move',guid_point)

	def move_for(self, forward_distance) -> (str):
		"""
			return a mission for relative move

			Args:
				forward_distance (float): forward distance
		"""
		return self.__create_mission('relative move',forward_distance)

	def dock_to(self, point_name) -> (str):
		"""
			return a mission docking the robot to the L-marker

			Args:
				point_name (str): The name of the point to go.
		"""
		guid, _ = self.get_LMarker_point(point_name)
		return self.__create_mission('dock',guid)


	# -----------------------------------------------------------------------------------
	# audio control

	def scream(self, audio_name) -> (str):
		if audio_name == 'beep':
			mission = 'EiT: beep!'
		elif audio_name == 'start':
			mission = 'EiT: start'
		elif audio_name == 'end':
			mission = 'EiT: done!'

		return self.get_mission(mission)
	
	# -----------------------------------------------------------------------------------
	# sensory feedback

	def get_battery_status(self) -> str:
		"""
			Retrieve the battery percentage of the MiR.
			"""
		status = self.read('status')
		battery = status['battery_percentage']
		print(f"status: {status}")

		return battery

	# -----------------------------------------------------------------------------------
	# map and marker

	def get_LMarker_point(self, markerName, helper=False) -> (str, dict):
		"""
			Retrieve the LMarker's point or its helper id based on its name. It also returns the full data of this point.

			Args:
				markerName (str): The marker's name.
				helper (bool): Set to True if you want to access to its helper.
			"""

		points = self.get_predefined_positions()
		guid = ''
		full_point_data = {}

		for point in points:
			if point['name'] == markerName:
				if helper and point["type_id"] == self.position_type["L-marker entry position"]:
					guid = point['guid']
					full_point_data = point
					break
				elif not helper and point["type_id"] == self.position_type["L-marker"]:
					guid = point['guid']
					full_point_data = point
					break
			pass
		return guid, full_point_data

	def get_guid_point(self, point_name) -> (str, dict):
		"""
			Retrieve the point id based on its name. It also returns the full data of this point.

			Args:
				point_name (str): The point's name.
			"""

		points = self.get_predefined_positions()

		guid = ''
		full_point_data = {}

		for point in points:
			if point['name'] == point_name:
				guid = point['guid']
				full_point_data = point
				break
			pass
		return guid, full_point_data

	def get_predefined_positions(self) -> list:
		"""
			Retrieve the list of stored positions in the MiR robot.
			"""

		positions = self.read('positions')
		return positions

	# -----------------------------------------------------------------------------------
	# mission

	def get_predefined_missions(self) -> list:
		"""
			Retrieve the list of missions stored in MiR.
			"""
		return self.read('missions')

	def __create_mission(self, mission_type , parameter_value) -> (str):

		mission = ''
		if mission_type == 'move':
			mission = 'EiT: move'
			action_type = 'move'
			param_name = 'position'
		elif mission_type == 'dock':
			mission = 'EiT: dock'
			action_type = 'docking'
			param_name = 'marker'
		elif mission_type == 'relative move':
			mission = 'EiT: relative move'
			action_type = 'relative_move'
			param_name = 'x'

		guid_mission = self.get_mission(mission)
		actions = self.get_actions_mission(guid_mission)
		action_guid = ''
		for action in actions:
			if action["action_type"] == action_type:
				action_guid = action["guid"]
				break

		dict_helper = {"priority": 999, "parameters": [{"id": param_name,"value": parameter_value}]}
		self.put(f'missions/{guid_mission}/actions/{action_guid}', dict_helper)

		return guid_mission

	def get_mission(self, name) -> (str):
		"""
			Retrieve the mission ID and its information from MiR knowing its name. In case that
			the mission is not found, the guid and the dictionary will be empty.

			Args:
				name (str): The name of the saved mission in MiR.
			"""

		missions = self.get_predefined_missions()
		guid = ''
		full_mission_data = {}

		for mission in missions:
			if mission['name'] == name:
				guid = mission['guid']
				full_mission_data = mission
				break
			pass
		return guid

	def get_actions_mission(self, guid) -> list:
		"""
			Retrieve the list of actions that belong to the mission with the specified mission ID.

			Args:
				guid (str): The identification of the mission.
			"""

		return self.read(f'missions/{guid}/actions')


	# -----------------------------------------------------------------------------------
	# robot operational state
	
	def change_state_id(self, id_robot) -> None:
		"""
			Change the state id of the MiR robot.
			"""

		if not (id_robot in self.states):
			raise Exception("The id is not correct")

		dict_help = {"state_id": id_robot}
		self.put('status', dict_help)


	def get_mission_history(self) -> list:
		"""
			Retrieve the list of missions in the queue. Finished, failed, pending and executing missions.
			"""

		missions = self.read('mission_queue')
		return missions

	# -----------------------------------------------------------------------------------
	# read/write MiR register

	def read_register(self, i):
		data = self.read('registers/'+str(i))
		return data

	def write_register(self, i, value):
		jsondata = {"value": value}
		status = self.write('registers/'+str(i), elements=jsondata)
		return status

	# -----------------------------------------------------------------------------------
	# fundamental REST api: read (get), write (post), put

	def read(self, uri, elements=None, verbose=False):

		if elements is None:
			elements = {}

		received_mess = requests.get(self.host + uri, json=elements, headers=self.headers)
		response = {}

		code = self.__get_code__(received_mess)
		if verbose:
			print(f"Code: {code}")

		if code == 200 or len(elements) and code == 201:
			response = self.__transform_mess__(received_mess)

		return response

	def write(self, uri, elements=None, verbose=False):

		if elements is None:
			elements = {}

		received_mess = requests.post(self.host + uri, json=elements, headers=self.headers)
		response = {}

		code = self.__get_code__(received_mess)
		if verbose:
			print(f"Code: {code}")

		if code == 200 or len(elements) and code == 201:
			response = self.__transform_mess__(received_mess)

		return response

	def put(self, uri, elements, verbose=False):
		received_mess = requests.put(self.host + uri, json=elements, headers=self.headers)
		response = {}

		code = self.__get_code__(received_mess)
		if verbose:
			print(f"Code: {code}")

		if code == 200:
			response = self.__transform_mess__(received_mess)

		return response

	# -----------------------------------------------------------------------------------
	# static method for initialization

	@staticmethod
	def __transform_mess__(received_mess):
		text = received_mess.text
		return json.loads(text)

	@staticmethod
	def __get_code__(received_mess):
		return received_mess.status_code

