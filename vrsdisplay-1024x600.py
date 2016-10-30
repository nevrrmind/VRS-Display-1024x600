# -*- coding: utf-8 -*-
import os
import pygame
import time
from threading import Thread
from datetime import datetime
import json
import sys
from itertools import cycle
import requests

#VRS-Frontend
station="" #Your Stationname
vrsurl="" #Enter your VRS-Url with "/" at the end!
login="on" #Change to "off" if your VRS is public.
username="" #Only needed if VRS-Login=on
password="" #Only needed if VRS-Login=on
querytime=5 #Server Querytime
#VRS-Backend
admin="on" #Only if the User above is an Admin
#Weather
display_weather="on" #Weather on ore off...
location="" #Weatherlocation "London,uk"
owm_key="" #Openweathermap-API-Key Get yours at http://home.openweathermap.org/users/sign_up
 
class dspl :
    screen = None;
    def __init__(self):
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print "I'm running under X display = {0}".format(disp_no)
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pygame.display.init()
            except pygame.error:
                print 'Driver: {0} failed.'.format(driver)
                continue
            found = True
            break
        if not found:
			raise Exception('No suitable video driver found!')

	size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
	print "VRS-Displaysize: %d x %d" % (size[0], size[1])
	self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
	self.screen.fill((0, 0, 0))
	pygame.font.init()
	pygame.display.update()
    def __del__(self):
		"Destructor to make sure pygame shuts down, etc."

def format_int(i, sep='.'):
	cyc = cycle(['', '', sep])
	s = str(i)
	last = len(s) - 1
	formatted = [(cyc.next() if idx != last else '') + char
		for idx, char in enumerate(reversed(s))]
	return ''.join(reversed(formatted))

vrsdspl = dspl()
font_vrs = pygame.font.Font("fonts/roboto.ttf", 26)
font_vrs_feeds = pygame.font.Font("fonts/roboto.ttf", 15)
font_weather = pygame.font.Font("fonts/roboto.ttf", 15)
font_sqkalarm = pygame.font.Font("fonts/roboto.ttf", 15)

def readvrs():
	while True:
		if login == "on":
			while True:
				try:
					vrs_response = requests.get(vrsurl+'AircraftList.json', auth=(username, password))
					flights = vrs_response.json()
					break
				except ValueError:
					vrsdspl.screen.blit(font_weather.render('Error! No AircraftList.json. Try again...Please wait', True, (0, 0, 0)), (500, 250))
					print "No AircraftList.json"
					time.sleep(5)
		else:
			while True:
				try:
					vrs_response = requests.get(vrsurl+'AircraftList.json')
					flights = vrs_response.json()
					break
				except ValueError:
					vrsdspl.screen.blit(font_weather.render('Error! No AircraftList.json. Try again...Please wait', True, (0, 0, 0)), (500, 250))
					print "No AircraftList.json"
					time.sleep(5)
		if admin == "on":
			while True:
				try:
					requests.get(vrsurl+'WebAdmin/Index.html', auth=(username, password))
					vrs_admin_response = requests.get(vrsurl+'WebAdmin/Index/GetState', auth=(username, password))
					admin_stuff = vrs_admin_response.json()
					break
				except ValueError:
					vrsdspl.screen.blit(font_weather.render('Error! No Admin-GUI. Try again...Please wait', True, (0, 0, 0)), (520, 250))
					print "No Admin-Gui"
					time.sleep(5)
			global feeds
			feeds=admin_stuff['Response']['Feeds']
		flieger=flights['acList']
		global sqkalarm
		sqkalarm=[{'Reg': k.get('Reg', 'unknown'), 'ICAO': k.get('Icao', 'unknown'), 'Squawk': k.get('Sqk', 'unknown')} for k in flieger if k['Sqk'] in sqkinfo.keys()]
		global flightscount
		flightscount=flights['totalAc']
		global milflights
		milflights=sum(1 for d in flieger if d.get('Mil') == 1)
		global mlatflights
		mlatflights=sum(1 for d in flieger if d.get('Mlat') == 1)
		global heliflights
		heliflights=sum(1 for d in flieger if d.get('Species') == 4)
		time.sleep(querytime)
