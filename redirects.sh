cd sdoc/_build/html
(for x in `find .  -name '*.html'|cut -c 3-`;
do
    p="${x//\//\\/}";
    echo sed -i.bak \'s/CANONICALPATH/$p/\' $x;
done) > replaces.sh
sh replaces.sh
cd - 
