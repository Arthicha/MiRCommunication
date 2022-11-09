import requests
import json


class MIR:
	""" Description of the actions/requests the user can send/receive from MiR robot.

	In order to establish a communication with MiR robot, a REST (REpresentational State Transfer) API  needs to be
	programmed.
	Therefore, this class is programmed to hold this communication in order to do
	the actions that will be useful for us during the project.
	"""

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

		self.headers = {'Content-Type': 'application/json', 'Authorization': auth_}

		self.mission_tex_executing = "Waiting for obstacles to be removed."
		self.states = {10: "Emergency stop", 4: "Pause", 3: "Ready", 5: "Executing", 12: "Error"}
		self.position_type = {"L-marker entry position": 14, "L-marker": 13, "Robot position": 0}
		self.error_type = {""}

	# -----------------------------------------------------------------------------------
	# mission

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

	def get_actions_mission(self, guid) -> list:
		"""
			Retrieve the list of actions that belong to the mission with the specified mission ID.

			Args:
				guid (str): The identification of the mission.
			"""

		return self.read(f'missions/{guid}/actions')

	def get_mission_queue(self) -> list:
		"""
			Retrieve the list of missions in the queue. Finished, failed, pending and executing missions.
			"""

		missions = self.read('mission_queue')
		return missions

	def get_guid_mission(self, name) -> (str, dict):
		"""
			Retrieve the mission ID and its information from MiR knowing its name. In case that
			the mission is not found, the guid and the dictionary will be empty.

			Args:
				name (str): The name of the saved mission in MiR.
			"""

		missions = self.get_missions()
		guid = ''
		full_mission_data = {}

		for mission in missions:
			if mission['name'] == name:
				guid = mission['guid']
				full_mission_data = mission
				break
			pass

		return guid, full_mission_data

	def post_simple_mission_queue(self, mission_id) -> dict:
		"""
			Add a new mission to the mission queue. The mission will always go to the end of the queue.
			This mission should not contain required arguments.

			Args:
				mission_id (str): the mission ID to be put in the queue.
			"""

		dict_post = {"mission_id": mission_id, "priority": 0}
		return self.write('mission_queue', elements=dict_post)

	def get_missions(self) -> list:
		"""
			Retrieve the list of missions stored in MiR.
			"""

		return self.read('missions')

	# -----------------------------------------------------------------------------------
	# robot navigation control

	def move_to_LMarker(self, point_name, move_mission_name, helper=False) -> (str, str):
		"""
			The function move the robot to a LMarker position. In order to do so, a mission's action is modified to move
			to a specific point. The helper can be accessed as well.

			It retrieves the mission id, and the point id.

			Args:
				point_name (str): The name of the point to go.
				move_mission_name (str): The name of the mission to modify.
				helper (bool): Set true if you want
			"""

		guid_point, _ = self.get_LMarker_point(point_name, helper)
		return self.__move_robot_to_guid_point__(guid_point, move_mission_name)

	def move_to_point(self, point_name, move_mission_name) -> (str, str):
		"""
			The function move the robot to a position. In order to do so, a mission's action is modified to move
			to a specific point.

			It retrieves the mission id, and the point id.

			Args:
				point_name (str): The name of the point to go.
				move_mission_name (str): The name of the mission to modify.
			"""

		guid_point, _ = self.get_guid_point(point_name)
		return self.__move_robot_to_guid_point__(guid_point, move_mission_name)

	def __move_robot_to_guid_point__(self, guid_point, move_mission_name) -> (str, str):

		guid_mission, _ = self.get_guid_mission(move_mission_name)
		actions = self.get_actions_mission(guid_mission)

		action_guid = ''

		for action in actions:
			if action["action_type"] == "move":
				action_guid = action["guid"]
				break

		dict_helper = {
			"priority": 999, "parameters": [
				{
					"id": "position",
					"value": guid_point
				}
			]
		}

		print(action_guid)
		self.put(f'missions/{guid_mission}/actions/{action_guid}', dict_helper)

		return guid_mission, guid_point

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

		points = self.get_positions()
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

		points = self.get_positions()
		guid = ''
		full_point_data = {}

		for point in points:
			if point['name'] == point_name:
				guid = point['guid']
				full_point_data = point
				break
			pass

		return guid, full_point_data

	def get_positions(self) -> list:
		"""
			Retrieve the list of stored positions in the MiR robot.
			"""

		positions = self.read('positions')
		return positions

	# -----------------------------------------------------------------------------------
	# robot state
	
	def change_state_id(self, id_robot) -> None:
		"""
			Change the state id of the MiR robot.
			"""

		if not (id_robot in self.states):
			raise Exception("The id is not correct")

		dict_help = {"state_id": id_robot}
		self.put('status', dict_help)

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

