import vk_api, vk, sqlite3, config
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from datetime import datetime
from matplotlib import pyplot as plt
from vk_api import VkUpload


vk_session = vk_api.VkApi(token=config.TOKEN)
longpoll = VkBotLongPoll(vk_session, config.BOT_ID)
vk = vk_session.get_api()
vk_upload = VkUpload(vk)

con = sqlite3.connect("data.db")
cur = con.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
            id INTEGER,
            date TEXT,
            count INTEGER DEFAULT 0
    )
""")


def send(event, message, disable_mentions=False, attachment=None):
    if attachment:
        response = vk_upload.photo_messages(attachment)[0]
        attachment = f"photo{response['owner_id']}_{response['id']}_{response['access_key']}"


    vk.messages.send(
        random_id = get_random_id(),
        message=message,
        chat_id = event.chat_id,
        disable_mentions=disable_mentions,
        attachment=attachment
    )


def get_user(user_id, fields: list = None):
    data = vk.users.get(
        user_ids=[user_id],
        fields=fields
    )
    return data[0]


def update_stats(event: vk_api.bot_longpoll.VkBotMessageEvent):
    user_id = event.message['from_id']

    # чтобы бот не считал сообщения ботов
    # id сообществ отрицательные
    if user_id < 0:
        return
    
    today = datetime.now().date()
    data = cur.execute(f"SELECT id FROM messages WHERE id = '{user_id}' AND date = '{today}'").fetchone()
    if not data:
        cur.execute("INSERT INTO messages (id, date) VALUES (?, ?)", (user_id, today))

    cur.execute(f"UPDATE messages SET count = count + 1 WHERE id = '{user_id}' AND date = '{today}'")
    con.commit()


def profile(event, args):
    if args:
        mention = args[0]
        try:
            user_id = mention.removeprefix("[id").split("|")[0]
        except Exception as err:
            send(event, f"Неверно указан пользователь\n{err}")
            return

    else:
        user_id = event.message["from_id"]
    
    if not cur.execute(f"SELECT id FROM messages WHERE id = '{user_id}'").fetchone():
        send(event, f"Пользователь не найден")
        return
    
    today = datetime.now().date()
    total_messages = cur.execute(f"SELECT SUM(count) FROM messages WHERE id = '{user_id}'").fetchone()[0]

    messages_today = cur.execute(f"SELECT count FROM messages WHERE id = '{user_id}' AND date = '{today}'").fetchone()
    if not messages_today:
        messages_today = 0
    else:
        messages_today = messages_today[0]

    message = f"Статистика пользователя {get_user(user_id)['first_name']}\n📃 Всего сообщений: {total_messages}\n✉️ Сообщений сегодня: {messages_today}"
    send(event, message)
    

def stats(event):
    today = datetime.now().date()
    top_users = cur.execute(f"SELECT id, count FROM messages WHERE date = '{today}' ORDER BY count DESC LIMIT 10").fetchall()
    
    if not top_users:
        send(event, "Сегодня еще никто не писал в чат")
        return
    
    total_today = cur.execute(f"SELECT SUM(count) FROM messages WHERE date = '{today}'").fetchone()[0]


    
    message = f"🏆 Топ активных за сегодня:\n"
    for data, i in zip(top_users, range(1, 11)):
        message += f"{i}. @{get_user(data[0], fields=['screen_name'])['screen_name']} - {data[1]} ✉️\n"

    message += f"\nВсего сообщений за сегодня: {total_today}"

    send(event, message, disable_mentions=True)


def stats_all(event):
    top_users = cur.execute(f"SELECT id, count FROM messages ORDER BY count DESC LIMIT 10").fetchall()
    
    if not top_users:
        send(event, "Еще никто не писал в чат")
        return
    
    messages_total = cur.execute("SELECT SUM(count) FROM messages").fetchone()[0]

    message = f"🏆 Топ активных:\n"
    for data, i in zip(top_users, range(1, 11)):
        message += f"{i}. @{get_user(data[0], fields=['screen_name'])['screen_name']} - {data[1]} ✉️\n"

    message += f"\nВсего сообщений: {messages_total}"

    data = cur.execute("SELECT date, SUM(count) FROM messages GROUP BY date LIMIT 3 OFFSET -3").fetchall()
    x, y = [], []
    for date, messages in data:
        x.append(date)
        y.append(messages) 

    plt.plot(x, y)
    plt.title('Статистика сообщений за последний месяц', fontsize=14, loc='left') 
    plt.savefig("plot.png")

    with open("plot.png", "rb") as plot:
        send(event, message, disable_mentions=True, attachment=plot)


def catch_messages():
    for event in longpoll.listen():
        if event.type != VkBotEventType.MESSAGE_NEW:
            continue

        # Обновление статистики
        update_stats(event)

        if not event.message["text"].startswith(config.PREFIX):
            continue

        text: str = event.message["text"].removeprefix(config.PREFIX)

        # Удаление префикса и разделение на слова
        words = text.split(" ")
        command = words[0]
        
        if text == "стата":
            stats(event)
        
        elif text.startswith("стата моя"):
            args = words[2:]
            profile(event, args)

        elif text.startswith("стата вся"):
            stats_all(event)

        

while True:
    # try:
    #     catch_messages()
    # except Exception as err:
    #     print(err)
    #     time.sleep(10)

    catch_messages()
        

        


    
    

    