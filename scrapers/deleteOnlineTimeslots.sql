delete from Timeslot
where Timeslot.id in (
        select Timeslot.id
        from Timeslot
            left join Section on Section.id = Timeslot.section_id
        where Section.kind = 'ONL'
    )