for x in test*
do
 (cd $x && rm *.png; ete maptrees -r reftree --source_trees genetrees --detect_duplication --debug)
done

