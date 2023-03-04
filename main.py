import pandas as pd
from serpapi import GoogleSearch
from PIL import Image
import urllib.request
import csv
import cv2
import signal
import requests
import pandas

import os

LINKBLACKLISTS = ["pisces", "365dm"] #If the program times out on a link, add that link to the blacklist
print("This application is in beta, some prompts may not work properly.")



ListOfUsedNames = []



def GetData():
    KeepRunning = "Yes"
    while True:
        art = input("Please write the name of the subject you would like images of.")
        ListOfUsedNames.append(art)                    #saves the subject name for making the csv file
        if os.path.exists(art) == True:
            print("Folder already exists, A csv file will be made from the files in this folder")
            KeepRunning = input("Would you like to Enter another name?").lower()
            if KeepRunning != "yes":
                break
        else:
            os.mkdir(art)
            params = {                                      #These paramaters will download around 50 images
                "q": art,                                   #Go to serpapi's website to see how more can be downloaded
                "tbm": "isch",
                "ijn": "0",
                "api_key": ""                                  #Put API-Key here
                     }
            search = GoogleSearch(params)
            results = search.get_dict()
            image_results = results["images_results"]         #Only take the image results and save the links in results
            links = []
        # addup = 0
        # for link in image_results:
        #     addup += 1
            runtimes = 0
            for link in image_results:
                links.append(link['original']) #'Link' does not provide the ability to download
                runtimes += 1
                print(runtimes)
            DownloadLinks(links, art, LINKBLACKLISTS)
            KeepRunning = input("Would you like to Enter another name?").lower()
            if KeepRunning != "yes":
                break
            print(KeepRunning)

def GetCornerColers(width, height, pix):
    exportLists = []
    topRight = pix[width, height]
    topLeft = pix[-width, height]
    bottumRight = pix[width, -height]
    bottumLeft = pix[-width, -height]
    center = (pix[0, 0])
    exportLists.append(topRight, topLeft, bottumRight, bottumLeft, center)
    return exportLists

def GetRGBPixel(im, width, height):
    rgb_im = im.convert('RGB')
    r, g, b = rgb_im.getpixel((width/1.5, height/1.5))
    return r, g, b

def DownloadLinks(Links, art, BlackList):
    IsFound = False
    runInt = 0
    saveOriginalWorkSpace = os.getcwd()
    os.chdir(art)
    print("If the program is stuck on a link, put the link in the LINKBLACKLISTS array in the code")
    input("press any button to continue")
    for link in Links:
        imgURL = link
        handle = imgURL[-4:]
        IsFound = CheckBlackList(link, BlackList)        #Compares links to links listed on the blacklist
        if (handle == ".png") or (handle == ".jpg"):
           print(link)
           if IsFound != True:
              try:               #If an error is gotten, ignore it
                print("trying")
                urllib.request.urlretrieve(imgURL, f"{art}{runInt}{handle}")
                print("finished")
              except Exception:
                print("Falty Link, skipping will be attempted")
                pass
           runInt = runInt + 1
    os.chdir(saveOriginalWorkSpace)

def CheckIfListBlack(link, list):
    linkChecker = ''
    nameChecker = ''
    charNum =0
    nameLength = 0
    softRunner = 0
    fromZero = 0
    for name in list:
        for letter in name:
            nameLength += 1
        while linkChecker != '\n':
            linkChecker = link[charNum]
            if name[0] == linkChecker:
                while linkChecker != nameChecker:
                    softRunner = charNum
                    linkChecker = link[softRunner]
                    nameChecker = name[fromZero]
                    fromZero += 1
                    if fromZero > nameLength:
                        return True
            charNum += 1
        return False




def GetRGB(imageName):
    im = Image.open(imageName)
    pix = im.load()
    width = im.size[0]
    height = im.size[1]
    exportLists = []
    topRight = GetRGBPixel(im, width, height)             #Grabs the RGB informtion on certain parts of the screen
    topLeft = GetRGBPixel(im, -width, height)
    bottomLeft = GetRGBPixel(im, -width, -height)
    bottomRight = GetRGBPixel(im, width, -height)
    center = GetRGBPixel(im, 0, 0)
    #try:
    #   exportLists = GetCornerColers(width, height, pix)
    #except:
    #    print("fail")
    #    pass
    exportLists.append(topRight)
    exportLists.append(topLeft)
    exportLists.append(bottomLeft)
    exportLists.append(bottomRight)
    exportLists.append(center)
    print(f"EXPORT LIST: {exportLists} ")
    print(exportLists)

    return exportLists




