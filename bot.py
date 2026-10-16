"""Guncel Girls: self-contained outfit planner, Python 3.12, no paid APIs."""
import json
import logging
import os
import random
import signal
import threading
import urllib.error
import urllib.request

NAME = 'Guncel Girls'
USERNAME = 'Guncel_Girls_Bot'
BIO = {
    'tr': 'Güncel Girls: günlük kombin fikirleri ve renk uyumu önerileri.',
    'en': 'Guncel Girls: everyday outfit ideas and colour matching inspiration.',
}
DESCRIPTION = {
    'tr': 'Guncel Girls ile günlük kombin fikirleri keşfedin. İş, üniversite, günlük yaşam veya özel bir gün seçin; ardından tarzınıza uygun kıyafet, renk ve aksesuar önerileri alın. Renk uyumlarını inceleyin. Ücretsizdir; kanal üyeliği gerekmez. Başlamak için Başlat düğmesine dokunun. Türkçe ve İngilizce desteklenir.',
    'en': 'Discover everyday outfit ideas with Guncel Girls. Choose work, university, casual or a special occasion, then get clothing, colour and accessory suggestions for your style. Explore colour combinations. Free to use; no channel membership required. Tap Start to begin. Available in Turkish and English.',
}
TEXT = {
 'tr': ['Hoş geldiniz! Bir etkinlik ve tarz seçerek kombin oluşturun. Öneriler genel stil fikirleridir; hava durumuna ve rahatınıza göre uyarlayın.', 'Kombin oluştur', 'Renk uyumu', 'Favorilerim', 'Yardım', 'English', 'Bir etkinlik seçin:', 'Bir tarz seçin:', 'Ana menü', 'Kaydet', 'Başka öneri', 'Kaydedildi.', 'Henüz favoriniz yok. Önce bir kombin oluşturun.', 'Favorileri sil', 'Favoriler silindi.', 'Bir renk seçin:', 'Verilerimi sil', 'Etkinlik ve tarz seçin veya renk uyumlarını keşfedin. Kullanıcı kaydı, veritabanı ve yönetici paneli yoktur. Mesajlar işlem sırasında kullanılır; uygulama mesaj geçmişini kaydetmez. Telegram kendi politikaları kapsamında mesajları saklayabilir. /start: menü, /help: yardım, /privacy: gizlilik.', 'Verileriniz silindi.', 'Bu seçim artık geçerli değil. /start ile yeniden başlayın.', 'Günün kombini'],
 'en': ['Welcome! Choose an occasion and style to build an outfit. These are general style ideas; adapt them to the weather and your comfort.', 'Build an outfit', 'Colour matcher', 'My favourites', 'Help', 'Türkçe', 'Choose an occasion:', 'Choose a style:', 'Main menu', 'Save', 'Another idea', 'Saved.', 'No favourites yet. Create an outfit first.', 'Clear favourites', 'Favourites cleared.', 'Choose a colour:', 'Delete my data', 'Choose an occasion and style or explore colour combinations. No user registration, database or admin panel. Messages are processed to reply; this app does not save chat history. Telegram may retain messages under its own policies. /start: menu, /help: help, /privacy: privacy.', 'Your data has been deleted.', 'This selection is no longer valid. Use /start to begin again.', 'Today’s outfit'],
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


class Bot:
    def __init__(self, token):
        self.token = token
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
            self.api('setMyCommands', language_code=code, commands=[{'command': command, 'description': label} for command, label in zip(('start', 'help', 'privacy'), labels)])
    @staticmethod
    def keyboard(items):
        return {'inline_keyboard': [[{'text': label, 'callback_data': data}] for label, data in items]}
    def send(self, chat, text, items=()):
        items = [(label, f'{self.lang}|{data}') for label, data in items]
        self.api('sendMessage', chat_id=chat, text=text, reply_markup=self.keyboard(items))
    def menu(self, chat, lang):
        t = TEXT[lang]
        self.send(chat, t[0], [(t[1], 'build'), (t[20], 'daily'), (t[2], 'colours'), (t[4], 'help'), (t[5], 'lang:en' if lang == 'tr' else 'lang:tr')])
    def handle(self, update):
        callback = update.get('callback_query')
        message = callback.get('message', {}) if callback else update.get('message', {})
        user = callback['from'] if callback else message.get('from', {})
        if message.get('chat', {}).get('type') != 'private' or not user.get('id'):
            return
        uid, chat = user['id'], message['chat']['id']
        lang = 'en' if user.get('language_code', '').startswith('en') else 'tr'
        t = TEXT[lang]
        if callback:
            self.api('answerCallbackQuery', callback_query_id=callback['id'])
            data = callback.get('data', '')
            if '|' in data:
                selected, data = data.split('|', 1)
                if selected in TEXT:
                    lang = selected
                    t = TEXT[lang]
        else:
            data = {'/start': 'menu', '/help': 'help', '/privacy': 'help', '/delete_data': 'help'}.get(message.get('text', '').split(' ')[0].split('@')[0], 'menu')
        self.lang = lang
        back = [(t[8], 'menu')]
        if data == 'menu':
            self.menu(chat, lang)
        elif data in ('lang:en', 'lang:tr'):
            lang = data[-2:]; self.lang = lang; self.menu(chat, lang)
        elif data == 'build':
            self.send(chat, t[6], [(label, f'occasion:{i}') for i, label in enumerate(OCCASIONS[lang])] + back)
        elif data.startswith('occasion:'):
            try:
                occasion = int(data.split(':')[1]); assert occasion in range(4)
            except (ValueError, AssertionError):
                self.send(chat, t[19], back); return
            self.send(chat, t[7], [(label, f'look:{occasion}:{i}:0') for i, label in enumerate(STYLES[lang])] + back)
        elif data == 'daily' or data.startswith('look:'):
            try:
                if data == 'daily':
                    o, s, v = random.randrange(4), random.randrange(4), random.randrange(2)
                else:
                    _, a, b, c = data.split(':'); o, s, v = int(a), int(b), int(c)
                look = outfit(lang, o, s, v)
            except (ValueError, IndexError):
                self.send(chat, t[19], back); return
            self.send(chat, look, [(t[10], f'look:{o}:{s}:{1-v}')] + back)
        elif data == 'colours':
            self.send(chat, t[15], [(label, f'colour:{i}') for i, label in enumerate(COLOURS[lang])] + back)
        elif data.startswith('colour:'):
            try:
                index = int(data.split(':')[1]); assert index in range(4)
            except (ValueError, AssertionError):
                self.send(chat, t[19], back); return
            self.send(chat, COLOURS[lang][index] + '\n\n' + MATCHES[lang][index], [(t[2], 'colours')] + back)
        elif data == 'help':
            self.send(chat, t[17], back)
        else:
            self.send(chat, t[19], back)


def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    token = os.environ.get('BOT_TOKEN', '').strip()
    if not token:
        raise SystemExit('Set BOT_TOKEN in your hosting environment; never commit it.')
    bot = Bot(token)
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
        logging.info('Bot stopped')


if __name__ == '__main__':
    main()
