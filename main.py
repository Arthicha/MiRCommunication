from MiR.MiRCommunication import MIR
import time

auth_file = "auth.json"


target_idx = 0

if __name__ == "__main__":
	mir = MIR(auth_file=auth_file)

	print("battery: ", mir.get_battery_status())

	while(1):
		available = mir.is_available(acceptance_radius=0.2)
		
		if(available):
			mir.play_audio(1)
			time.sleep(3)
			mir.set_target(target_idx)
			print('set target at',target_idx)
			target_idx += 1
			if target_idx >= 3:
				target_idx = 1
			time.sleep(5)
		time.sleep(3)



