# 🖥️ Discord Remote PC Control

A multifunctional tool for remote PC management via a Discord bot. Designed for personal use, allowing you to control your computer from anywhere in the world.

### 🌟 Основні можливості
* **Файловий менеджер:** Повний доступ до файлової системи (`ls`, `cd`, `mkdir`).
* **Операції з файлами:** Завантаження з ПК, вивантаження на ПК та видалення (`rm`, `rmdir`).
* **Віддалений робочий стіл:** Скріншоти високої якості з підсвічуванням курсору.
* **Керування введенням:** Симуляція кліків, руху миші, друк тексту та натискання клавіш.
* **Спостереження:** Отримання знімків з підключеної веб-камери.
* **Збір даних:** Експорт історії браузера Google Chrome у файл `.txt`.
* **Автономність:** Автоматичне додавання в автозавантаження Windows та спроба додавання у виключення захисника.

### ⚙️ Встановлення та налаштування
1.  **Клонуйте репозиторій:**
    ```bash
    git clone [https://github.com/vash-login/nazva-repo.git](https://github.com/vash-login/nazva-repo.git)
    ```
2.  **Встановіть бібліотеки:**
    ```bash
    pip install disnake mss pyautogui opencv-python pillow
    ```
3.  **Налаштуйте бота:**
    Відкрийте `pc_bot.py` та вкажіть ваш `OWNER_ID` та `TOKEN`.
4.  **Запустіть:**
    ```bash
    python pc_bot.py
    ```

---

## 🎮 Commands / Команди

| Command / Команда | Description (EN) | Опис (UA) |
| :--- | :--- | :--- |
| `!select <pc_name>` | Start session with specific PC | Почати сесію з конкретним ПК |
| `!help` | Detailed list of all functions | Детальний список усіх функцій |
| `!ss` | Take a screenshot | Зробити скріншот екрану |
| `!ls` | View directory content | Переглянути вміст директорії |
| `!rm <file>` | Delete a specific file | Видалити конкретний файл |
| `!rmdir <folder>` | Delete a folder and its content | Видалити папку та її вміст |
| `!history` | Export Chrome history to TXT | Експорт історії Chrome у TXT |
| `!webcam` | Take a photo from webcam | Фото з веб-камери |

---

## ⚠️ Disclaimer / Відмова від відповідальності
**EN:** This tool is for educational purposes only. Unauthorized access to computer systems is illegal. The author is not responsible for any misuse.
**UA:** Цей інструмент створено виключно для освітніх цілей. Несанкціонований доступ до комп'ютерних систем є незаконним. Автор не несе відповідальності за будь-яке зловживання.
