# **Project 5: Linux Server**

**by Sacha Wharton**

## **About**
This is the fifth project in the Udacity Full Stack Web Developer Nanodegree. We were required to prepare a Linux virtual machine to host a web application i.e project 4, install updates to the server, secure it from a number of attack vectors and install configure PostgreSQL as the database backend. The application is for adding books with their relevant details such as title, publisher, cover image and so forth with your favourite browser. It uses a third party login namely Google Sign-In which once signed in will then allow you to perform CRUD operations. A JSON endpoint has been provided to query book information.

- Domain Name - http://www.pangarabbit.com/
- Public IP - 13.232.129.42
- Virtual Machine - Ubuntu 16.04.5 LTS
- SSH Port - 2200

## **Required Libraries and Dependencies**

- Virtual machine hosted by AWS using their Lightsail product
- Python 2.x (The Python executable should be in your default path, which the Python installer sets)
- Flask Web Framework
- Bootstrap
- Git
- Apache2
- Your favourite browser
- A requirements.txt file has been created for all package dependencies

## **Remote Login**
- If you are using windows, I suggest installing Putty, which can be downloaded [here](https://www.putty.org/).
- I can also recommend Remote Desktop Manager Free Edition for Windows and Mac [here](https://remotedesktopmanager.com/home/download) 
which uses Putty under the hood for its SSH connections but makes managing multiple different remote connections to various
operating system flavours a dream.

- If you are using Linux, you will use SSH.

## **Project Walkthrough**

## **AWS Lightsail**
- Create an account or sign in at Amazon Web Servers [here](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fconsole.aws.amazon.com%2Fconsole%2Fhome%3Fstate%3DhashArgs%2523%26isauthcode%3Dtrue&client_id=arn%3Aaws%3Aiam%3A%3A015428540659%3Auser%2Fhomepage&forceMobileApp=0)
- Chose and instance and create the instance
- Click on: Networking and setup a static ip
- Click on: Instances
- Click on: the three little orange dots 
- Click on: Manage  
- Click on: Networking and edit the firewall rules ---> http tcp port 80 and create a custom tcp port of 2200 and remove the ssh rule
- !!!ON THE ABOVE STEP MAKE SURE YOU DO NOT LOCK YOURSELF OUT OF REMOTE CONNECTING TO YOUR INSTANCE!!!
- !!!IF YOU ARE UNSURE YOU CAN ALWAYS DO THIS LATER!!!
- SSH
- Click on: Connect
- Click on: Connect using SSH
- You will then be logged is as the Ubuntu user

## **Update and upgrade all packages**
- Updates and upgrades all packages without prompting you```sudo apt-get update && apt-get upgrade -y```
- If it asks you to be root type ```sudo -i``` and run the command again without ```sudo```

## **Create a new user named Grader and give sudoer rights**
- ```sudo adduser grader```
- ```sudo nano /etc/sudoers.d/grader```
- Add the following text ```grader ALL=(ALL:ALL) ALL```

## Set SSH Login using keys
- Generate keys on your local machine using ```ssh-keygen``
- Save the private key in ```~/.ssh``` on the local machine
- Copy and paste the public key to the AWS Lightsail instance
```
su - grader
mkdir .ssh
touch .ssh/authorized_keys
nano .ssh/authorized_keys
chmod 700 .ssh/authorized keys
chmod 644 .ssh/authorized keys
```
## **Linux**
- Use this command to access your instance remotely where ~/.ssh/* is a path to your private key on your local machine and
-i means identity file. Check this man page for more [info](https://linux.die.net/man/1/ssh)
```ssh -i ~/.ssh/"private key file"grader@13.232.129.42 -p 2200```

## **Windows** 
- If you are using putty please use the PuttyGen program to convert the key to a Putty readable identity file
- Create a file with any name and with the extension ```ppk``` e.g. key.ppk and copy the private key information to that ppk file
- In the Putty console under Session put the IP and port 2200
- Then go to SSH - Auth - Browse to your ppk file
- Click on: Open

## **Change the SSH port from 22 to 2200**
- ```sudo nano /etc/ssh/sshd_config```
- Change ```Port 22``` to 2200

## **Only allow key based authentication**
- Go to ```PasswordAuthentication``` and change it to ```no```
- Restart SSH ```sudo service ssh restart```
- !!!ON THE ABOVE STEP MAKE SURE YOU DO NOT LOCK YOURSELF OUT OF REMOTE CONNECTING TO YOUR INSTANCE!!!
- !!!IF YOU ARE UNSURE YOU CAN ALWAYS DO THIS LATER!!!

## **Uncomplicated Firewall UFW**
- Install and configure UFW
```
sudo ufw deny ssh
sudo ufw allow 2200/tcp
sudo ufw allow 80/tcp
sudo ufw allow 123/udp
sudo ufw enable
```

## **Configure the timezone to UTC**
- Run ```sudo dpkg-reconfigure tzdata``` and then choose UTC

## **Apache Web Server**
- Install Apache Web Server ```sudo apt-get install apache2```
- Install mod_wsgi ```sudo apt-get install libapache2-mod-wsgi python-dev```
- Enable mod_wsgi ```sudo a2enmod wsgi```
- Restart Apache ```sudo service apache2 restart```

## **Git and Github**
- Install Git ```sudo apt-get install git```
- Create a directory where you will store your repositories ```mkdir git```
- Clone the linuxserver git repository to your repository location  ```git clone https://github.com/sachajw/linuxserver.git```

## **PostgreSQL**
- Install PostgreSQL ```sudo apt-get install postgresql postgresql-contrib```
- Switch to the PostgreSQL super admin ```sudo -i -u postgres```
- Create PostgreSQL user ```createuser --interactive``` 
- And follow the prompts. Do not give superuser rights, create database rights or create more roles
- Create the PostgreSQL database ```createdb -O catalog bookcatalog```
- To get the application to work with PostgreSQL lines had to be changed:
- Line 41 in __init__.py ```engine = create_engine('postgresql+psycopg2://catalog:catalog@localhost/bookcatalog')```
- Line 49 in database_setup.py ```engine = create_engine('postgresql+psycopg2://catalog:catalog@localhost/bookcatalog')```
- Some extra tips:
- To switch to the bookcatalog database ```psql -d bookcatalog -U catalog```
- To drop a user ```dropuser username```
- To drop a database ```dropdb dbname```
- To check the tables of a database ```\dt```
- To quit ```\q```
- I can recommend using netcat to test if your PostgreSQL port 5432 is open to connections 
- Install netcat ```sudo apt-get install netcat```
- Test the port like this ```netcat -vz 5432``
- Navigate to database_setup.py file and run ```python database_setup.py```

## **Deploy the Flask Application**
- Navigate to ```cd /var/www```
- Create a directory ```sudo mkdir FlaskApp```
- Navigate to ```cd FlaskApp```
- Create a FlaskApp.wsgi file and add this code:
```
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/FlaskApp/")

from FlaskApp import app as application
application.secret_key = 'Add your secret key'
```
- Create a directory ```sudo mkdir FlaskApp```
- Navigate to ```cd FlaskApp```
- Copy the contents of the git repository ```cp -avr /home/grader/git/linuxserver/FlaskApp /var/www/FlaskApp/FlaskApp```
- Install Flask and all requirements ```pip install -r requirements.txt``` (this installs all the required packages)
- Configure the virtual host in Apache ```sudo nano /etc/apache2/sites-available/FlaskApp.conf```
- Add this code to FlaskApp.conf
```
<VirtualHost *:80>
                ServerName pangarabbit.com
                ServerAdmin admin@mywebsite.com
                WSGIScriptAlias / /var/www/FlaskApp/flaskapp.wsgi
                <Directory /var/www/FlaskApp/FlaskApp/>
                        Order allow,deny
                        Allow from all
                </Directory>
                Alias /static /var/www/FlaskApp/FlaskApp/static
                <Directory /var/www/FlaskApp/FlaskApp/static/>
                        Order allow,deny
                        Allow from all
                </Directory>
                ErrorLog ${APACHE_LOG_DIR}/error.log
                LogLevel warn
                CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
- Enable the virtual host ```sudo a2ensite FlaskApp```

## **Absolute Paths JSON Files**
- Made the paths absolute for access to client_secrets.json on the following lines:
- Line 47 ```open('/var/www/FlaskApp/FlaskApp/client_secrets.json', 'r').read())['web']['client_id']```
- Line 114 ```oauth_flow = flow_from_clientsecrets('/var/www/FlaskApp/FlaskApp/client_secrets.json', scope=''```

- Restart Apache ```sudo server apache2 restart```

- Browse to ****http://www.pangarabbit.com**** with your favourite browser

## **Extra Credit Description**
I have added an extra layer of security, basic analytics and performance by using Cloudflare as my DNS, CDN and security provider. Cloudflare is the first point of contact before hitting my site.

## **Miscellaneous**
I based the README on this template [forum](https://discussions.udacity.com/t/readme-files-in-project-1/23524)
