mkdir -p grb2_files
mkdir -p g2_tar_zips

total=$(find . -maxdepth 1 -name "*.g2.tar" | wc -l)
counter=0

for file in *.g2.tar; do

  filename=$(basename "$file" .g2.tar)
  new_name="${filename#rap_130_}"
  new_name="${new_name%00}"
  new_name="${new_name:0:4}-${new_name:4:2}-${new_name:6:2}"
  mkdir "grb2_files/$new_name"

  echo "Unzipping $file..."
  tar -xf "$file" -C "grb2_files/$new_name"
  mv "$file" g2_tar_zips
  counter=$((counter+1))
  echo "... $counter out of $total files unzipped ..."

done

