-- Run this file to add sample values into the database.

insert into trees values
    (1, 'Sample Tree', 'A simple test of a tree', '2021-01-01 00:00:00.000000',
    '(B:2,(C:3,D:4)E:5)A:1;'),
    (2, 'Multinest', 'An empty-looking tree', '2021-01-01 00:00:00.000000',
    '(((((((((,),),),),),),),),);'),
    (3, 'Directories', 'From the filesystem', '2021-01-01 00:00:00.000000',
    '(boot/,dev/,etc/,(user1/,user2/)home/,(bin/,lib/)usr/,var/,tmp/)/;');
