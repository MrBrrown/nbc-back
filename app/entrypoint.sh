# Ожидание запуска PostgreSQL
while ! pg_isready -h db -p 5432 -U user; do
  echo "Waiting for postgres..."
  sleep 1
done

# Применение миграций Alembic
alembic upgrade head

# Запуск команды, переданной как аргумент
exec "$@"
