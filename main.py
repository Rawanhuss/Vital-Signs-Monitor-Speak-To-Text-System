import websockets
import asyncio
import base64
import json
import requests
from requests.structures import CaseInsensitiveDict
import pyaudio
from heartrate_monitor import HeartRateMonitor
import time
import argparse
import smbus2
from mlx90614 import MLX90614
import hrcalc

auth_key = 'auth key for speach to text API ,from assembly ai'
headers = CaseInsensitiveDict()
headers["Content-Type"] = "application/json"
headers2 = {'x-api-key':'your API x-api-key'}
FRAMES_PER_BUFFER = 3200
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()
 
#----------------------------------------
#set reads from MAX30102 Sensor
parser = argparse.ArgumentParser(description="Read and print data from MAX30102")
parser.add_argument("-r", "--raw", action="store_true",
                    help="print raw data instead of calculation result")
parser.add_argument("-t", "--time", type=int, default=30,
                    help="duration in seconds to read from sensor, default 30")
args = parser.parse_args()

print('sensor starting...')
hrm = HeartRateMonitor(print_raw=args.raw, print_result=(not args.raw))
hrm.start_sensor()
bus = smbus2.SMBus(1)
tempsensor = MLX90614(bus, address=0x5A)
#----------------------------------------

# starts recording
stream = p.open(
	format=FORMAT,
	channels=CHANNELS,
	rate=RATE,
	input=True,
	frames_per_buffer=FRAMES_PER_BUFFER
)
 
# the AssemblyAI endpoint we're going to hit
URL = "url"
 
async def send_receive():

	print(f'Connecting websocket to url ${URL}')

	async with websockets.connect(
		URL,
		extra_headers=(("Authorization", auth_key),),
		ping_interval=5,
		ping_timeout=20
	) as _ws:

		await asyncio.sleep(0.1)
		print("Receiving SessionBegins ...")

		session_begins = await _ws.recv()
		print(session_begins)
		print("Sending messages ...")


		async def send():
			while True:
				try:
					data = stream.read(FRAMES_PER_BUFFER)
					data = base64.b64encode(data).decode("utf-8")
					json_data = json.dumps({"audio_data":str(data)})
					await _ws.send(json_data)

				except websockets.exceptions.ConnectionClosedError as e:
					print(e)
					assert e.code == 4008
					break

				except Exception as e:
					assert False, "Not a websocket 4008 error"

				await asyncio.sleep(0.01)
		  
			return True
	  

		async def receive():
			while True:
				try:
					maxLength = 3
					cmdList = []
					wakeWords =[]
					matches =[]
					#the system will listen for 3 words then check if it's a wake up word or not
					#wake up word in this project is "hey,SAK"
					while len(cmdList) < maxLength:
						result_str = await _ws.recv()
						if json.loads(result_str)['message_type'] == 'FinalTranscript':
							msg = json.loads(result_str)['text'] 
							cmdList.append(msg)
							print(cmdList)
					#check from the train file
					f = open("train.txt", "r")
					wakeWords = f.read().split('\n')
					print(wakeWords)
					matches = [x for x in cmdList if x in wakeWords]
					result_str = await _ws.recv()
					print("matches are :",matches)
					if len(matches) >= 1:
						#whenever there is a wake word has been detected the command will be send to the cloud
						print("wake wrord detected")
						payload ={
							"command": str(cmdList)
							}
						rv =requests.post('your API url',headers=headers ,json=payload)
					
					else:
						print("No wake words")
					print("Ambient Temperature :",tempsensor.get_amb_temp())
					print("Body Temperature :",tempsensor.get_obj_temp())
					print ("Bpm-------",hrm.bpm)
					bpm = hrm.bpm
					spo2 = hrm.spo2
					temperature = tempsensor.get_obj_temp()
					payload ={
                        "bpm": bpm,
                        "spo2": spo2,
                        "temperature": temperature
						}
					r = requests.post('your API url',headers=headers2 ,json=payload)
					print(r.text)
					time.sleep (10)	

				except websockets.exceptions.ConnectionClosedError as e:
					print(e)
					assert e.code == 4008
					break

				except Exception as e:
					assert False, "Not a websocket 4008 error"
	  
		send_result, receive_result = await asyncio.gather(send(), receive())

while True:
	asyncio.run(send_receive())
	
