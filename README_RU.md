# CryptoSalesBot

### Обзор
CryptoSalesBot — это Telegram-бот для отслеживания сделок с криптовалютой, который отправляет уведомления о транзакциях, соответствующих заданным критериям. Бот интегрируется с API для получения данных о сделках и отправляет подробные уведомления в Telegram, включая графику, основанную на объеме сделок.

### Особенности
- Отслеживание сделок через API в реальном времени.
- Отправка деталей сделок с кастомными анимациями на основе объема сделки.
- Обработка flood control для избежания ограничений Telegram.
- Поддержка команд для управления ботом.

### Установка
1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Настройте бота:
   - Укажите `token` и `chat_id` в скрипте.
   - Обновите `API_URL` для указания API-эндпоинта для получения данных.

4. Запустите бота:
   ```bash
   python cryptosalesbot.py
   ```

### Команды
- `/startsales` - Запустить отслеживание сделок с криптовалютой.
- `/restartsales` - Перезапустить бота и очистить предыдущие задачи.
- Отправьте "ca" - Получить контрактный адрес токена.

### Требования
- Python 3.8+
- Библиотеки (указаны в `requirements.txt`):
  - `urllib3`
  - `python-telegram-bot`
  - `asyncio`