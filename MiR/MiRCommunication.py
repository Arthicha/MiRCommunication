import requests
import json


class MIR:
	""" Description of the actions/requests the user can send/receive from MiR robot.

	In order to establish a communication with MiR robot, a REST (REpresentational State Transfer) API  needs to be programmed.
	Therefore, this class is programmed to hold this communication in order to do
	the actions that will be useful for us during the project.
	"""

	def __init__(self, auth_=None, auth_file=None):
		"""
		constructor: setup connection/interface
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

	def start_mission_queue(self):
		self.change_state_id(3)

	def stop_mission_queue(self):
		self.change_state_id(4)

	def get_actions_mission(self, guid):
		return self.read(f'missions/{guid}/actions')

	def get_mission_queue(self):
		missions = self.read('mission_queue')
		print(missions)

	def get_guid_mission(self, name):
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

	def post_simple_mission_queue(self, mission_id):
		dict_post = {"mission_id": mission_id, "priority": 0}
		return self.write('mission_queue', elements=dict_post)

	def get_missions(self):
		return self.read('missions')

	# -----------------------------------------------------------------------------------
	# robot navigation control

	def move_to_LMarker(self, point_name, move_mission_name, helper=False):
		guid_point, _ = self.get_LMarker_point(point_name, helper)
		return self.__move_robot_to_guid_point__(guid_point, move_mission_name)

	def move_to_point(self, point_name, move_mission_name):
		guid_point, _ = self.get_guid_point(point_name)
		return self.__move_robot_to_guid_point__(guid_point, move_mission_name)

	def __move_robot_to_guid_point__(self, guid_point, move_mission_name):
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
	
	def get_positions(self):
		positions = self.read('positions')
		return positions

	def get_battery_status(self):
		status = self.read('status')
		battery = status['battery_percentage']
		print(f"status: {status}")

		return battery

	# -----------------------------------------------------------------------------------
	# map and marker

	def get_LMarker_point(self, markerName, helper=False):
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

	def get_guid_point(self, point_name):
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

	# -----------------------------------------------------------------------------------
	# robot state
	
	def change_state_id(self, id_robot):
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

