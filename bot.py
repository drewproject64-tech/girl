"""Guncel Girls: self-contained outfit planner, Python 3.12, no paid APIs."""
import json
import logging
import os
import random
import signal
import sqlite3
import threading
import urllib.error
import urllib.request
from pathlib import Path

NAME = 'Guncel Girls'
USERNAME = 'Guncel_Girls_Bot'
BIO = {
    'tr': 'Güncel Girls: günlük kombin fikirleri, renk uyumu ve kaydedilebilir stil önerileri.',
    'en': 'Guncel Girls: everyday outfit ideas, colour matching and saved style inspiration.',
}
DESCRIPTION = {
    'tr': 'Guncel Girls ile günlük kombin fikirleri keşfedin. İş, üniversite, günlük yaşam veya özel bir gün seçin; ardından tarzınıza uygun kıyafet, renk ve aksesuar önerileri alın. Favorilerinizi kaydedin veya renk uyumlarını inceleyin. Ücretsizdir; kanal üyeliği gerekmez. Başlamak için Başlat düğmesine dokunun. Türkçe ve İngilizce desteklenir.',
    'en': 'Discover everyday outfit ideas with Guncel Girls. Choose work, university, casual or a special occasion, then get clothing, colour and accessory suggestions for your style. Save favourite looks or explore colour combinations. Free to use; no channel membership required. Tap Start to begin. Available in Turkish and English.',
}
TEXT = {
 'tr': ['Hoş geldiniz! Bir etkinlik ve tarz seçerek kombin oluşturun. Öneriler genel stil fikirleridir; hava durumuna ve rahatınıza göre uyarlayın.', 'Kombin oluştur', 'Renk uyumu', 'Favorilerim', 'Yardım', 'English', 'Bir etkinlik seçin:', 'Bir tarz seçin:', 'Ana menü', 'Kaydet', 'Başka öneri', 'Kaydedildi.', 'Henüz favoriniz yok. Önce bir kombin oluşturun.', 'Favorileri sil', 'Favoriler silindi.', 'Bir renk seçin:', 'Verilerimi sil', 'Kaydettiğiniz kombinler ve dil tercihiniz bu botun veritabanında tutulur. Fotoğraf, telefon veya konum istemeyiz. /delete_data ile kayıtlarınızı silebilirsiniz. /start: menü, /help: yardım, /privacy: gizlilik. Botu engelleyerek iletişimi durdurabilirsiniz.', 'Verileriniz silindi.', 'Bu seçim artık geçerli değil. /start ile yeniden başlayın.', 'Günün kombini'],
 'en': ['Welcome! Choose an occasion and style to build an outfit. These are general style ideas; adapt them to the weather and your comfort.', 'Build an outfit', 'Colour matcher', 'My favourites', 'Help', 'Türkçe', 'Choose an occasion:', 'Choose a style:', 'Main menu', 'Save', 'Another idea', 'Saved.', 'No favourites yet. Create an outfit first.', 'Clear favourites', 'Favourites cleared.', 'Choose a colour:', 'Delete my data', 'Saved outfits and your language preference are stored in this bot’s database. We do not request photos, phone numbers or location. Use /delete_data to delete your records. /start: menu, /help: help, /privacy: privacy. Block the bot to stop communication.', 'Your data has been deleted.', 'This selection is no longer valid. Use /start to begin again.', 'Today’s outfit'],
}
OCCASIONS = {'tr': ['İş', 'Üniversite', 'Günlük', 'Özel gün'], 'en': ['Work', 'University', 'Casual', 'Special occasion']}
STYLES = {'tr': ['Minimal', 'Tesettür', 'Sportif', 'Zarif'], 'en': ['Minimal', 'Modest', 'Sporty', 'Elegant']}
# Each occasion has two complete bases; style adds a practical adaptation.
BASES = {
 'en': [
 [('Cream shirt, navy tailored trousers', 'Loafers', 'Structured tote'), ('White blouse, charcoal midi skirt', 'Flat ankle boots', 'Small shoulder bag')],
 [('Cotton shirt, straight-leg jeans', 'Comfortable trainers', 'Canvas tote'), ('Breathable knit top, wide-leg trousers', 'Flat shoes', 'Backpack')],
 [('Striped cotton top, relaxed jeans', 'Trainers', 'Crossbody bag'), ('Plain T-shirt, olive cotton trousers', 'Flat sandals', 'Canvas bag')],
 [('Navy midi dress', 'Comfortable dress shoes', 'Small evening bag'), ('Ivory blouse, black wide-leg trousers', 'Smart flats', 'Clutch bag')]],
 'tr': [
 [('Krem gömlek, lacivert kumaş pantolon', 'Loafer', 'Yapılı omuz çantası'), ('Beyaz bluz, antrasit midi etek', 'Düz taban bot', 'Küçük omuz çantası')],
 [('Pamuklu gömlek, düz kesim jean', 'Rahat spor ayakkabı', 'Bez çanta'), ('Hafif triko üst, bol paça pantolon', 'Düz ayakkabı', 'Sırt çantası')],
 [('Çizgili pamuklu üst, rahat jean', 'Spor ayakkabı', 'Çapraz çanta'), ('Düz tişört, zeytin yeşili pamuklu pantolon', 'Düz sandalet', 'Bez çanta')],
 [('Lacivert midi elbise', 'Rahat klasik ayakkabı', 'Küçük gece çantası'), ('Ekru bluz, siyah bol paça pantolon', 'Şık babet', 'Portföy çanta')]],
}
ADAPT = {
 'en': ['Keep accessories simple; add a neutral cardigan if needed.', 'Choose opaque fabrics, a long-sleeved top and ankle-length bottoms; layer a long tunic or coat for your preferred coverage.', 'Use supportive trainers and a lightweight jacket for easy movement.', 'Add a tailored blazer or fine-knit layer and one understated accessory.'],
 'tr': ['Aksesuarları sade tutun; gerekirse nötr bir hırka ekleyin.', 'Opak kumaş, uzun kollu üst ve bilek boy alt tercih edin; istediğiniz örtücülük için uzun tunik veya dış katman ekleyin.', 'Rahat hareket için destekli spor ayakkabı ve hafif ceket tercih edin.', 'Kombini bir blazer veya ince triko katman ve sade bir aksesuarla tamamlayın.'],
}
COLOURS = {'en': ['Navy', 'Cream', 'Olive', 'Black'], 'tr': ['Lacivert', 'Krem', 'Zeytin yeşili', 'Siyah']}
MATCHES = {'en': ['Cream + light blue; add brown accessories.', 'Navy + camel; add white accessories.', 'White + beige; add brown accessories.', 'White + grey; add one burgundy accent.'], 'tr': ['Krem + açık mavi; kahverengi aksesuar ekleyin.', 'Lacivert + camel; beyaz aksesuar ekleyin.', 'Beyaz + bej; kahverengi aksesuar ekleyin.', 'Beyaz + gri; tek bir bordo detay ekleyin.']}


