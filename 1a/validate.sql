-- Prints a problem count for each check. Every count should be 0.
.headers on
.mode column
PRAGMA foreign_key_check;
PRAGMA integrity_check;

SELECT 'cabin counter drift' AS check_name, COUNT(*) AS problems FROM Cabin C
WHERE C.c_current_size <> (SELECT COUNT(*) FROM Passenger P WHERE P.p_cabin_id = C.c_cabin_id)
UNION ALL
SELECT 'excursion counter drift', COUNT(*) FROM Excursion X
WHERE X.ex_current_size <> (SELECT COUNT(*) FROM Books_Excursion B WHERE B.ex_excursion_id = X.ex_excursion_id)
UNION ALL
SELECT 'event counter drift', COUNT(*) FROM Event E
WHERE E.ev_current_size <> (SELECT COUNT(*) FROM RSVPs_Event R WHERE R.ev_event_id = E.ev_event_id)
UNION ALL
SELECT 'venue over capacity', COUNT(*) FROM (
    SELECT A.dv_venue_id, A.reservation_time
    FROM (SELECT DISTINCT dv_venue_id, reservation_time FROM Reserves_Dining) A
    JOIN Reserves_Dining B ON B.dv_venue_id = A.dv_venue_id
     AND B.reservation_time <= A.reservation_time
     AND datetime(B.reservation_time, '+90 minutes') > A.reservation_time
    JOIN Dining_Venues V ON V.dv_venue_id = A.dv_venue_id
    GROUP BY A.dv_venue_id, A.reservation_time, V.dv_capacity
    HAVING SUM(B.party_size) > V.dv_capacity
);