t1 = Thread(target = readvrs)
t1.daemon = True

def weather():
	while True:
		weather_response = requests.get('http://api.openweathermap.org/data/2.5/weather?q={0}&appid={1}&units=metric'.format(location, owm_key))
		wetter = weather_response.json()
		global clouds
		clouds = wetter['clouds']['all']
		global weather_time
		weather_time = datetime.fromtimestamp(wetter['dt'])
		global windspeed
		windspeed = wetter['wind']['speed']*3.6
		global wind_deg
		wind_deg = wetter['wind']['deg']
		global temp
		temp = wetter['main']['temp']
		global wettericon
		wettericon = wetter['weather'][0]['icon']
		global compass
		if wind_deg > 11.25 and wind_deg < 33.75:
			compass = "NNE"
		elif wind_deg > 33.75 and wind_deg < 56.25:
			compass = "NE"
		elif wind_deg > 56.25 and wind_deg < 78.75:
			compass = "ENE"
		elif wind_deg > 78.75 and wind_deg < 101.25:
			compass = "E"
		elif wind_deg > 101.25 and wind_deg < 123.75:
			compass = "ESE"
		elif wind_deg > 123.75 and wind_deg < 146.25:
			compass = "SE"
		elif wind_deg > 146.25 and wind_deg < 168.75:
			compass = "SSE"
		elif wind_deg > 168.75 and wind_deg < 191.25:
			compass = "S"
		elif wind_deg > 191.25 and wind_deg < 213.75:
			compass = "SSW"
		elif wind_deg > 213.75 and wind_deg < 236.25:
			compass = "SW"
		elif wind_deg > 236.25 and wind_deg < 258.75:
			compass = "WSW"
		elif wind_deg > 258.75 and wind_deg < 281.25:
			compass = "W"
		elif wind_deg > 281.25 and wind_deg < 303.75:
			compass = "WNW"
		elif wind_deg > 303.75 and wind_deg < 326.25:
			compass = "NW"
		elif wind_deg > 326.25 and wind_deg < 348.75:
			compass = "NNW"
		elif wind_deg > 348.75 or wind_deg < 11.25:
			compass = "N"
		time.sleep(120)
t2 = Thread(target = weather)
t2.daemon = True	

