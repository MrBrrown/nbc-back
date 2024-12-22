# Используем официальный образ Python в качестве базового
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости для Poetry
RUN pip install poetry 

# Копируем файл pyproject.toml и poetry.lock в контейнер
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости с помощью Poetry
RUN poetry env use python3.13
RUN poetry install

# Копируем все исходные файлы приложения в контейнер
COPY . .

# Открываем порт, на котором будет работать приложение
EXPOSE 8000

# Команда для запуска приложения с использованием Poetry
CMD ["poetry", "run", "python", "cli.py", "api"]
