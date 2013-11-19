import requests, json
from os.path import join

from tenyks.client import Client, run_client
from tenyks.config import settings

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
    direct_only = False

    def __init__(self, *args, **kwargs):
        super(TraumaeTranslate, self).__init__(*args, **kwargs)

    def recurring(self):
        self.logger.debug('DOING NOTHING')

    def handle(*args, **kwargs):
        pass

    def attempt_english_to_traumae(self, potential_english):
        # Turns positivity(noneness) into ['positivity', 'noneness']
        broken_up = potential_english.replace(")", "").split("(")
        translated = reduce(
            lambda accum, val: accum + ENGLISH_TO_TRAUMAE_ALPHABET.get(val.lower(), "__"),
            broken_up,
            "")
        return translated

    def attempt_traumae_to_english(self, potential_traumae):
        letters = list()
        [letters.append(potential_traumae[i:i+2]) for i in range(0, len(potential_traumae), 2)]
        for aeth in letters:
            # Make sure we're dealing with all Traumae, here:
            if TRAUMAE_TO_ENGLISH.get(aeth.lower(), None) is None:
                raise Exception("Letter not in dictionary.")

        return reduce(
            lambda a, v: TRAUMAE_TO_ENGLISH.get(v.lower(), "?") + "(" + a + ")",
            letters[::-1],
            "")

    def get_traumae_json(self):
        traumae_api_url = "http://api.xxiivv.com/?key=traumae&cmd=read"
        request = requests.get(traumae_api_url)
        return request.json()

    def get_traumae_json_for_word(self, word):
        traumae_api_url = "http://api.xxiivv.com/?key=traumae&filter={}".format(word)
        request = requests.get(traumae_api_url)
        json = {}

        try:
            json = request.json()
        except ValueError as e:
            # No json came back. No translation.
            pass

        return json

    def get_suggested_meaning_list(self, words):
        to_return = []

        for word in words:
            json = self.get_traumae_json_for_word(word)
            try:
                to_return.append(json[word]["english"])
            except KeyError as e:
                to_return.append("?")

        return to_return

    def get_suggested_definition(self, english_word):
        json = self.get_traumae_json_for_word(english_word)
        word = "?"

        if json:
            word = ", ".join(json.keys())

        return word

    def get_suggested_meaning(self, traumae_word):
        json = self.get_traumae_json()
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
            traumae_words = to_translate.split(" ")
            try:
                words = [self.attempt_traumae_to_english(word) for word in traumae_words]
            except:
                # Something in there isn't traumae.
                words = [self.get_suggested_definition(word) for word in traumae_words]
                words = reduce(lambda a, v: a + " " + v, words, "")
                self.send('{nick}: Traumae translation: {words}'.format(
                    nick=data['nick'],
                    words=words),
                    data=data)
            else:
                translated = reduce(lambda a,v: v + " " + a, words, "")
                suggested = self.get_suggested_meaning_list(traumae_words)
                suggested = reduce(lambda a,v: a + " " + v, suggested[::1], "")
                self.send('{nick}: Traumae translation: {translated}, Suggested meaning: {meaning}'.format(
                    nick=data['nick'],
                    translated=translated,
                    meaning=suggested),
                            data=data)

def main():
    run_client(TraumaeTranslate)

if __name__ == '__main__':
    main()
