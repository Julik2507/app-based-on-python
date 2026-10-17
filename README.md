# Diary CLI

`diary` — однопользовательская утилита командной строки для хранения заметок в SQLite.

## Установка

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

После установки доступна команда `diary`.

## Использование

Добавить заметку:

```bash
diary add "Купить продукты"
```

Вывести все заметки:

```bash
diary list
```

Удалить заметку:

```bash
diary delete 1
```

Если заметки с указанным идентификатором нет, команда выведет понятную ошибку и завершится с ненулевым кодом.

Данные сохраняются в `diary.db`, а события и ошибки — в `app.log`. Оба файла создаются в текущей рабочей директории и не добавляются в Git.

Для варианта `diary` команда `stats` не требуется.

## Тесты

Тесты дневника используют SQLite в памяти и не требуют PostgreSQL:

```bash
pytest --confcutdir=attestation_1 attestation_1/tests -q
```

## Форматирование и линтинг

```bash
ruff format --check attestation_1
ruff check attestation_1
```
