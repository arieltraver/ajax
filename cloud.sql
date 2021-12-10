use tg2_db;

drop table if exists userKeyVal;
drop table if exists userpass;

create table userpass(
       uid int auto_increment,
       username varchar(50) not null,
       hashed char(60),
       unique(username),
       index(username),
       primary key (uid)
);

create table userKeyVal(
    username varchar(50),
    userKey varchar(60),
    userVal varchar(60),
    foreign key (username) references userpass (username)
);
