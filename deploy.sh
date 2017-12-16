#! /bin/sh
SERVER=guran.krats.se
PROJECT=fandjango
VERSION=$1
REPO='git@github.com:kaj/fandjango.git'
PROJROOT=/usr/web/deploy/$PROJECT
DESTDIR=$PROJROOT/$VERSION

if [ ! -n "$PROJECT" -o ! -n "$VERSION" ]; then
    echo "Usage"
    echo "$0 version"
    exit
fi
echo "Should deploy $PROJECT version $VERSION"

ssh $SERVER <<EOF
set -e
if [ -d $DESTDIR ]; then
  echo "$DESTDIR already exists. Stop."
  exit 1
fi
cd $PROJROOT
# Checking out "master", but to a directory named $VERSION
git clone -b master $REPO $VERSION
cd $VERSION
pyvenv-3.6 --system-site-packages ve
. ve/bin/activate
pip install -r requirements.txt
cp /usr/web/$PROJECT/settings/local.py settings/
./manage.py collectstatic --no-input
ln -s $PROJROOT/covers/* static
./manage.py fetchcovers
cd /usr/web
rm $PROJECT
ln -sf $DESTDIR $PROJECT
EOF
