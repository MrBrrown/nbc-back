FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /

# Устанавливаем зависимости для Poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry && \
    apt-get remove -y curl && apt-get autoremove -y

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
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]