def outfit(lang, occasion, style, variant):
    if lang not in TEXT or occasion not in range(4) or style not in range(4) or variant not in range(2):
        raise ValueError('Invalid outfit')
    clothes, shoes, bag = BASES[lang][occasion][variant]
    if style == 2:
        shoes = 'Destekli spor ayakkabı' if lang == 'tr' else 'Supportive trainers'
    return f'{OCCASIONS[lang][occasion]} · {STYLES[lang][style]}\n\n{clothes}\n{shoes}\n{bag}\n\n{ADAPT[lang][style]}'


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.executescript('CREATE TABLE IF NOT EXISTS preferences (uid INTEGER PRIMARY KEY, lang TEXT); CREATE TABLE IF NOT EXISTS favourites (uid INTEGER, look TEXT, PRIMARY KEY(uid, look));')
    def language(self, uid, detected='tr'):
        row = self.db.execute('SELECT lang FROM preferences WHERE uid=?', (uid,)).fetchone()
        return row[0] if row else ('en' if detected.startswith('en') else 'tr')
    def set_language(self, uid, lang):
        self.db.execute('INSERT OR REPLACE INTO preferences VALUES (?,?)', (uid, lang)); self.db.commit()
    def save(self, uid, look):
        self.db.execute('INSERT OR IGNORE INTO favourites VALUES (?,?)', (uid, look))
        self.db.execute('DELETE FROM favourites WHERE uid=? AND rowid NOT IN (SELECT rowid FROM favourites WHERE uid=? ORDER BY rowid DESC LIMIT 20)', (uid, uid)); self.db.commit()
    def favourites(self, uid):
        return [r[0] for r in self.db.execute('SELECT look FROM favourites WHERE uid=? ORDER BY rowid DESC', (uid,))]
    def clear(self, uid, all_data=False):
        self.db.execute('DELETE FROM favourites WHERE uid=?', (uid,))
        if all_data:
            self.db.execute('DELETE FROM preferences WHERE uid=?', (uid,))
        self.db.commit()


