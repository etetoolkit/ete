#! /usr/bin

cp -r ete_tools/ /opt/
cd /usr/local/bin
ln -s /opt/ete_tools/ete 

cd /ete/bash_completion.d/
ln -s /opt/ete_tools/ete_completion ete


