#! /bin/sh


if [ $# -ne 2 ]
then
echo "Not enough arguments. \nuse $0 repos_source outpath"
exit
fi


REPOSITORY=$1
BRANCH=2.0
REVISION=`cd $REPOSITORY; git log --pretty=format:'' | wc -l;`
VERSION=$BRANCH\rev$REVISION
MODULE_NAME=ete2
PKG_NAME=ete$VERSION
OUTPATH=$2/$PKG_NAME


echo "Source repos : $REPOSITORY"
echo "Output pkg   : $OUTPATH"
echo "Pkg. Version : $VERSION"
echo "Module name  : $MODULE_NAME"


# removes repository info
if  [ -e $OUTPATH ]; then
    OVERRIDE='n'
    while [ $OVERRIDE != 'y' ]; do
	echo "$OUTPATH already exists. Override? [y|n]"
	read OVERRIDE
    done
fi 


rm $OUTPATH/ -rf
git clone $REPOSITORY $OUTPATH/
rm $OUTPATH/.git/ -rf

# mv 
mv $OUTPATH/pygenomics $OUTPATH/$MODULE_NAME

# Ccorrect imports
find $OUTPATH -name *.py| xargs perl -e "s/from pygenomics/from $MODULE_NAME/g" -p -i 

# Set VERSION in all modules
find $OUTPATH/ete2/ -name '*.py' |xargs sed "1 i __VERSION__=\"$VERSION\""  -i

echo $VERSION > $OUTPATH/VERSION

# Add Copyright and License
# ...


