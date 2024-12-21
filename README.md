#Backend часть проекта NeoBitCloud

##Установка и запуск
- Установить и запустить Docker Desktop
- docker-compose up --build   
- Для работы asyncpg/psycopg2 установить "Microsoft Visual C++ 14.0 or greater is required. Get it with Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/	или https://aka.ms/vs/17/release/vc_redist.x64.exe
pip install poetry
poetry lock
poetry install
RUN main.py