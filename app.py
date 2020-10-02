import requests
from flask import Flask,render_template, request, redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'thisisasecret***MANPUR'
db= SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city=db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return '<Task %r>' %self.id

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid=a167d6220a6c9250e8601bcf2372061e'
    r = requests.get(url).json()
    return r 

@app.route('/',methods=['GET'])
def index_get():
    cities = City.query.all()
    
    weather_data=[]

    for city in cities:
        r = get_weather_data(city.city)
        weather={
        'city': city.city, 
        'temperature': r['main']['temp'], 
        'description':r['weather'][0]['description'], 
        'icon': r['weather'][0]['icon']
        }
        weather_data.append(weather)
    return render_template('weather.html', weather_data=weather_data)




@app.route('/',methods=['POST'])
def index_post():
    err = ''
    new_city = request.form.get('city')
    if new_city:
        existing_city = City.query.filter_by(city=new_city).first()
        if not existing_city:
            new_city_data = get_weather_data(new_city)
            if new_city_data['cod'] ==200:
                new_city_obj = City(city=new_city)

                try:
                    db.session.add(new_city_obj)
                    db.session.commit()
                except:
                    return "There is an issue"
            else:
                err = 'City does not exist'
        else:
            err = 'City already exist'
    if err:
        flash(err,'error')
    else:
        flash('city added successfully')
    return redirect(url_for('index_get'))

@app.route('/delete/<city>')
def delete_city(city):
    city_del = City.query.filter_by(city=city).first()
    try:
        db.session.delete(city_del)
        db.session.commit()
    except:
        return "delete error"
    flash(f'successfully deleted{city_del.city}','success')
    return redirect(url_for('index_get')) 


if __name__=='__main__':
    app.run(debug=True)