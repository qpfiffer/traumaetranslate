import requests, json
from os.path import join

from tenyksclient.client import Client, run_client
from tenyksclient.config import settings

ENGLISH_TO_TRAUMAE_ALPHABET = {
    'parent':        'ki',
    'location':      'ti',
    'children':      'pi',
    'psychology':    'xi',
    'physiognomy':   'di',
    'physicality':   'bi',
    'complexity':    'si',
    'organicity':    'li',
    'syntheticity':  'vi',
    'inwardness':    'ka',
    'stability':     'ta',
    'outwardness':   'pa',
    'addition':      'xa',
    'equality':      'da',
    'subtraction':   'ba',
    'multiplicity':  'sa',
    'uniqueness':    'la',
    'noneness':      'va',
    'impossibility': 'ko',
    'possibility':   'to',
    'specificity':   'po',
    'positivity':    'xo',
    'unknown':       'do',
    'negativity':    'bo',
    'observation':   'so',
    'existence':     'lo',
    'interaction':   'vo',
}

TRAUMAE_TO_ENGLISH = {v:k for k, v in ENGLISH_TO_TRAUMAE_ALPHABET.items()}

class TraumaeTranslate(Client):

    irc_message_filters = {
        'translate': [r'translate (.*)'],
        #'list_feeds': r'list feeds',
        #'del_feed': r'delete feed (.*)',
    }
    direct_only = True

    def __init__(self, *args, **kwargs):
        super(TraumaeTranslate, self).__init__(*args, **kwargs)

    def recurring(self):
        self.logger.debug('Fetching latest suggestions')

    def attempt_english_to_traumae(self, potential_english):
        pass

    def attempt_traumae_to_english(self, potential_traumae):
        pass

    def get_suggested_meaning(self, traumae_word):
        traumae_api_url = "http://api.xxiivv.com/?key=traumae&cmd=read"
        request = requests.get(traumae_api_url)
        json = request.json()
        for s_id in json.keys():
            # ["pixi","research","Expression","sure","head"]
            if json[s_id][0] == traumae_word:
                return json[s_id][1]

        return "N/A"

    def handle_translate(self, data, match):
        # Raw data
        to_translate = match.groups()[0]

        if "(" in to_translate:
            # Turns positivity(noneness) into ['positivity', 'noneness']
            broken_up = to_translate.replace(")", "").split("(")
            translated = reduce(
                lambda accum, val: accum + ENGLISH_TO_TRAUMAE_ALPHABET[val],
                broken_up, "")
            #import ipdb; ipdb.set_trace()
            self.send('{nick}: Traumae translation: {translated}, Suggested meaning: {meaning}'.format(
                nick=data['nick'],
                translated=translated,
                meaning=self.get_suggested_meaning(translated)),
                        data=data)
            return

        else:
            # We're probably dealing with a traumae word.
            if(len(to_translate) % 2 != 0 or
                '\'' in to_translate):
                    # They want me to translate something hard. :(
                self.send("{nick}: You've given me complex word. I'm not that smart yet.".format(
                    nick=data['nick']),
                    data=data)
                return
            letters = list()
            [letters.append(to_translate[i:i+2]) for i in range(0, len(to_translate), 2)]
            #import ipdb; ipdb.set_trace()
            translated = reduce(lambda a, v: TRAUMAE_TO_ENGLISH[v] + "(" + a + ")", letters[::-1], "")
            self.send('{nick}: Traumae translation: {translated}, Suggested meaning: {meaning}'.format(
                nick=data['nick'],
                translated=translated,
                meaning=self.get_suggested_meaning(to_translate)),
                        data=data)

def main():
    run_client(TraumaeTranslate)

if __name__ == '__main__':
    main()
