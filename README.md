# IT490-Project
We want to make a web application that will tell you what room 
is available and at what time the next room will be free. 
The library at NJIT doesn’t have a system that can tell you the
schedule so, our web app will show the rooms schedule and when the
 next room will be available. This way students don’t have to wait 
for hours in line. Users can login, register/reserve the next available
 room and will have a chat feature that users can chat with the librarian
 if they have any questions/comments.


#############################
First Login:
 Student Regitraion
 or
 Librarian Regigration
* Both have different accessiblity.

Login Page is the same. Once Registered successfully, you will be brought to the
login page once you click the "OK" on thr prompt. 
Depending on who you registered as, you will be brought to the correct web page to
view the rooms and messaging.


#############################
# For Build

cd flask_backend/
docker-compose build

cd ../flask_frontend/
docker-compose build

cd ..

# For Run

docker-compose up
##############################