def rundisplay():
	while True:
		if 'flightscount' in globals():
			start_line_top=5
			feed_rect_h=0
			msg_total=0
			pygame.mouse.set_visible(0)
			vrsdspl.screen.fill((194, 194, 194))
			pygame.draw.rect(vrsdspl.screen, (255, 255, 255), (4,4,504,240), 2)
			vrsdspl.screen.blit(font_vrs.render('Station: %s' %station , True, (0, 0, 0)), (10, 5))
			vrsdspl.screen.blit(font_vrs.render('%s' %time.strftime("%d.%b.%y") , True, (0, 0, 0)), (10, 30))
			vrsdspl.screen.blit(font_vrs.render('%s' %datetime.now().strftime("%H:%M:%S") , True, (0, 0, 0)), (10, 60))
			vrsdspl.screen.blit(font_vrs.render('Aircraft: %s' %flightscount , True, (0, 0, 0)), (10, 90))
			vrsdspl.screen.blit(font_vrs.render('Military: %s' %milflights , True, (0, 0, 0)), (10, 120))
			vrsdspl.screen.blit(font_vrs.render('Multilateration: %s' %mlatflights , True, (0, 0, 0)), (10, 150))
			vrsdspl.screen.blit(font_vrs.render('Helicopter: %s' %heliflights , True, (0, 0, 0)), (10, 180))
			vrsdspl.screen.blit(font_vrs.render('Querytime: %ss' %querytime , True, (0, 0, 0)), (10, 210))
			vrsdspl.screen.blit(pygame.image.load('images/vrs2.png'), (250, 40))
			if display_weather=="on":
				pygame.draw.rect(vrsdspl.screen, (255, 255, 255), (4,248,250,200), 2)
				vrsdspl.screen.blit(font_weather.render('Weather in %s' %location , True, (0, 0, 0)), (10, 250))
				vrsdspl.screen.blit(font_weather.render('@ %s' %weather_time , True, (0, 0, 0)), (10, 265))
				vrsdspl.screen.blit(font_weather.render('Cloud coverage: %s%%' %clouds , True, (0, 0, 0)), (10, 280))
				vrsdspl.screen.blit(font_weather.render('Temp: %s °C' %temp , True, (0, 0, 0)), (10, 295))
				vrsdspl.screen.blit(pygame.image.load('images/icons/%s.png' %wettericon), (180, 250))
				vrsdspl.screen.blit(font_weather.render('Wind: %s km/h from %s' %(windspeed, compass) , True, (0, 0, 0)), (10, 315))
				vrsdspl.screen.blit(pygame.image.load('images/compass/%s.png' %compass), (10, 345))
			if admin=="on":
				#start_line_top=5
				#feed_rect_h=0
				#msg_total=0
				for k in feeds:
					if k['Merged']==0:
						name=k['Name'][:12] + (k['Name'][12:] and '..')
						status=k['ConnDesc']
						status_code=k['Connection']
						tracked=k['Tracked']
						id=k['Id']
						msg_total+=k['Msgs']
						vrsdspl.screen.blit(font_vrs_feeds.render('%s' %name , True, (0, 0, 0)), (513, start_line_top))
						vrsdspl.screen.blit(font_vrs_feeds.render('%s' %id , True, (0, 0, 0)), (630, start_line_top))
						vrsdspl.screen.blit(pygame.image.load('images/status/%s.png' %status_code), (650, start_line_top))
						if tracked == 0:
							vrsdspl.screen.blit(font_vrs_feeds.render('Tracking: %s NO Traffic!!!' %tracked, True, (255, 0, 0),(255, 255, 0)), (740, start_line_top))
						else:
							vrsdspl.screen.blit(font_vrs_feeds.render('Tracking: %s' %tracked , True, (0, 0, 0)), (740, start_line_top))
						start_line_top+=15
						feed_rect_h+=16
				vrsdspl.screen.blit(font_vrs.render('Msgs: %s' %format_int(msg_total) , True, (0, 0, 0)), (200, 210))
				pygame.draw.rect(vrsdspl.screen, (255, 255, 255), (510,4,510,feed_rect_h), 2)
			sqkalarm_top=16+start_line_top
			for k in sqkalarm:
				if k['Squawk'] in warnlist:
					vrsdspl.screen.blit(font_sqkalarm.render('Reg:%s ICAO:%s Squawk:%s Trans: %s' %(k['Reg'], k['ICAO'], k['Squawk'], sqkinfo[(k['Squawk'])].decode('utf-8')) , True, (255, 0, 0)), (510, sqkalarm_top))
					sqkalarm_top+=16
				else:
					vrsdspl.screen.blit(font_sqkalarm.render('Reg:%s ICAO:%s Squawk:%s Trans: %s' %(k['Reg'], k['ICAO'], k['Squawk'], sqkinfo[(k['Squawk'])].decode('utf-8')) , True, (0, 0, 0)), (510, sqkalarm_top))
					sqkalarm_top+=16
			pygame.display.update()
			time.sleep(0.2)
		else:
			pygame.mouse.set_visible(0)
			vrsdspl.screen.fill((255, 255, 255))
			pygame.display.update()
			path="images/loading/"
			loadgif = ((path + "loading{0}.jpg".format(i)) for i in range(1,62))
			for loading in loadgif:
				vrsdspl.screen.blit(pygame.image.load(loading), (0, 0))
				pygame.display.update()
				time.sleep(0.05)

t3 = Thread(target = rundisplay)
t3.daemon = True

t1.start()
if display_weather=="on":
	t2.start()
t3.start()

raw_input ("Hit enter to quit VRS-Display: ")
exit()
