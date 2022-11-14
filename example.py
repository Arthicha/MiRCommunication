from MiR.MiRCommunication import MIR
"""
 an example program: move/doct to different predefined locations
"""

auth_file = "auth.json" # authorization file

if __name__ == "__main__":

	mir = MIR(auth_file=auth_file) # initialize MiR communication

	mir.stop_mission_queue() # pause the mission queue

	mir.todolist_add(mir.move_to,'Home')
	mir.todolist_add(mir.scream,'start')

	mir.todolist_add(mir.move_to,'Warehouse')
	mir.todolist_add(mir.scream,'beep')

	mir.todolist_add(mir.dock_to,'shelfA')
	mir.todolist_add(mir.move_for,-0.2)
	mir.todolist_add(mir.scream,'beep')

	mir.todolist_add(mir.move_to,'Warehouse')
	mir.todolist_add(mir.scream,'end')

	mir.start_mission_queue() # play the mission queue

	while(1):
		mir.handle()

	