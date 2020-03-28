rm meta.yml build.sh 
git push &&
python -c 'new = open("meta.yaml.template").read().replace("%VERSION%", open("../../VERSION").readline().strip()); open("meta.yaml", "w").write(new)' &&
python -c 'new = open("build.sh.template").read().replace("%VERSION%", open("../../VERSION").readline().strip()); open("build.sh", "w").write(new)' &&
conda build --python 3.7 ./
