from MiR.MiRCommunication import MIR
import time

auth_file = "auth.json"

target_idx = 0

if __name__ == "__main__":
    mir = MIR(auth_file=auth_file)

    # print("battery: ", mir.get_battery_status())
    # mir.get_mission_queue()
    # guid, full_data = mir.get_guid_mission('EiT: simple testing mission')
    # guid, full_data = mir.get_guid_mission('EiT: move2')
    # guid, _ = mir.move_to_point('StationA_1', 'EiT: move2')
    guid, _ = mir.move_to_point('Home', 'EiT: move2')
    # guid, _ = mir.move_to_point('shelfA', 'EiT: move2')
    print(guid)
    mir.post_simple_mission_queue(guid)
    mir.start_mission_queue()
    # # mir.get_mission_definition(guid)
    # # print(full_data)
    # mir.stop_mission_queue()
    # print(mir.get_positions())

# while 1:
# 	available = mir.is_available(acceptance_radius=0.2)
#
# 	if available:
# 		mir.play_audio(1)
# 		# time.sleep(3)
# 		print('set target at', target_idx)
# 		mir.set_target(target_idx)
#
# 		target_idx += 1
# 		if target_idx >= 3:
# 			target_idx = 1
#
# 		mir.is_available(acceptance_radius=0.2)
#
# 		# i = 0
# 		# while i < 5:
# 		# 	mir.get_battery_status()
# 		# 	time.sleep(1)
#
# 		# time.sleep(5)
# 	time.sleep(3)
