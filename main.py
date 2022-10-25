from MiR.MiRCommunication import MIR

auth_file = "auth.json"

if __name__ == "__main__":
    mir = MIR(auth_file=auth_file)
    mir.get_positions()
    battery, state = mir.get_status()
    print(battery, state)

