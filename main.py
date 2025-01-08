import mss
import cv2
import sys
import numpy as np
import time
import pydirectinput
import keyboard
import threading

#Outside pos: 960, 1100
#Close pos: 1200, 750
#Select pos: 458, 370
#Sell_1 pos: 960, 980
#Sell_2 pos: 1111, 850

class Fisher:
    def __init__(self):
         self.status = True
         self.fish_count = 0
         self.fish_limit = 6
         pass
    
    def stream(self):
        with mss.mss() as sct:
            img = sct.grab({"top": 925, "left": 650, "width": 618, "height": 20})
            img = np.array(img)
            return img
    def stream_all(self):
        with mss.mss() as sct:
            img_all = sct.grab({"top": 348, "left": 342, "width": 903, "height": 684})
            img_all = np.array(img_all)
            return img_all
    def buoy(self):
        img = self.stream()
        buoy = cv2.imread("D:/Code/Python/Auto-FishingTon-OpenCV/img/buoy.png", cv2.IMREAD_UNCHANGED)
        result = cv2.matchTemplate(buoy, img, cv2.TM_CCOEFF_NORMED)
        _, max_val_buoy, _, max_loc_buoy = cv2.minMaxLoc(result)
        return max_val_buoy, max_loc_buoy
    
    def exclamation(self):
        img_all = self.stream_all()
        exclamation = cv2.imread("D:/Code/Python/Auto-FishingTon-OpenCV/img/exclamation.png", cv2.IMREAD_UNCHANGED)
        result = cv2.matchTemplate(exclamation, img_all, cv2.TM_CCOEFF_NORMED)
        _, max_val_exclamation, _, max_loc_exclamation = cv2.minMaxLoc(result)
        return max_val_exclamation, max_loc_exclamation
    
    def close(self):
        img_all = self.stream_all()
        close = cv2.imread("D:/Code/Python/Auto-FishingTon-OpenCV/img/close.png", cv2.IMREAD_UNCHANGED)
        result = cv2.matchTemplate(close, img_all, cv2.TM_CCOEFF_NORMED)
        _, max_val_close, _, max_loc_close = cv2.minMaxLoc(result)
        return max_val_close, max_loc_close

    def sell(self):
        print("Go sell fish")
        pydirectinput.keyDown('w')
        time.sleep(5)
        pydirectinput.keyUp('w')
        pydirectinput.press('space')
        print("Selling")
        time.sleep(0.5)
        pydirectinput.leftClick(458, 370)
        time.sleep(0.5)
        pydirectinput.leftClick(960, 980)
        time.sleep(0.5)
        pydirectinput.leftClick(1111, 850)
        time.sleep(0.5)
        pydirectinput.leftClick(960, 1100)
        print("Selled")
        print("Go back")
        pydirectinput.keyDown('s')
        time.sleep(5)
        pydirectinput.keyUp('s')
        
    def fish(self):
        while self.status:
            img_all = self.stream_all()
            #Reset
            pydirectinput.leftClick(960, 1100)
            print("Number of fish: ", fisher.fish_count)
            time.sleep(0.5)
            #Throw
            pydirectinput.mouseDown()
            time.sleep(1.5)
            pydirectinput.mouseUp()
            print("Throwed")
            #Catch
            while self.status:
                max_val_exclamation, max_loc_exclamation = self.exclamation()
                if max_val_exclamation >= 0.8:
                    pydirectinput.leftClick()
                    print("Catch")
                    break
            start_time = time.time()
            while self.status:
                max_val_close, max_loc_close = self.close()
                if time.time() - start_time > 30:
                    break
                if max_val_close >= 0.8:
                    time.sleep(2)
                    pydirectinput.leftClick(1200, 750)
                    print("Catched")
                    self.fish_count += 1
                    break

            #Check limit
            if self.fish_count >= self.fish_limit:
                time.sleep(4)
                fisher.fish_count = 0
                self.sell()
            time.sleep(1)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                self.status = False
                cv2.destroyAllWindows()
                break
        
        

if __name__ == "__main__":
    print("Press 's' to start, 'q' to quit")
    keyboard.wait('s')

    fisher = Fisher()
    fishing = threading.Thread(target=fisher.fish)
    fishing.start()

    while fisher.status:
        img = fisher.stream()
        img_all = fisher.stream_all()
        max_val_buoy, max_loc_buoy = fisher.buoy()



        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        cv2.drawContours(img, contours, -1, (0, 255, 0), 2)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            area = cv2.contourArea(contour)
        
        if max_val_buoy >= 0.8:
            if area < 550:
                cv2.putText(img, "out", (0,15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                pydirectinput.mouseDown()
            if area > 3000:
                cv2.putText(img, "out", (0,15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                pydirectinput.mouseUp()
            else:
                cv2.putText(img, "in", (0,15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)



        small = cv2.resize(img, (0, 0), fx=1, fy=1)
        cv2.imshow("Computer Vision", small)
        cv2.setWindowProperty("Computer Vision", cv2.WND_PROP_TOPMOST, 1)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            fisher.status = False
            cv2.destroyAllWindows()
            break