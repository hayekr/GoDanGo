#!/usr/bin/env python
############################################################################################                                                                
#      EDITED BY DADILETTA   : http://lancertechga.org
# This script uses a ultrasonic sensor scan to identify a path forward
############################################################################################
#
# Reference GoPiGo commands at: http://www.dexterindustries.com/GoPiGo/programming/python-programming-for-the-raspberry-pi-gopigo/
# ! Attach Ultrasonic sensor to A1 Port.
#
############################################################################################
from gopigo import *
import sys  #Used to get input from user via console
from time import sleep #needed for the pause commands
from collections import Counter  #do I even need this?
import math  #Do I need this?

sweep = [None] * 160  #the list to hold scanning data
cornerdistance = 10  #used to check the corners for nearby collisions
fardistance = 90  #distance used when plotting a clear direction... longer so we're planning farther ahead

def quickcheck():
	enable_servo()
	servo(70)  #check the right edge of our forward path
	time.sleep(.2) #pause so the sensor reading is more accurate
	check1 = us_dist(15) #first check
	servo(80)  #check dead ahead
	time.sleep(.1)
	check2 = us_dist(15)
	servo(90) #check the left edge of our forward path
	time.sleep(.1)
	check3 = us_dist(15)
	if check1 > fardistance and check2 > fardistance and check3 > fardistance:
		print "Quick check looks good."
		disable_servo()
		return True
	else:
		print "Quick check failed. [70|",check1,"cm.][80|",check2,"cm.][90|",check3,"cm.]" 
		disable_servo()
		return False

def crashcheck(counter):
	if counter % 10 == 0:
		servo(140)
		time.sleep(.4)
		if us_dist(15) < cornerdistance:
			return False
	elif counter % 5 == 0:  #this will be every 10, since the first if will take the 10's
		servo(20)
		time.sleep(.4)
		if us_dist(15) < cornerdistance:
			return False
	servo(80)
	time.sleep(.1)
	if us_dist(15) < fardistance:
		return False
	else:
		return True

def scan():
	time.sleep(1)
	while stop() == 0:  #bot sometimes doesn't stop, so I loop the command until it returns a 1 for completed
		print "Having trouble stopping"
		time.sleep(.5)
	allclear = True #we use this to save the return and still complete the whole scan
	if not quickcheck():
		print "Starting a full scan."
		for ang in range(10, 160, 2): #wide scan, skipping all the odd numbers to move quicker
			servo(ang)  #move the servo to the angle in the loop
			time.sleep(.07) #pause between scans seems to get better results (has to be before the sensor is activated)
			sweep[ang] = us_dist(15) #note the distance at each angle
			print "[Angle:", ang, "--", sweep[ang], "cm]"
			if sweep[ang] < fardistance and ang > 65 and ang < 95: #if we detect any obstacle in the direct path ahead
				allclear = False
	servo(80)
	disable_servo()
	return allclear

def turnto(ang):   #first calculate whether to use a low/med/high turn, then execute the turn
	time.sleep(1)
	set_left_speed(180)  #adjust these so your GoPiGo cruises straight
	set_right_speed(180) #adjust these so your GoPiGo cruises straight
	while stop() == None:  #stop loop to prepare for turn
			print "Having trouble stopping"
	diff = 80 - (ang-10)  #for some reason, 80 degrees is straight ahead with my servo. I take off 10 from ang to find the center of the window
	turnnum = 5  #reset the turn num to default value
	turntime = .14 #since the enc_tgt is unreliable, I'm using this turntime as a redundancy
	if abs(diff) > 30 and abs(diff) <= 60: #greater than 30 degrees, we should increase the amount needed to turn
		turnnum = 10
		turntime = .30
		print "Setting turn variable to 10. Turn time to .28"
	elif abs(diff) > 60:
		turnnum = 15
		turntime = .50
		print "Setting turn variable to 15. Turn time to .4"
	else:
		print "Setting turn variable to 5. Turn time to .14"
	if diff >= 0:
		enc_tgt(1,0,turnnum)
		while right() == None:
			print "Having trouble turning"
	else:
		enc_tgt(0,1,turnnum) 
		while left() == None:
			print "Having trouble turning"
	time.sleep(turntime)  #if the encoder fails, this sleep should vary the turn accordingly
	while stop() == None:
		print "Having trouble stopping"

def voltcheck():  #this check runs at the top of the main while loop
	if volt() < 6:
		print "Not enough power"
		return False
	elif volt() > 12:
		print "Spike in voltage!"
		return False
	else:
		print "Power is", volt(), "V"
		return True

def turnaround():
	disable_servo()
	time.sleep(1)
	set_left_speed(180)  #adjust these so your GoPiGo cruises straight
	set_right_speed(180) #adjust these so your GoPiGo cruises straight
	while stop() == None:
		print "Having trouble stopping"
	print "Backing up. Beep beep beep."
	while bwd() == None:
		print "Having trouble backing up"
	time.sleep(.8)  #TODO: Replace sleeps with enc_tgt. Was having trouble with it.
	while stop() == None:
		print "Having trouble stopping"
	while right_rot() == None:
		print "Having trouble spinning right."
	time.sleep(.8)
	while stop() == None:
		print "Having trouble stopping"

def letsroll():
	stopcount = 0 #avoids false stops by having to detect an obstacle multiple times
	counter = 0 #used for crashcheck, so we only check for corners every 5 counts
	print "Let's roll."   #always good to print messages so you can debug easier
	while True:
		set_left_speed(50)  #adjust these so your GoPiGo cruises straight
		set_right_speed(65) #adjust these so your GoPiGo cruises straight
		fwd()
		counter += 1
		if not crashcheck(counter):	#If the object is closer than the "distance_to_stop" distance, stop the GoPiGo
			stopcount += 1
			print "Is that something in my way?"
		if stopcount > 2:
			print "Yup. Something's in my way."
			while stop() == None:
				print "Having trouble stopping"
			break #stop the fwd loop

################################
################################

def casualScan():
    while stop() == 0:  #bot sometimes doesn't stop, so I loop the command until it returns a 1 for completed
        print "Having trouble stopping"
        time.sleep(.5)
    for ang in range(10, 160, 2): #wide scan, skipping all the odd numbers to move quicker
        servo(ang)  #move the servo to the angle in the loop
        time.sleep(.1) #pause between scans seems to get better results (has to be before the sensor is activated)
        sweep[ang] = us_dist(15) #note the distance at each angle
        print "[Angle:", ang, "--", sweep[ang], "cm]"
        if sweep[ang] < 20:
            time.sleep(.5)
            sweep[ang] = us_dist(15) #let's confirm
            if sweep[ang] < 20:
                break

def twitch():
    led_on(LED_R)
    led_on(LED_L)
    set_right_speed(10)
    set_left_speed(10)
    bwd()
    time.sleep(.1)
    while stop() == 0:  #bot sometimes doesn't stop, so I loop the command until it returns a 1 for completed
        print "Having trouble stopping"
        time.sleep(.5)
    servo(30)
    servo(110)
    led_off(LED_R)
    led_off(LED_L)




################################
#HERE'S WHERE THE PROGRAM STARTS
################################

while True:
    casualScan()
    twitch()


