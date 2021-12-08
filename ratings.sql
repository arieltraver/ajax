use tg2_db;

drop table if exists ratings;

create table ratings (
    uid int(11) not null,
    tt int(11) not null,
    rate int(1),
    foreign key (uid) references staff(uid),
    foreign key (tt) references movie(tt),
    primary key (uid, tt)
);

alter table movie
add avgrating float(2);