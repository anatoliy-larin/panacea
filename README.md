django-panacea [![Build Status](https://travis-ci.org/klem4/panacea.png?branch=master)](https://travis-ci.org/klem4/panacea)
=======
django caching middleware, based on django-cacheops for using with httpredis nginx module

*In Greek mythology, Panacea (Greek Πανάκεια, Panakeia) was a goddess of Universal remedy*


Проект представляет собой приложение django, которое имеет в своем составе middleware, позволяющий средствами django-cacheops
сохранять в redis полный ответ, сгенерированный django-view, при этом, благодаря использованию [django-cacheops](https://github.com/Suor/django-cacheops "django-cacheops") , привязывать
ключ, под которым сохраняется контент к конъюнкциями заданных моделей, что дает возможность шибкой инвалидации данного кеша.
Формат ключа, под которым происходит сохранение контента в redis является "понятным" для регулярных выражений nginx, в результате
чего и происходит вторая часть магии: достовать закешированные ответы в дальнейшем сможет непосредственно nginx, благодаря модулю [HttpRedis](http://wiki.nginx.org/HttpRedis)

[django-cacheops](https://github.com/Suor/django-cacheops "django-cacheops") + [HttpRedis(Nginx)](http://wiki.nginx.org/HttpRedis) = **django-panacea**

## Установка
Последнюю стабильную версию можно поставить из pip:

`pip install django-panacea==0.1.2`

Никаких зависимостей за собой не тянет, но для работы естественно необходимо окружение в виде:
 - django >= 1.4.3
 - django-cacheops >= 1.0.0
 - django-rest-franework >= 2.3.6(на этом фреймворке я использую panacea), в теории, возможно использования любых других 
совместимых с django фреймворков, но для этого возможно потребуются небольшие доработки, связанные с получение данных из объекта
response(таких как куки, аргументы query_string и прочее, если класс объекта response далеко ушел от стандартного джанговского,
нужно будет допилить)

Полную матрицу тестирования можно посмотреть (тут)[https://github.com/klem4/panacea/blob/master/.travis.yml]

## Настройка
Для включения в работе необходимо внести изменения в *settings.py* вашего проекта:
 - Добавить panacea в список приложени: 

`INSTALLED_APPS.append('panacea')`

 - Добавить middleware в список мидлвейров(желательно поближе к началу списка, так как обратка ответа
 идет по списку мидлвейров снизу в вверх): 

`MIDDLEWARE_CLASSES.insert(0, 'panacea.middleware.NginxRedisCachingMiddleware')`

## Пример использования
Это очень простой пример, не раскрывающий всех возможностей приложения, его и еще несколько сэмплов можно увидеть при запуске тестов
тестового проекта: https://github.com/klem4/panacea/tree/master/test_project


У нас есть api, отвечающее по следующему урлу: 
`url(
        r'^api/promo/single/(?P<pk>\d+)/cache1/?$',
        views.APIPromoSingleView.as_view(),
        name='api_promo_single_cache1'
    ),`
    
И мы хотим кешировать ответы данного апи таким образом, чтобы:
 - в составлении ключа учавстсвовали: парамерт query_string с именем "custom_qs1", заголовок "HTTP_CUSTOM_META" и кука с именем "custom_cookie"
 (для любого различного сочетания этих параметров ключ будет различным, например запросы
`/api/promo/single/123456/cache1/?custom_qs1=100500` и `/api/promo/single/123456/cache1/?custom_qs1=9999` будут сохранены под разными ключами) 
 - кеш апи должен инвалидироваться при изменении(удалеии/редактировании) модели Promo, описанной в приложении test_app, при этом
 конъюнкция cacheops, в которую сохранится ключ, должна строиться на основе следующего QuerySet: 

`Promo.objects.filter(id=<параметр pk захваченный из урла>)`

Для этого, нам необходимо в settings.py нашего приложения, помимо пунктов, указанных в разделе "Настройка", разместить следующие строки:


    PCFG_ENABLED = True

    # настройки коннекта к redis, должно совпадать с cacheops
    PCFG_REDIS = CACHEOPS_REDIS
 
    PCFG_CACHING = {
        'key_defaults': {
            'GET': [],
            'META': [],
            'COOKIES': []
        },
        'key_defaults_order': ['GET', 'META', 'COOKIES'],
    
        'schemes': {
            'api_promo_single_cache1': {
                'GET': ['custom_qs1'],
                'META': ['HTTP_CUSTOM_META'],
                'COOKIES': ['custom_cookie'],
                'models': [
                    {
                        'model': 'test_app.Promo',
                        'queryset_conditions': {
                            'id': 'pk'
                        }
                    }
                ]
            }
        }
    }


Далее, на необходимо подключить в работу nginx(HttpRedis должен быть установлен). 
Если конфигурация в settings.py задана верно, то можно выполнить команду:

`./manage.py nginx_cache_conf`

В результате ее работы, на экран будет выведен готовый блок конфигурации nginx, который необходиом запнклюдить в основной конфиг nginx.
В данном случае вывод будет следующий:
location @django {include conf/django.conf; }


    location ~ "^/api/promo/single/\d+/cache1/?$" {
        set $redis_key panacea:api_promo_single_cache1:$uri:custom_qs1=$arg_custom_qs1:HTTP_CUSTOM_META=$HTTP_CUSTOM_META:custom_cookie=$cookie_custom_cookie;
        set $redis_db 1;
        redis_pass     localhost:6379;
        default_type   application/json;
        error_page     502 404 = @django;
    }


Если все сложится удачно, после перезапуска nginx и вашего сервера backend GET-запросы по данному урлу(возвращающие Content-type: application/json)
начнут кешироваться. 

Более подробное описание возможностей конфигурирования находится в следующем разделе.

## Описание конфигурации
Дефолтные настройки находяться в файле  `panacea/config.py`  и могут быть переопределены в `settings.py` вашего проекта.

Для удобства, все ключи, относящиеся к конфигурированию panacea имеют префикс `PCFG_`


#### Ключи, не относящиеся к схемам кеширования
 - `PCFG_ENABLED = False` - глобальный ребильник, если выставлен в `False`, кеширование не производится.
 - `PCFG_KEY_PREFIX = 'panacea:'` - префикс ключей, под которыми конткнт сохраняется в redis
 - `PCFG_PART_SEPARATOR = ':'` - разделитель составных частей ключа(ключ делится на несколько частей, среди которых есть постоянные, такие как
 собственно данный префикс и path(url без агрументов query-string), и опциональные, такие как: аргументы query-string, cookies, headres)
 - `PCFG_VALUES_SEPARATOR = '&'` - разделитель значений внутри какой-либо части ключа(например: если мы учитываем в ключе два парамертра
 qyery_string 'foo' и 'bar', то выглядеть эт будет так: foo=<значение>&bar=<значение>, где '&' и есть данный параметр )
 - 
 

#### Конфигурирование схем кеширования
