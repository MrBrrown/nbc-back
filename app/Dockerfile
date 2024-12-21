#TODO Dockerfile for API
# Используем официальный образ Python
FROM python:3.13

# Устанавливаем рабочую директорию
WORKDIR /
RUN echo "Before ls"
RUN echo "After ls"
#
## Копируем requirements.txt и устанавливаем зависимости
#COPY pyproject.toml .
#COPY poetry.lock .
##COPY pyproject.toml  .
#RUN pip install poetry
#RUN poetry config virtualenvs.create false
#RUN poetry install --no-interaction --no-root
# Копируем остальные файлы проекта

RUN pwd
COPY ../ .
RUN ls -al
#COPY api/entrypoint.sh /app/entrypoint.sh
#RUN chmod +x /app/entrypoint.sh

 # Используем ENTRYPOINT
#ENTRYPOINT ["/app/entrypoint.sh"]


# Команда для запуска приложения
#CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]