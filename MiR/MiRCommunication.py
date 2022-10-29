from copy import deepcopy
import requests
import json


class MIR:
	""" Description of the actions/requests the user can send/receive from MiR robot.

	In order to establish a communication with MiR robot, a rest API needs to be programmed.
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
					raise Exception("The json have not the correct format")

		self.headers = {'Content-Type': 'application/json', 'Authorization': auth_}

	# -----------------------------------------------------------------------------------
	# read functions

	def get_positions(self):
		positions = self.read('positions')
		return positions

	def get_mission_queue(self):
		missions = self.read('mission_queue')
		print(missions)

	def get_battery_status(self):
		status = self.read('status')
		battery = status['battery_percentage']
		return battery

	def is_available(self,acceptance_radius=0.1):
		available = False
		status = self.read('status')

		distance = status['distance_to_next_target']
		v = status['velocity']['linear']
		w = status['velocity']['angular']

		if ((distance <= acceptance_radius) and (v == 0.0) and (w == 0.0)):
			available = True
		return available

	# -----------------------------------------------------------------------------------
	# read/write MiR register

	def read_register(self,i):
		data = self.read('registers/'+str(i))
		return data

	def write_register(self,i,value):
		jsondata = {"value": value}
		status = self.write('registers/'+str(i),elements=jsondata)
		return status

	# -----------------------------------------------------------------------------------
	# move MiR

	def set_target(self,station_idx,point=0):
		'''
		set MiR target
		input: 
				(1) station_idx (int) : station num 
				(2) point (int) : subpoint
		'''
		status = self.write_register(21,point)
		status = self.write_register(20,station_idx)
		return status


	# -----------------------------------------------------------------------------------
	# play audio

	def play_audio(self,audio_idx):
		status = self.write_register(19,audio_idx)
		return status

	# -----------------------------------------------------------------------------------

	def read(self,uri,elements='',verbose=False):
		received_mess = requests.get(self.host + uri, json=elements, headers=self.headers)
		response = {}

		code = self.__get_code__(received_mess)
		if verbose:
			print(f"Code: {code}")

		if code == 200 or len(elements) and code == 201:
			response = self.__transform_mess__(received_mess)

		return response

	def write(self,uri,elements='',verbose=False):
		received_mess = requests.post(self.host + uri, json=elements, headers=self.headers)
		response = {}

		code = self.__get_code__(received_mess)
		if verbose:
			print(f"Code: {code}")

		if code == 200 or len(elements) and code == 201:
			response = self.__transform_mess__(received_mess)

		return response



	@staticmethod
	def __transform_mess__(received_mess):
		text = received_mess.text
		return json.loads(text)

	@staticmethod
	def __get_code__(received_mess):
		return received_mess.status_code
