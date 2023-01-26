base_url=$1
curl -s $base_url | 
grep -o '<a .*href=.*g2\.tar.*>' | 
sed -e 's/^.*href="\([^"]*\)".*$/\1/' | 
head -n 1 | 
xargs -I {} echo $base_url{} |
xargs wget -nc 
mkdir -p grb2_files
filename=$(echo *.g2.tar)
tar -xvf $filename -C grb2_files