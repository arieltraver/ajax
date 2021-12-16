use tg2_db;

drop table if exists userKeyVal;
drop table if exists userpass;

create table userpass(
       username varchar(50) not null,
       hashed char(60),
       unique(username),
       index(username),
       primary key (username)
);

create table userKeyVal(
    username varchar(50),
    userKey varchar(60),
    userVal varchar(60),
    foreign key (username) references userpass (username),
    primary key (username, userKey)
);
