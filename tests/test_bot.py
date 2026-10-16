import tempfile
import unittest
from pathlib import Path
from bot import BIO, DESCRIPTION, Bot, Store, outfit


class FakeBot(Bot):
    def __init__(self, store):
        super().__init__('not-a-real-token', store)
        self.calls = []
    def api(self, method, **params):
        self.calls.append((method, params))
        return {'username': 'Guncel_Girls_Bot'} if method == 'getMe' else True


class BotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = str(Path(self.tmp.name) / 'test.db')
        self.store = Store(self.path)
        self.bot = FakeBot(self.store)
    def tearDown(self):
        self.store.db.close()
        self.tmp.cleanup()
    def click(self, data, uid=42):
        self.bot.handle({'callback_query': {'id': 'test', 'from': {'id': uid, 'language_code': 'tr'}, 'data': data, 'message': {'chat': {'id': uid, 'type': 'private'}}}})
    def test_metadata_before_start(self):
        self.bot.configure()
        self.assertTrue(all(len(v) <= 120 for v in BIO.values()))
        self.assertTrue(all(len(v) <= 512 for v in DESCRIPTION.values()))
        self.assertEqual(len([m for m,p in self.bot.calls if m == 'setMyDescription']), 3)
    def test_every_outfit_and_save_isolation(self):
        for lang in ('tr', 'en'):
            for o in range(4):
                for s in range(4):
                    for v in range(2):
                        self.assertTrue(outfit(lang, o, s, v))
        self.click('look:0:1:0')
        self.assertIn('Krem', self.bot.calls[-1][1]['text'])
        self.click('save:0:1:0')
        self.assertEqual(len(self.store.favourites(42)), 1)
        self.assertEqual(self.store.favourites(43), [])
        self.click('delete')
        self.assertEqual(self.store.favourites(42), [])
    def test_language_persists_and_favourites_cap(self):
        self.click('lang:en')
        self.assertEqual(self.store.language(42), 'en')
        for i in range(25):
            self.store.save(42, str(i))
        self.assertEqual(len(self.store.favourites(42)), 20)
        other = Store(self.path)
        self.assertEqual(other.language(42), 'en')
        self.assertEqual(len(other.favourites(42)), 20)
        other.db.close()
    def test_all_menus_and_invalid_callbacks(self):
        for data in ('menu', 'build', 'occasion:0', 'daily', 'colours', 'colour:0', 'saved', 'clear', 'help', 'occasion:99', 'look:99:0:0', 'colour:-1', 'unknown'):
            self.click(data)
        for _, params in self.bot.calls:
            for row in params.get('reply_markup', {}).get('inline_keyboard', []):
                for button in row:
                    self.assertLessEqual(len(button['callback_data'].encode()), 64)
    def test_start_and_groups(self):
        self.bot.handle({'message': {'from': {'id': 42}, 'chat': {'id': 42, 'type': 'private'}, 'text': '/start campaign'}})
        self.assertIn('Hoş geldiniz', self.bot.calls[-1][1]['text'])
        before = len(self.bot.calls)
        self.bot.handle({'message': {'from': {'id': 42}, 'chat': {'id': -1, 'type': 'group'}, 'text': '/start'}})
        self.assertEqual(len(self.bot.calls), before)


if __name__ == '__main__':
    unittest.main()
