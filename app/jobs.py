import random
from app.models.models import Geolocation
from app.models.database import *
from sqlalchemy.sql import text

from app import scheduler


from .pwa import trigger_notifications
from geopy.geocoders import Nominatim


@scheduler.task('interval', id='check_time_10', minutes=60, misfire_grace_time=900)
def check_time_10():
    print("--- starting job 'check_time_10' ---")

    query = f"""with max_id_per_user as (
    SELECT
    e."idUser"
    ,max(e.id) max_id
    FROM event e
    group by "idUser"),

    max_event_data as (
    select
    e."createdAt"
    ,et.name event_name
    ,ABS(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP(0) - e."createdAt"))) as "timeSpent"
    ,et.category
    ,ps.*
    from max_id_per_user mipu
    inner join event as e on e.id = mipu.max_id
    inner join "eventType" as et on et.id = e."idType"
    inner join push_subscription as ps on ps.userid = mipu."idUser"
    where 1=1
    and et.category in ('Availability','Work', 'Rest')
)

select * from max_event_data WHERE "timeSpent">=36000;
    """
    query = text(query)
    session = Session()
    data = session.execute(query).all()
    session.close()
    trigger_notifications(data, "⚠️ Atividade aberta", "Lembre-se de verificar se você finalizou o timer")

    print("--- Ending job 'check_time_10' ---")


@scheduler.task('interval', id='check_time_4', minutes=60, misfire_grace_time=900)
def check_time_4():
    print("--- starting job 'check_time_4' ---")
    query = f"""with max_id_per_user as (
    SELECT 
    e."idUser"
    ,max(e.id) max_id
    FROM event e 
    group by "idUser"),

    max_event_data as (
    select 
    e."createdAt"
    ,et.name event_name
    ,ABS(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP(0) - e."createdAt"))) as "timeSpent"
    ,et.category
    ,ps.*
    from max_id_per_user mipu 
    inner join event as e on e.id = mipu.max_id
    inner join "eventType" as et on et.id = e."idType"
    inner join push_subscription as ps on ps.userid = mipu."idUser"
    where 1=1
    and et.category = 'Work'
)

select * from max_event_data WHERE "timeSpent" BETWEEN 14400 AND 21600;
    """
    query = text(query)
    session = Session()
    data = session.execute(query).all()
    session.close()

    messages = [
        {
            'title': '⏳ Por que não fazes uma pausa?',
            'body': 'Todos precisamos de recarregar energias de vez em quando.'
        },
        {
            'title': '☕ Hora do café',
            'body': 'Uma pausa sabe bem 😊'
        },
        {
            'title': '🌊 Parece que estás a precisar de um momento para relaxar.',
            'body': 'Que tal uma pausa breve?'
        },
        {
            'title': '🌿 Não te esqueças de cuidar de ti mesmo.',
            'body': 'Uma pausa é essencial para manter o equilíbrio.'
        },
        {
            'title': '🌞 O teu corpo e mente agradecerão uma pausa.',
            'body': 'Vai lá, tira uns minutos para ti.'
        },
        {
            'title': '🚶 Um intervalo curto pode fazer uma grande diferença.',
            'body': 'Vai beber um café ou dá um passeio rápido.'
        },
        {
            'title': '🧘 A concentração é importante, mas não te esqueças de descansar um pouco.',
            'body': 'Uma pausa rápida pode melhorar a tua concentração.'
        },
        {
            'title': '💡 Aproveita este momento para relaxar e recarregar baterias.',
            'body': 'Uma pausa é fundamental para manter o foco.'
        }
    ]
    selected = random.choice(messages)

    trigger_notifications(data, selected['title'], selected['body'])
    print("--- Ending job 'check_time_4' ---")


@scheduler.task('interval', id='add_address', minutes=10, misfire_grace_time=900)
def add_address():
    print("--- starting job 'add_address' ---")
    session = Session()
    locations = session.query(Geolocation).filter(Geolocation.address == None).all()
    geolocator = Nominatim(user_agent="driver_booklet")
    for location in locations:
        loc = geolocator.reverse(location.coordinates)
        if loc is not None:
            setattr(location, "address", loc.address)
            session.add(location)
            session.commit()
    session.close()
    print("--- Ending job 'add_address' ---")
