# Foodgram, «Продуктовый помощник»

### Описание проекта Foodgram:
На этом сервисе пользователи могут публиковать рецепты, подписываться на 
публикации других пользователей, добавлять понравившиеся рецепты в список 
«Избранное», а перед походом в магазин скачивать сводный список продуктов, 
необходимых для приготовления одного или нескольких выбранных блюд.

### Содержание файла .env:
```
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
```

### Запуск проекта:

#### Клонировать образ проекта:
```
https://github.com/grachevvladislav/foodgram-project-react.git
```
#### Из каталога `infra/` выполнить команду:

```
sudo docker-compose up -d
```
### Развернутый проект:
[Foodgram](http://vlad.360.ru)
admin / admin

### Разработчик проекта
- [Владислав Грачев](https://github.com/grachevvladislav)

![yamdb](https://github.com/grachevvladislav/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
