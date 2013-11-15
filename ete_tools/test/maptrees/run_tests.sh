for x in test*
do
 (cd $x && rm *.png; ete maptrees -r reftree --source_trees genetrees -o annotated_reftree --debug)
done

