<h1>Установка</h1>
<h2>Создание токена и редактирование config.py</h2>
<p>Создаём токен с разрешениями на сообщество, сообщения и изображения. Включаем longpoll api и ставим там тип эвентов входящие сообщения. Заполняем config.py</p>

<h2>Создание и запуск виртуального окружения</h2>
<p>python -m venv venv</p>
<p>Linux: source venv/bin/activate | Windows: venv/scripts/activate</p>

<h2>Установка библиотек</h2>
<p>pip install -r requirements.txt</p>

<h2>Запуск</h2>
<p>python src/main.py</p>


<h1>Команды</h1>
<p>профиль (упоминание - опционально) - показывает личную статистику за сутки</p>
<p>стата вся - показывает всю статистику сообщений и график актива за месяц</p>
<p>стата - показывает статистику за сутки</p>