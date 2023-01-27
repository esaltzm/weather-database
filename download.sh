total=$(wc -l < "files.txt")
counter=1
for file in `cat files.txt`; do
    echo downloading $file "(...$counter / $total...)";
    curl https://www1.ncdc.noaa.gov/pub/has/model/HAS012347676/$file > /Volumes/Untitled/$file;
    counter = $((counter+1))
done