class Bot:
    def __init__(self, token, store):
        self.token, self.store = token, store
    def api(self, method, **params):
        payload = json.dumps(params).encode()
        request = urllib.request.Request(f'https://api.telegram.org/bot{self.token}/{method}', data=payload, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.load(response)
        except urllib.error.HTTPError as exc:
            # Never log exception URLs: they contain the bot token.
            raise RuntimeError(f'Telegram {method} HTTP {exc.code}') from None
        except (urllib.error.URLError, TimeoutError):
            raise RuntimeError(f'Telegram {method} network failure') from None
        if not result.get('ok'):
            raise RuntimeError(f'Telegram {method} failed')
        return result['result']
    def configure(self):
        me = self.api('getMe')
        if me.get('username', '').lower() != USERNAME.lower():
            raise RuntimeError('BOT_TOKEN does not belong to Guncel_Girls_Bot')
        self.api('setMyName', name=NAME)
        for code in ('', 'tr', 'en'):
            lang = code or 'tr'
            self.api('setMyShortDescription', short_description=BIO[lang], language_code=code)
            self.api('setMyDescription', description=DESCRIPTION[lang], language_code=code)
            labels = ['Menü', 'Yardım', 'Gizlilik', 'Verilerimi sil'] if lang == 'tr' else ['Menu', 'Help', 'Privacy', 'Delete my data']
            self.api('setMyCommands', language_code=code, commands=[{'command': command, 'description': label} for command, label in zip(('start', 'help', 'privacy', 'delete_data'), labels)])
    @staticmethod
    def keyboard(items):
        return {'inline_keyboard': [[{'text': label, 'callback_data': data}] for label, data in items]}
    def send(self, chat, text, items=()):
        self.api('sendMessage', chat_id=chat, text=text, reply_markup=self.keyboard(items))
    def menu(self, chat, lang):
        t = TEXT[lang]
        self.send(chat, t[0], [(t[1], 'build'), (t[20], 'daily'), (t[2], 'colours'), (t[3], 'saved'), (t[4], 'help'), (t[5], 'lang:en' if lang == 'tr' else 'lang:tr')])
    def handle(self, update):
        callback = update.get('callback_query')
        message = callback.get('message', {}) if callback else update.get('message', {})
        user = callback['from'] if callback else message.get('from', {})
        if message.get('chat', {}).get('type') != 'private' or not user.get('id'):
            return
        uid, chat = user['id'], message['chat']['id']
        lang = self.store.language(uid, user.get('language_code', 'tr'))
        t = TEXT[lang]
        if callback:
            self.api('answerCallbackQuery', callback_query_id=callback['id'])
            data = callback.get('data', '')
        else:
            data = {'/start': 'menu', '/help': 'help', '/privacy': 'help', '/delete_data': 'delete'}.get(message.get('text', '').split(' ')[0].split('@')[0], 'menu')
        back = [(t[8], 'menu')]
        if data == 'menu':
            self.menu(chat, lang)
        elif data in ('lang:en', 'lang:tr'):
            lang = data[-2:]; self.store.set_language(uid, lang); self.menu(chat, lang)
        elif data == 'build':
            self.send(chat, t[6], [(label, f'occasion:{i}') for i, label in enumerate(OCCASIONS[lang])] + back)
        elif data.startswith('occasion:'):
            try:
                occasion = int(data.split(':')[1]); assert occasion in range(4)
            except (ValueError, AssertionError):
                self.send(chat, t[19], back); return
            self.send(chat, t[7], [(label, f'look:{occasion}:{i}:0') for i, label in enumerate(STYLES[lang])] + back)
        elif data == 'daily' or data.startswith(('look:', 'save:')):
            try:
                if data == 'daily':
                    o, s, v = random.randrange(4), random.randrange(4), random.randrange(2)
                else:
                    _, a, b, c = data.split(':'); o, s, v = int(a), int(b), int(c)
                look = outfit(lang, o, s, v)
            except (ValueError, IndexError):
                self.send(chat, t[19], back); return
            if data.startswith('save:'):
                self.store.save(uid, look); self.send(chat, t[11], back)
            else:
                self.send(chat, look, [(t[9], f'save:{o}:{s}:{v}'), (t[10], f'look:{o}:{s}:{1-v}')] + back)
        elif data == 'colours':
            self.send(chat, t[15], [(label, f'colour:{i}') for i, label in enumerate(COLOURS[lang])] + back)
        elif data.startswith('colour:'):
            try:
                index = int(data.split(':')[1]); assert index in range(4)
            except (ValueError, AssertionError):
                self.send(chat, t[19], back); return
            self.send(chat, COLOURS[lang][index] + '\n\n' + MATCHES[lang][index], [(t[2], 'colours')] + back)
        elif data == 'saved':
            looks = self.store.favourites(uid)
            # One saved look per message keeps replies within Telegram limits.
            for look in looks:
                self.send(chat, look)
            self.send(chat, t[3] if looks else t[12], ([(t[13], 'clear')] if looks else []) + back)
        elif data == 'clear':
            self.store.clear(uid); self.send(chat, t[14], back)
        elif data == 'delete':
            self.store.clear(uid, all_data=True); self.send(chat, t[18], back)
        elif data == 'help':
            self.send(chat, t[17], [(t[16], 'delete')] + back)
        else:
            self.send(chat, t[19], back)


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    token = os.environ.get('BOT_TOKEN', '').strip()
    if not token:
        raise SystemExit('Set BOT_TOKEN in your hosting environment; never commit it.')
    bot = Bot(token, Store(os.environ.get('DB_PATH', 'data/girls.db')))
    stop = threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    try:
        bot.configure()
        bot.api('deleteWebhook', drop_pending_updates=False)
        logging.info('Profile configured; starting private-chat polling')
        offset = 0
        while not stop.is_set():
            try:
                updates = bot.api('getUpdates', offset=offset, timeout=25, allowed_updates=['message', 'callback_query'])
                for update in updates:
                    if stop.is_set():
                        break
                    try:
                        bot.handle(update)
                    except Exception:
                        logging.error('Could not process update; use /start to retry')
                    offset = update['update_id'] + 1
            except RuntimeError:
                logging.warning('Polling unavailable; retrying in five seconds')
                stop.wait(5)
    finally:
        bot.store.db.close()


if __name__ == '__main__':
    main()
