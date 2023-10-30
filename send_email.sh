#!/bin/bash

echo "========================="
cat ./Snd.0
echo "========================="

echo "attached file: "
attach=$(cat Snd.0 | grep Content-Disposition | awk -F ';' '{ print $2 }' | awk -F '=' '{ print $2 }')
echo $attach

echo "Send ? [y/N]:"
read answer

if [ "$answer" != "Y" ]; then
    echo "Abort"
    exit 0
fi

boundary="BOUNDARY"
body=$(grep -A5000 "Content-Disposition:" ./Snd.0 | tail -n +2)

# Prepare the email headers
echo "To: $(grep "To:" ./Snd.0 | sed 's/To: //')" > email.mime
echo "From: $(grep "From:" ./Snd.0 | sed 's/From: //')" >> email.mime
echo "Subject: $(grep "Subject:" ./Snd.0 | sed 's/Subject: //')" >> email.mime
echo "MIME-Version: 1.0" >> email.mime
echo "Content-Type: multipart/mixed; boundary=\"$boundary\"" >> email.mime
echo "" >> email.mime

# Add the body of the email
echo "--$boundary" >> email.mime
echo "Content-Type: text/plain; charset=\"UTF-8\"" >> email.mime
echo "Content-Transfer-Encoding: 8bit" >> email.mime
echo "" >> email.mime
echo "$body" >> email.mime
echo "" >> email.mime

# Add the attachment
echo "--$boundary" >> email.mime
echo "Content-Type: application/octet-stream; name=\"$(basename $attach)\"" >> email.mime
echo "Content-Transfer-Encoding: base64" >> email.mime
echo "Content-Disposition: attachment; filename=\"$(basename $attach)\"" >> email.mime
echo "" >> email.mime
base64 "$attach" >> email.mime
echo "" >> email.mime

# End the MIME message
echo "--$boundary--" >> email.mime

# Send the email
cat email.mime | msmtp -t -a startmail --read-recipients  --read-envelope-from 

# Clean up the temporary file
rm email.mime
