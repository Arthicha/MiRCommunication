import requests
import json


class MIR:
    """ Description of the actions/requests the user can send/receive from MiR robot.

    In order to establish a communication with MiR robot, a rest API needs to be programmed.
    Therefore, this class is programmed to hold this communication in order to do
    the actions that will be useful for us during the project.

    """
    def __init__(self, auth_=None, auth_file=None):

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

    def get_positions(self):
        positions = self.send_receive_data('positions')
        print(positions)

    def get_mission_queue(self):
        missions = self.send_receive_data('mission_queue')
        print(missions)

    def get_status(self):
        status = self.send_receive_data('status')
        battery = status['battery_percentage']
        state = status['state_text']

        return battery, state

    def send_receive_data(self, uri, elements=''):
        received_mess = requests.get(self.host + uri, json=elements, headers=self.headers)
        response = {}

        code = self.__get_code__(received_mess)
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
