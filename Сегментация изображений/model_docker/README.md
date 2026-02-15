# Бригада 1: Сегментация объектов на изображении кастомного датасета
- Сергеев Дмитрий
- Чегодаева Елизавета
- Карпий Игорь  
Группа 0304

# Ссылки:
[Датасет](https://drive.google.com/file/d/14Qgw4F4a7T-9yMhyzlySSsfzw_8fv-lP/view)
для работы необходимо распаковать содержимое архива в директорию src/
    
[Модель](https://drive.google.com/file/d/1bXfGD-PKm6jUpu80h7bKG3qXERQp1Jpx/view?usp=sharing)
для работы необходимо поместить в директорию src/cv_pkg

# Итоговая структура директорий:
- src
    - cv_pkg
    - dataset_ready_for_yolo

# Запуск Docker-контейнера

0. Open VScode
1. `ctrl` + `shift` + `P`
2. write `devcontainer` and choose build
3. После подключения необходимо прописать `cd src/cv_pkg`

# Применение модели к тестовой выборке и вычисление метрик
`python test.py`

# Применение модели к изображению
`python inference.py`
