use tg2_db;

drop table if exists ratings;

create table ratings (
    nm int(11) not null,
    tt int(11) not null,
    rate int(1),
    foreign key (nm) references person(nm),
    foreign key (tt) references movie(tt),
    primary key (nm, tt)
);

alter table movie
add avgrating float(2);