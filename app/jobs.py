from app import scheduler
from app.models.models import *
from app.models.database import *
from sqlalchemy.sql import text
from .pwa import trigger_notifications
from flask_login import current_user, login_required

@scheduler.task('interval', id='check_time', seconds=10, misfire_grace_time=900)
def check_time():
    query = f"""with max_id_per_user as (
    SELECT 
    e.idUser
    ,max(e.id) max_id
    FROM `event` e 
    group by idUser),

    max_event_data as (
    select 
    e.eventTime
    ,et.name event_name
    ,TIMESTAMPDIFF(SECOND,curdate(),e.eventTime) as timeSpent
    ,et.category
    ,ps.*
    from max_id_per_user mipu 
    inner join event as e on e.id = mipu.max_id
    inner join eventType as et on et.id = e.idType
    inner join push_subscription as ps on ps.userid = mipu.idUser
    where 1=1
    and et.category in ('Availability','Work')
    and et.name like '%_start'
) 

select * from max_event_data WHERE timeSpent>=36000;
    """
    query = text(query)
    session = Session()
    data = session.execute(query).all()
    session.close()
    trigger_notifications(data, "Timer is open.", "remember to close the timer if you aren't using it.")

#test function
@scheduler.task('interval', id='test_push_login', seconds=10, misfire_grace_time=900)
def test_push_login():
    session = Session()
    data = session.query(PushSubscription).filter(
    PushSubscription.userId == 7).first()
    trigger_notifications([data], "you are logged", "hahahahahahahahah")