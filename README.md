# TrainingAPP
Workout Diary APP made on Flask


<!-- ABOUT THE PROJECT -->
## About The Project
Welcome! This is my first Flask project. It is a web application to scheduling yor workouts. I used modifided by me Mobiscroll Calendar with all CRUD functions. Enjoy!


### Functions
* Registartion on the site
* Activtion code is sended via email, is valid 30 minutes
* Full password recovery by token
* Password changing
* Account delete
* CRUD Calendar (Create, Read, Update, Delete)
### Stack

* Python3
* Flask
* Mobiscroll Calendar (https://demo.mobiscroll.com/eventcalendar/create-read-update-delete-CRUD)
* Google ReCapatcha (https://www.google.com/recaptcha/about/)
* Gmail

<!-- How to install -->
## How to instal:
Clone repository from GitHub or download it. 

Install extra libraries from requirements.txt.
Open your terminal in project folder and type:

  ```sh
  pip install -r requirements.txt
  ```
  

Creating global database:
  ```sh
  from app import db, app
  db.create_all(app=app)
  ```
  
  
  

## User settings:

### Sending emails :
My program is able to send activations code on emails. First you need to create evironment variables to keep your data safe.

I recommend this Corey's video how to do that on Windows, Mac and Linux. (https://www.youtube.com/watch?v=IolxqkL7cD8)

In my code i created variables "EMAIL_PASS" and "EMAIL_USER". You can name it however you like, but you need to sure, that variables are named the same in python and your OS.

![projektpng](https://user-images.githubusercontent.com/79137973/117843451-1c47f280-b27f-11eb-80c4-f00416d67cca.png)


## Activating ReCaptcha:

I used ReCaptcha to prevent my site from bots. First you need to register your site on Google and get keys from them.



  
  


<!-- CONTACT -->
## Contact

Sebastian Szymański - shadow.smoke7@gmail.com

