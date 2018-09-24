#.saz parser

import zipfile
import os
import re
from xml.dom import minidom
from datetime import datetime
from pathlib import Path

commentedSessions = []
dateFormat = '%Y-%m-%dT%H:%M:%S.%f'
ecidPattern = 'X-ORACLE-DMS-ECID'
cardIdPattern = 'X-FA-CARD-ID'


def extractFiddler(fiddlerPath, destDir):

    zf = zipfile.ZipFile(fiddlerPath)
    zf.extractall(destDir)


def readRawFiles(dir, onlyCommented, time):

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


def isMetaCommented(metaFile):
    # print(metaFile)
    xmldoc = minidom.parse(metaFile)
    sessionflagList = xmldoc.getElementsByTagName('SessionFlag')

    for flag in sessionflagList:
        if flag.attributes['N'].value == 'ui-comments':
            return True, flag.attributes['V'].value

    return False, None


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

    except Exception as ex:
        pass
        # print(ex)


# X-FA-CARD-ID, X-ORACLE-DMS-ECID:
def parseServerFile(metaFile, pattern_str):

    serverFile = metaFile.replace('_m.xml', '_s.txt')

    sfile = open(serverFile, 'rb')

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


def printCommentedSessions():
    for metafile in commentedSessions:
        print(metafile)
        # calcElapsedTime(metafile)
        # parseEcid(metafile)


def processFiddler(fiddler, readCommented, time_str):

    print(fiddler, readCommented, time_str)

    try:

        destDir = Path(fiddler).parent.__str__()

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
