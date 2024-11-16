# Проект парсинга статей с хабра

С этого репозитория можно брать примеры оформления
докерфайлов для python с poetry

## Настройка среды разработки

### Установка виртуального окружения

```shell
cd parser_habr
poetry install
```

Виртуальное окружение активируется с помощью команды `poetry shell`

!Введите сначала команду `env` потом активируйте окружение
и снова команду `env`. Что изменилось?

### Запуск базы для разработки

Чтобы проводить запуск приложения, нужна база данных, куда оно будет
складывать результаты своего поиска, поэтому надо запустить эту базу,
и ещё инициализировать

#### Запуск базы

```shell
docker compose -f ./docker-compose.yml -f ./docker-compose.development.yml \
  up db pgadmin -d
```

#### Инициализация базы

Должен вывести, что таблицы созданы

```shell
python -m src.init_db
```

### Запуск приложения

```shell
python -m src.main
```

## Запуск проекта в докере в разработке

#### Запуск базы

```shell
docker compose -f ./docker-compose.yml -f ./docker-compose.development.yml \
  up db pgadmin -d
```

#### Инициализация базы

Должен вывести, что таблицы созданы

```shell
docker compose -f ./docker-compose.yml -f ./docker-compose.development.yml \
  run --rm -it --build crauler python -m src.init_db
```

#### Запуск приложения

```shell
docker compose -f ./docker-compose.yml -f ./docker-compose.development.yml \
  run --rm -it --build crauler
```

Параметр --build можно убрать, если контейнер уже собран

## Запуск проекта в докере в проде

#### Запуск базы

```shell
docker compose up db pgadmin -d
```

#### Инициализация базы

Должен вывести, что таблицы созданы

```shell
docker compose run --rm -it --build crauler python -m src.init_db
```

Параметр --build можно убрать, если контейнер уже собран

#### Запуск приложения

```shell
docker compose run --rm -it --build crauler
```
