#! /bin/sh

if [ $# -ne 2 ]; then
    echo "Not enough arguments. \nuse $0 repos_source outpath"
    exit
fi

REPOSITORY=$1
BRANCH=2.0
REVISION=`cd $REPOSITORY; git log --pretty=format:'' | wc -l;`
VERSION=$BRANCH\rev$REVISION
MODULE_NAME=ete2
PKG_NAME=ete-$VERSION
OUTPATH=$2/$PKG_NAME


echo "Source repos : $REPOSITORY"
echo "Output pkg   : $OUTPATH"
echo "Pkg. Version : $VERSION"
echo "Module name  : $MODULE_NAME"

echo "Last commited changes in package:"
echo "----------------------------------"
cd $REPOSITORY; git log --pretty=format:"%cr %s" |head
cd ..
echo 
echo


# Continue?
if  [ -e $OUTPATH ]; then
    OVERRIDE='n'
    while [ $OVERRIDE != 'y' ]; do
       echo "Go ahead? [y|Ctrl-C]"
       read OVERRIDE
    done
fi

# removes repository info
if  [ -e $OUTPATH ]; then
    OVERRIDE='n'
    while [ $OVERRIDE != 'y' ]; do
       echo "$OUTPATH already exists. Override? [y|Ctrl-C]"
       read OVERRIDE
    done
fi

rm $OUTPATH/ -rf
git clone $REPOSITORY $OUTPATH/
rm $OUTPATH/.git/ -rf

cd $OUTPATH/
python unittest/test_all.py
cd ..


# mv
#mv $OUTPATH/pygenomics $OUTPATH/$MODULE_NAME

# Ccorrect imports
#find $OUTPATH -name '*.py'| xargs perl -e "s/from pygenomics/from $MODULE_NAME/g" -p -i


# Set VERSION in all modules
find $OUTPATH/ete2/ -name '*.py' |xargs sed "1 i __VERSION__=\"$VERSION\""  -i
#find $OUTPATH/ete2/ -name '*.py' |xargs sed "1 i #__DISCLAMER___"  -i


echo $VERSION > $OUTPATH/VERSION
tar -zcf ./$PKG_NAME.tgz $OUTPATH

echo "Copy pkg. to cgenomics server? [y|Ctrl-C]"
read COPY
if [ $COPY = 'y' ]; then
    scp ./$PKG_NAME.tgz jhuerta@cgenomics:/home/services/web/ete.cgenomics.org/releases/ete2/
    ssh cgenomics  'cd /home/services/web/ete.cgenomics.org/releases/ete2/; sh update_downloads.sh'
fi
# Add Copyright and License
# ...
