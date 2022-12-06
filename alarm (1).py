
from threading import Thread

import playsound




class alarm:
    def sound_alarm(self, path):
        playsound.playsound(path)
    def detectAlarm(self):
        args = {'alarm': 'alarm.wav'}
        t = Thread(target=self.sound_alarm,args=(args["alarm"],))
        t.deamon = True
        t.start()



