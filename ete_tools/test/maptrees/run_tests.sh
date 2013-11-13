for x in test*
do
 (cd $x && rm *.png; ete maptrees -r reftree --source_trees genetrees --output annotated_reftree.pkl --debug)
done

