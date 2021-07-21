-- Run this file to (re)create all the tables needed for the backend.

drop table if exists trees;
create table trees (
    id integer primary key autoincrement,
    name text unique not null,
    description text,
    birth datetime,
    newick text);
