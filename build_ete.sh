#! /bin/sh
BRANCH=2.0
REVISION=`git log --pretty=format:'' | wc -l`
VERSION=$BRANCH\rev$REVISION
MODULE_NAME=ete2
PKG_NAME=ete$VERSION

cd ..
echo "git clone pygenomics $PKG_NAME/"
rm $PKG_NAME/ -rfi
git clone pygenomics $PKG_NAME/
cd $PKG_NAME
rm .git/ -rf
mv pygenomics $MODULE_NAME
ls -lat
find . -name *.py| xargs perl -e "s/from pygenomics/from $MODULE_NAME/g" -p -i 
