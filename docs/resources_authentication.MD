# Resources Authentication

Some resources, like ftp files, need authentication to get access to them. That's why tuttle provides a *.tuttlepass* file
to set a username and password to resources that need it.

## Warning
Passwords are not in the tuttlefile beacause **you should never commit your password nor authentication into your source repository**.

## .tuttlepass structure

You can set user and password to resources according to regular expressions on resources :

    ftp://ftp\.mysite\.com/lexman/.*   lexman  password
    http://download\.mysite\.com/protected/data.csv   myaccount   mypassword
    ftp://ftp\..*   me  mypassword

Any regular expression, user name and password are separated with tabulations.
The order matters, so the first regular expressions that capures the ressource defines the username and password.


## Location of .tuttlepass file

On Linux and other unix, the .tuttlepass file is at the root of the user directory (ie ~/.tuttlepass)

On Windows, the file is located at XXX

It's always possible to overwrite the .tuttlepass location by setting environnement variable TUTTLEPASSFILE.