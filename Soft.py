import argparse
import datetime
import imutils
import time
import cv2
import numpy as np


peopleOnCarpet = 0
rez= open("rez.txt", "w")
rez.write("RA 62-2104 ,Marko Kljajic \n")
rez.write("file,count\n")

#Prolaz kroz sve video snimke
for i in range (1,11):
	camera = cv2.VideoCapture("video" +str(i) + ".mp4")
	peopleOnCarpet=0
	firstFrame = None

	while True:
        #uzimamo treutni frejm
		(grabbed, frame) = camera.read()

		if not grabbed:  # ako nije uspeo da uzme frejm, brejk posto je video gotov
			break

		frame = imutils.resize(frame, width=640)
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		gray = cv2.GaussianBlur(gray, (21,21 ), 0)  # odradim blurovanje da se smanji noise slike

		if firstFrame is None:
			firstFrame = gray
			continue

		#racunamo apsolutnu razliku izmedju prvog frejma i trenutnog frejma
		frameDelta = cv2.absdiff(firstFrame, gray)  # razlika izmedju prvog frejma i trenuntnog
		frameDelta = cv2.dilate(frameDelta, None, iterations=2)
		frameDelta = cv2.erode(frameDelta,None, iterations=2)

		thresh = cv2.threshold(frameDelta, 17, 255, cv2.THRESH_BINARY)[1] # prabaci u belu boju sve piksele koji imaju vrednost vecu od 17

		tepih= cv2.threshold(gray,30, 255, cv2.THRESH_BINARY)[1]
		tepih=cv2.bitwise_not(tepih) # prebacimo belu u crnu i obrnuto. Da bi dobili tepih.
		tepih=cv2.erode(tepih,None,iterations=1)


		thresh = cv2.erode(thresh, None, iterations=1)

		(_,cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)

		(_, cnts2, _) = cv2.findContours(tepih.copy(), cv2.RETR_EXTERNAL,
										cv2.CHAIN_APPROX_SIMPLE)
		for c2 in cnts2:
			if cv2.contourArea(c2) < 500 : # ako je kontura manja od 500, preskoci je. To odradimo da bi dobili tepih.
				continue

            #izracuna gde se nalazi kontura i posle je ogranicimo sa pravougaonikom i dodamo crvenu tackicu u sredinu
			(xt, yt, wt, ht) = cv2.boundingRect(c2)
			cv2.rectangle(frame, (xt, yt), (xt + wt, yt + ht), (0, 255, 0), 2)
			rectagleCenterPont = ((xt + xt + wt) / 2, (yt + yt + ht) / 2)
			cv2.circle(frame, rectagleCenterPont, 1, (0, 0, 255), 5)


		for c in cnts:
			if 500 < cv2.contourArea(c) < 50 :
				continue

			(x, y, w, h) = cv2.boundingRect(c)
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
			rectagleCenterPont = ((x + x + w) / 2, (y + y + h) / 2)
			cv2.circle(frame, rectagleCenterPont, 1, (0, 0, 255), 5)

			if yt<y<yt+2 :  #brojac ljudi na tepihu
				peopleOnCarpet+=1



			print peopleOnCarpet
        #Ispisi na glavnom videu broj ljudi na tepihu
		cv2.putText(frame, "Number of people: {}".format(str(peopleOnCarpet)), (10, 20),
			cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

		# Prikazi video snimke
		cv2.imshow("Security Feed", frame)
		cv2.imshow("Thresh", thresh)
		cv2.imshow("Frame Delta", frameDelta)
		cv2.imshow("tepih", tepih)

		key = cv2.waitKey(1) & 0xFF

		#ako se pritisne q da prekine trenutni video
		if key == ord("q"):
			break

	camera.release()
	cv2.destroyAllWindows()

	rez.write("video" + str(i) + ".mp4," + str(peopleOnCarpet) + "\n")

