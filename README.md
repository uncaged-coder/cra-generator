This is a very simple python script that generate "activity report" (CRA in french).
Every month I have to fill the pdf, and sign it then send an email to my customer to make him sign it.
This is a boring task that can be automated.
If you want to do the same:
- update cra_model.pdf: this is a template pdf that will then be filled
- update the python file cra_generator.py: If you didn't work some days you have to update holidays variable.
Sunday and Saturday are already counted as not working days.
- update snd_template: this is the email template

then you can run:
```
> python cra_generator.py: this will generate cra_.pdf
```

this will generate a file:
cra_2023_10.pdf : (for october 2023 activity)

Check the generated file.

then run:
```
> bash send_email.sh
```
this will send the email with the "activity report" attached.
