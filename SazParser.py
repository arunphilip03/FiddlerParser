#.saz parser

import zipfile
import os
import re
from xml.dom import minidom
from datetime import datetime
import shutil

commentedSessions = []
dateFormat = '%Y-%m-%dT%H:%M:%S.%f'
ecidPattern = 'X-ORACLE-DMS-ECID'
cardIdPattern = 'X-FA-CARD-ID'

# extract fiddler saz file
def extractFiddler(fiddlerPath, destDir):

    zf = zipfile.ZipFile(fiddlerPath)
    zf.extractall(destDir)

# parse each session in fiddler saz
def readRawFiles(dir, onlyCommented, time):

    commentedSessions.clear()

    for fileName in os.listdir(dir):

        if fileName.endswith('_m.xml'):
            metaFile = os.path.join(dir, fileName)
            elapsedTime = calcElapsedTime(metaFile)

            isComment, commentStr = isMetaCommented(metaFile)

            if onlyCommented:

                if isComment and elapsedTime != None and elapsedTime > time:
                    commentedSessions.append((fileName, elapsedTime, commentStr, parseServerFile(
                        metaFile, ecidPattern), parseServerFile(metaFile, cardIdPattern)))
            else:

                #print(type(elapsedTime), elapsedTime)
                #print(type(time), time)

                if elapsedTime != None and elapsedTime > time:
                    commentedSessions.append((fileName, elapsedTime, commentStr, parseServerFile(
                        metaFile, ecidPattern), parseServerFile(metaFile, cardIdPattern)))


# check if the fiddler session has comments added
def isMetaCommented(metaFile):
    # print(metaFile)
    xmldoc = minidom.parse(metaFile)
    sessionflagList = xmldoc.getElementsByTagName('SessionFlag')

    for flag in sessionflagList:
        if flag.attributes['N'].value == 'ui-comments':
            return True, flag.attributes['V'].value

    return False, None

# calculate elapsed time of a session
def calcElapsedTime(metaFile):

    try:

        xmldoc = minidom.parse(metaFile)
        sessiontimer = xmldoc.getElementsByTagName('SessionTimers')

        clientReqDoneTime = sessiontimer[0].attributes['ClientDoneRequest'].value
        serverResDoneTime = sessiontimer[0].attributes['ServerDoneResponse'].value

        startTime = datetime.strptime(clientReqDoneTime[:24], dateFormat)
        endTime = datetime.strptime(serverResDoneTime[:24], dateFormat)

        timeElapsed = (endTime-startTime).total_seconds()

        # print(timeElapsed)
        return timeElapsed

    except Exception:
        pass
        # print(ex)


# parse session server file (response) for following headers
# X-FA-CARD-ID, X-ORACLE-DMS-ECID:
def parseServerFile(metaFile, pattern_str):

    serverFile = metaFile.replace('_m.xml', '_s.txt')

    sfile = open(serverFile, 'rb')
    print(metaFile, pattern_str)
    result = None

    try:
        for line in sfile:
            linestr = line.decode('utf-8')

            if linestr.startswith(pattern_str):
                matches = re.match("{}: (.*)\r".format(pattern_str), linestr)
                result = matches.group(1)
                break

    except Exception as inst:
        print(type(inst))
        print(inst)
        return result

    return result


# display the filtered sessions
def printCommentedSessions():
    for metafile in commentedSessions:
        for str in metafile:
            print(str, end="\t")
        print()

        

# starting point of processing input fiddler (saz) file
def processFiddler(fiddler, readCommented, time_str):

    print(fiddler, readCommented, time_str)

    try:

        dirName = os.path.dirname(fiddler)
        fileNameExt = os.path.basename(fiddler)
        fileName = os.path.splitext(fileNameExt)[0]
        #print(dirName, fileNameExt, fileName)

        destDir = os.path.join(dirName, fileName)
        #print("dest dir is %s" %destDir)

        if not os.path.exists(destDir):
            os.makedirs(destDir)
        else:
           shutil.rmtree(destDir)
       

        extractFiddler(fiddler, destDir)
        rawDir = os.path.join(destDir, 'raw')
        print('Raw directory is %s' % rawDir)

        if readCommented == 1:
            onlyCommented = True
        else:
            onlyCommented = False

        time = float(time_str)

        readRawFiles(rawDir, onlyCommented, time)
        printCommentedSessions()

    except Exception as ex:
        print(ex)



# test cases
if __name__ == "__main__":

    onlyCommented = False
    time = 5
    fiddler = r'D:\SAZParser\data\18SEP18.saz'
    destDir = r'D:\SAZParser\temp'
    extractFiddler(fiddler, destDir)

    rawDir = os.path.join(destDir, 'raw')
    print('Raw directory is %s' % rawDir)

    readRawFiles(rawDir, onlyCommented, time)
    printCommentedSessions()
