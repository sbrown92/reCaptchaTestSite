import json

from sox import core as sx
from watson_developer_cloud import SpeechToTextV1

from keys import WATSON_USER, WATSON_PASS



def splitFile(fileName):

    args = [fileName, 'outfile.wav', 'silence',
            '1', '0.1', '0.1',
            '1', '0.1', '0.1',
            ': newfile', ': restart']

    # Calls the silence argument to `sox`
    #   - args is a list of arguments passed
    #   - Will create set of wav files in working directory sequentially
    #   named outfile (outfile001, outfile002, ...)
    #   - Starts splitting audio when .1 seconds of 1% of volume is detected
    #   - Stops splitting audio after .1 seconds of silence is detected
    #   - Loops through entire file, so can do whole captcha message in one go!
    sx.sox(args)

    # Creates Watson Speech to Text Object
    speech_engine = SpeechToTextV1(username=WATSON_USER,
                                   password=WATSON_PASS,
                                   x_watson_learning_opt_out=True)

    # Makes request to Speech to Text API
    # Prints response received from API
    with open('<testFile || outfile0**>' + '.wav', 'rb') as sourceFile:
        print(json.dumps(speech_engine.recognize(sourceFile,
                                                 content_type='audio/wav',
                                                 continuous=True,
                                                 model='en-UK_NarrowbandModel',
                                                 inactivity_timeout=5, indent=2)))