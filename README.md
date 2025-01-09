# Система учета нарядов

Приложение для учета и анализа производственных нарядов с возможностью прогнозирования производительности цехов.

## Возможности

- Управление нарядами (добавление, редактирование, удаление)
- Анализ количества нарядов по периодам
- Оценка производительности цехов
- Анализ трудоемкости операций
- Прогнозирование производительности цехов

## Системные требования

- Windows 7/8/10/11 (64-bit) или Linux (Ubuntu 18.04+, 64-bit)
- Свободное место на диске: 200 МБ
- Разрешение экрана: минимум 800x600

## Установка

### Простая установка (для пользователей)

1. Перейдите на страницу [Releases](ссылка_на_релизы)
2. Скачайте версию для вашей операционной системы:
   - Windows: `naryad-windows.exe`
   - Linux: `naryad-linux`
3. Запустите скачанный файл:
   - Windows: двойной клик по .exe файлу
   - Linux: 
     ```bash
     chmod +x naryad-linux
     ./naryad-linux
     ```

### Сборка из исходного кода (для разработчиков)

#### Ubuntu
1. Установка зависимостей:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git
   ```

2. Клонирование репозитория:
   ```bash
   git clone https://github.com/username/naryad.git
   cd naryad
   ```

3. Создание виртуального окружения:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Установка Python-зависимостей:
   ```bash
   pip install -r requirements.txt
   ```

5. Сборка программы:
   ```bash
   pyinstaller naryad.spec
   ```

#### Windows
1. Установка необходимого ПО:
   - Python 3.x с python.org
   - Git с git-scm.com
   - При установке Python отметьте "Add Python to PATH"

2. Клонирование репозитория:
   ```cmd
   git clone https://github.com/username/naryad.git
   cd naryad
   ```

3. Создание виртуального окружения:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

4. Установка Python-зависимостей:
   ```cmd
   pip install -r requirements.txt
   ```

5. Сборка программы:
   ```cmd
   pyinstaller naryad.spec
   ```

Готовые файлы после сборки находятся в папке `dist`.

## Использование

### Вкладка "Данные"

- Заполните форму данными наряда
- Используйте кнопки для управления записями:
  - "Добавить" - создание новой записи
  - "Обновить" - изменение выбранной записи
  - "Удалить" - удаление выбранной записи
  - "Очистить" - очистка формы

### Вкладка "Аналитика"

- Выберите период для анализа (День/Месяц/Год)
- Выберите цех для просмотра прогноза производительности
- Изучите графики:
  - Количество нарядов по периодам
  - Производительность цехов
  - Трудоемкость операций
  - Прогноз производительности выбранного цеха

## Структура проекта

- `main.py` - основной файл приложения с GUI
- `database.py` - модуль для работы с базой данных
- `analytics.py` - модуль для анализа и визуализации данных
- `requirements.txt` - список зависимостей
- `naryad.db` - файл базы данных SQLite (создается автоматически)
