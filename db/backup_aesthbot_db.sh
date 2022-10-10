#!/bin/bash
echo "******** RUN WITH 'SUDO' ********"
now=$(date +'%m-%d-%Y')
outputfile="aesthbotDB_[${now}].sql"
echo "Saving to ${outputfile}"
mysqldump -u root -p aesthetic-bot --skip-add-drop-table --skip-add-locks --no-create-info --replace > $outputfile
#sed -i 's/INSERT/INSERT IGNORE/g' $outputfile 
