## Yatube - социальная сеть

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![SQLite](https://img.shields.io/badge/-SQLite-464646?style=flat-square&logo=SQLite)](https://www.sqlite.org/index.html)

Создан в рамках учебы в Яндекс.Практикум и представляет собой сервис, позволяющий создавать посты с изображениями. Так же посты можно объединить по тематике в группы. Например, посты на автомобильные темы или тексты про дизайн помещений и т.п. У проекта есть администраторская часть, позволяющая производить действия над постами (удалять, редактировать, создавать), а так же редактировать группы и зарегистрировавшихся участников. У авторизованных пользователей имеется возможноть подписки на определенного автора или авторов.


### Запуск проекта на локальной машине

Склонировать файлы проекта:
```
git clone https://gtihub.com/elvir906/yatube.git
```
```
cd yatube
```

Cоздать и активировать виртуальное окружение:
```
python -m venv env
```
```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

Выполнить миграции:
```
python manage.py migrate
```

Запустить проект:
```
python manage.py runserver
```