def GetPictureInfo(ListOfLibraries):
    NumOfNames = -1
    originalDirectory = os.getcwd()
    print(f"Original directory: {originalDirectory} ")
    for i in ListOfLibraries:
        NumOfNames = NumOfNames + 1
    NameIndex = 0
    while NameIndex <= NumOfNames:
        name = ListOfLibraries[NameIndex]
            #make more effecieny

        PicNumber = 0
        for pic in os.listdir(name):
            newPic = f"{originalDirectory}/{name}/{pic}"
            print(newPic)
            print("k")
            image = cv2.imread(newPic)
            greyIMG = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            RGBdata = GetRGB(newPic)
            Hcas = cv2.CascadeClassifier(r"haar_cas.xml")
            faces = Hcas.detectMultiScale(greyIMG, 1.1, 3)
            NumOfFaces = [len(faces)]
            if(RGBdata[0] != 0):
               ListForInputNum = [PicNumber]
               ListForName = [name]
               row = ListForName + RGBdata + NumOfFaces
               MakeCSV(row)
            PicNumber += 1
            print("------------------")
        print(f"{name} has been completed")
        NameIndex = NameIndex + 1


def StandarizeNames(Name, ListOfNames):
    NumberRuns = 1
    index = 0
    checkName = ListOfNames[index]
    while Name != checkName:
        index += 1
        checkName = ListOfNames[index]
        NumberRuns += 1
    return 1/NumberRuns


def MakeCSVTitle():
    categorie = ["Name","topright", "topleft", "bottomleft", "bottomright", "center", "faces"]            #put Categori names here
    MakeCSV(categorie)

def MakeCSV(row):
   print(os.getcwd())
   c = open(r"data.csv", 'a')
   writer = csv.writer(c)
   print(row)
   writer.writerow(row)
   c.close()

def CheckBlackList(link, Blist):
    linkChecker = ''
    nameChecker = ''
    linkLen = 0
    for charcter in link:           #get the amount of charcters in the link
        linkLen += 1
    for name in Blist:
        charNum = 0  # For tracking what character the link is on
        RunMain = 0  # Tracking what character the name is on
        nameLength = 0
        softRunner = 0
        fromZero = 0
        print(name)
        for letter in name:
            nameLength += 1
        while charNum != linkLen:
            linkChecker = link[charNum]
            #print(f"LC: {linkChecker}, {name[0]}")
            if name[0] == linkChecker:
                RunMain = 0                #If link is not on a blacklist, code will be able to try agaib at a different section
                nameChecker = name[0]
                #print("first checkpoint")
                softRunner = charNum      #sets soft runner to correct location to save postition on link in case of false positive
                while linkChecker == nameChecker and softRunner < linkLen:
                    #print("e")
                    print(softRunner)
                    print(linkLen)
                    linkChecker = link[softRunner]
                    print()
                    nameChecker = name[fromZero]
                    softRunner += 1
                    fromZero += 1
                    if fromZero == nameLength:
                        print("found blacklisted link")
                        return True
                    else:
                        print(f"lc:{linkChecker} nc: {nameChecker}")
                    if linkChecker != nameChecker:
                        fromZero = 0
            RunMain += 1
            charNum += 1
        return False

def UsersPic():
    print("please place the image you would like to the working directory under the name input.jpg")
    input("Press enter to Continue")
    userInput = r"input.jpg"
    ima = cv2.imread(r"input.jpg")
    greyIMG = cv2.cvtColor(ima, cv2.COLOR_BGR2GRAY)
    RGBdata = GetRGB(userInput)
    Hcas = cv2.CascadeClassifier(r"haar_cas.xml")
    faces = Hcas.detectMultiScale(greyIMG, 1.1, 3)
    NumOfFaces = [len(faces)]
    if (RGBdata[0] != 0):
        ListForInputNum = [0]
        row = RGBdata + NumOfFaces
        MakeCSV(row)

def MakeCSVofUserInput(row):
    c = open(r"userinput.csv", 'a')
    writer = csv.writer(c)
    print(row)
    writer.writerow(row)
    c.close()


def Main():  #Run main
    print("Main running")
    GetData()
    GetPictureInfo(ListOfUsedNames)
    print("The data.csv file has been populated. Please remember to clear said file before running again")
    UsersPic()
    return ListOfUsedNames


#def Main():
#    link = "plspleasepls"
#    list = ["work", "please"]
#    CheckBlackList(link, list)

Main()


#####CODE FOR ONLINE


