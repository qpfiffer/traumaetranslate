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
        # Turns positivity(noneness) into ['positivity', 'noneness']
        broken_up = potential_english.replace(")", "").split("(")
        translated = reduce(
            lambda accum, val: accum + ENGLISH_TO_TRAUMAE_ALPHABET.get(val, "__"),
            broken_up,
            "")
        return translated

    def attempt_traumae_to_english(self, potential_traumae):
        letters = list()
        [letters.append(potential_traumae[i:i+2]) for i in range(0, len(potential_traumae), 2)]
        return reduce(lambda a, v: TRAUMAE_TO_ENGLISH.get(v, "__") + "(" + a + ")", letters[::-1], "")

    def get_suggested_meaning_list(self, words):
        traumae_api_url = "http://api.xxiivv.com/?key=traumae&cmd=read"
        request = requests.get(traumae_api_url)
        json = request.json()
        to_return = {word:"?" for word in words}

        for s_id in json.keys():
            # ["pixi","research","Expression","sure","head"]
            for traumae_word in words:
                if json[s_id][0] == traumae_word:
                    to_return[traumae_word] = json[s_id][1]

        return to_return.values()

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
            translated = self.attempt_english_to_traumae(to_translate)
            self.send('{nick}: Traumae translation: {translated}, Suggested meaning: {meaning}'.format(
                nick=data['nick'],
                translated=translated,
                meaning=self.get_suggested_meaning(translated)),
                        data=data)
            return

        else:
            # We're probably dealing with a traumae word.
            if " " in to_translate:
                traumae_words = to_translate.split(" ")
                words = [self.attempt_traumae_to_english(word) for word in traumae_words]
                translated = reduce(lambda a,v: v + " " + a, words, "")
                suggested = self.get_suggested_meaning_list(traumae_words)
                suggested = reduce(lambda a,v: a + " " + v, suggested[::1], "")
            else:
                translated = self.attempt_traumae_to_english(to_translate)
                suggested = self.get_suggested_meaning(to_translate)

            self.send('{nick}: Traumae translation: {translated}, Suggested meaning: {meaning}'.format(
                nick=data['nick'],
                translated=translated,
                meaning=suggested),
                        data=data)

def main():
    run_client(TraumaeTranslate)

if __name__ == '__main__':
    main()
