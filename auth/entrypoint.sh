#!/bin/sh

# Ініціалізуємо базу даних
python database.py

# Запускаємо Flask-додаток
exec python main.py

