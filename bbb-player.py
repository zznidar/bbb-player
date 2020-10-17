import argparse
from urllib.parse import urlparse
import os
import urllib.request
import json
from distutils.dir_util import copy_tree
from http.server import HTTPServer, SimpleHTTPRequestHandler


def downloadFiles(baseURL, basePath):
    filesForDL = ["captions.json", "cursor.xml", "deskshare.xml", "metadata.xml",
                  "panzooms.xml", "presentation_text.json", "shapes.svg", "slides_new.xml", "video/webcams.webm", "video/webcams.mp4", "deskshare/deskshare.webm", "deskshare/deskshare.mp4"]

    for file in filesForDL:
        print('Downloading ' + file)
        downloadURL = baseURL + file
        # print(downloadURL)
        savePath = basePath + file
        # print(savePath)

        try:
            urllib.request.urlretrieve(downloadURL, savePath)
        except:
            print("Did not download " + file)


def downloadSlides(baseURL, basePath):
    # Part of this is based on https://www.programiz.com/python-programming/json
    with open(basePath + '/presentation_text.json') as f:
        data = json.load(f)
        for element in data:
            print(element)
            noSlides = 0
            for slide in data[element]:
                noSlides = noSlides + 1
            print(noSlides)
            createFolder(basePath + '/presentation/' + element)
            for i in range(1, noSlides+1):
                downloadURL = baseURL + 'presentation/' + \
                    element + '/slide-' + str(i) + '.png'
                savePath = basePath + '/presentation/' + \
                    element + '/slide-' + str(i) + '.png'

                print(downloadURL)
                print(savePath)
                try:
                    urllib.request.urlretrieve(downloadURL, savePath)
                except:
                    print("Did not download " + element +
                          '/slide-' + str(i) + '.png')


def createFolder(path):
    # Create meeting folders, based on https://stackabuse.com/creating-and-deleting-directories-with-python/
    try:
        os.makedirs(path)
    except OSError:
        print("Creation of the directory %s failed" % path)
    else:
        print("Successfully created the directory %s " % path)


# Parse the command line arguments
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("--download", type=str, nargs=1,
                   help="download the BBB conference linked here")
group.add_argument("--play", type=str, nargs=1,
                   help="play BBB conference saved locally with ID")
args = parser.parse_args()

if(args.download != None and args.play == None):
    print("Download")
    inputURL = args.download[0]
    meetingId = urlparse(inputURL).query[10:]
    print(meetingId)
    baseURL = urlparse(inputURL).scheme + '://' + \
        urlparse(inputURL).netloc + '/presentation/' + meetingId + '/'
    print(baseURL)

    folderPath = "./downloadedMeetings/" + meetingId

    if(os.path.isdir(folderPath) == False):

        createFolder(folderPath)
        createFolder(folderPath + '/video')
        createFolder(folderPath + '/deskshare')
        createFolder(folderPath + '/presentation')

        downloadFiles(baseURL, folderPath + '/')
        downloadSlides(baseURL, folderPath)
        copy_tree("./player", "downloadedMeetings/" + meetingId + "/player")

    else:
        print("Folder for this meeting already exists.")

elif(args.download == None and args.play != None):
    print("Play")
    fileId = args.play[0]

    os.chdir('./downloadedMeetings/' + fileId)

    print('---------')
    print('In your broswer open:')
    print('localhost:8000/player/playback.html')
    print('Press CTRL+C when done.')
    print('---------')

    # Based on https://stackoverflow.com/a/54413906
    httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
    httpd.serve_forever()


else:
    print("Error parsing aguments. Use '--help' for help.")