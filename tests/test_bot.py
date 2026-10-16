import unittest
from bot import Bot, BIO, DESCRIPTION, outfit

class FakeBot(Bot):
    def __init__(self):
        super().__init__('fake-token'); self.calls = []
    def api(self, method, **params):
        self.calls.append((method, params))
        return {'username': 'Guncel_Girls_Bot'} if method == 'getMe' else True

class BotTests(unittest.TestCase):
    def test_profile(self):
        bot = FakeBot(); bot.configure()
        self.assertTrue(all(len(v) <= 120 for v in BIO.values()))
        self.assertTrue(all(len(v) <= 512 for v in DESCRIPTION.values()))
        self.assertEqual(sum(m == 'setMyDescription' for m,p in bot.calls), 3)
    def test_flows_and_language(self):
        bot = FakeBot()
        for data in ('tr|menu', 'tr|build', 'tr|occasion:0', 'tr|look:0:1:0', 'tr|daily', 'tr|colours', 'tr|colour:0', 'tr|help', 'tr|lang:en', 'en|build', 'en|occasion:2', 'en|look:2:3:1', 'en|look:99:0:0'):
            bot.handle({'callback_query': {'id': 'q', 'from': {'id': 42}, 'data': data, 'message': {'chat': {'id': 42, 'type': 'private'}}}})
        self.assertEqual(bot.lang, 'en')
        self.assertIn('no longer valid', bot.calls[-1][1]['text'])
        for method, params in bot.calls:
            for row in params.get('reply_markup', {}).get('inline_keyboard', []):
                for button in row:
                    self.assertLessEqual(len(button['callback_data'].encode()), 64)
    def test_all_outfits(self):
        for lang in ('tr', 'en'):
            for o in range(4):
                for s in range(4):
                    for v in range(2):
                        self.assertTrue(outfit(lang, o, s, v))
    def test_start(self):
        bot = FakeBot()
        bot.handle({'message': {'from': {'id': 42}, 'chat': {'id': 42, 'type': 'private'}, 'text': '/start campaign'}})
        self.assertIn('Hoş geldiniz', bot.calls[-1][1]['text'])
