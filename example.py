from MiR.MiRCommunication import MIR

auth_file = "auth.json" # authorization file

if __name__ == "__main__":

    mir = MIR(auth_file=auth_file) # initialize MiR communication

    mir.stop_mission_queue() # pause the mission queue

    mir.mission_queue_add(mir.scream('start')) # play audio "start"
    mir.mission_queue_add(mir.move_to('Home')) # move to "Home"

    mir.mission_queue_add(mir.dock_to('shelfA')) # perform precision docking at "shelfA"
    mir.mission_queue_add(mir.scream('beep')) # play audio "beep"

    mir.mission_queue_add(mir.move_to('Home')) # move to "Home"
    mir.mission_queue_add(mir.scream('end')) # play audio "end"

    mir.start_mission_queue() # play the mission queue
    