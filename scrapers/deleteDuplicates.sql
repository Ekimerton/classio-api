-- SQLite
select *
from Timeslot
where id not in (
        select min(Timeslot.id)
        from Timeslot
        group by day,
            start_time,
            end_time,
            section_id
    )