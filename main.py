from flask import Flask, render_template, request
import numpy as np
import pickle
from dateutil.relativedelta import relativedelta
from datetime import datetime

app = Flask(__name__)

def load_model():
    with open('model/saved_steps.pkl', 'rb') as file:
        data = pickle.load(file)
    return data

data = load_model()
model = data["model"]
le_area = data["le_area"]
le_vehicle = data["le_vehicle"]
le_jenis = data["le_jenis"]

Area = (
 'BAU-BAU', 'BONE', 'BULUKUMBA', 'GOWA', 'KENDARI', 'KOLAKA',
 'LUWUK BANGGAI', 'MAKASSAR', 'MALILI', 'MAMUJU', 'MAROS',
 'PALOPO', 'PALU', 'PARE-PARE', 'POLMAN', 'POSO', 'SENGKANG',
 'SIDRAP', 'SOPPENG', 'TATOR'
)

Vehicle = (
 'AGYA', 'ALPHARD', 'AVANZA', 'C-HR', 'CALYA', 'CAMRY', 'COROLLA',
 'DYNA', 'ETIOS', 'FORTUNER', 'FT 86', 'HARRIER', 'HIACE', 'HILUX',
 'INNOVA', 'KIJANG', 'LANDCRUISER', 'LIMO', 'NAV1', 'RAIZE', 'RUSH',
 'SIENTA', 'VELLFIRE', 'VELOZ', 'VIOS', 'VOXY', 'YARIS', 'Other'
)

Jenis = ('Basah', 'Kering')

def mileage(x):
    if x >= 105000:
        return 21 + (x - 105000) // 5000
    else:
        return min(x // 5000, 21)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Ambil data dari form
        Area_input = request.form["area"]
        Vehicle_input = request.form["vehicle"]
        CMR = int(request.form["cmr"])
        Age = int(request.form["age"])
        Jenis_input = request.form["jenis"]
        delivery_date = request.form["delivery_date"]

        # Proses prediksi
        X = np.array([[Area_input, Vehicle_input, CMR, Age, Jenis_input]])
        X[:, 0] = le_area.transform(X[:, 0])
        X[:, 1] = le_vehicle.transform(X[:, 1])
        vectorized_mileage = np.vectorize(mileage)
        X[:, 2] = vectorized_mileage(X[:, 2].astype(int))
        X[:, 4] = le_jenis.transform(X[:, 4])
        X = X.astype(int)

        Rentang = model.predict(X)
        Rentang = np.abs(np.round(Rentang)).astype(int)

        delivery_date = datetime.strptime(delivery_date, "%Y-%m-%d")
        months_to_add = Rentang[0]

        replacement_dates = []
        current_date = datetime.now()
        while delivery_date <= current_date:
            replacement_dates.append(delivery_date.strftime('%Y-%m-%d'))
            delivery_date += relativedelta(months=months_to_add)

        future_replacement_dates = []
        while delivery_date <= current_date + relativedelta(months=months_to_add):
            future_replacement_dates.append(delivery_date.strftime('%Y-%m-%d'))
            delivery_date += relativedelta(months=months_to_add)

        # Kirimkan kembali nilai input ke template
        return render_template("index.html", 
                               replacement_dates=replacement_dates, 
                               future_replacement_dates=future_replacement_dates,
                               months_to_add=months_to_add,
                               areas=Area, 
                               vehicles=Vehicle, 
                               jenis_batteries=Jenis,
                               selected_area=Area_input,
                               selected_vehicle=Vehicle_input,
                               entered_cmr=CMR,
                               entered_age=Age,
                               selected_jenis=Jenis_input,
                               entered_delivery_date=request.form["delivery_date"])

    return render_template("index.html", 
                           areas=Area, 
                           vehicles=Vehicle, 
                           jenis_batteries=Jenis)
if __name__ == "__main__":
    app.run(debug=True)