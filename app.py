import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
import base64
from datetime import datetime, timedelta, time
import pandas as pd

APP_TITLE = "Le Wagon Cab"
st.set_page_config(APP_TITLE)

#url = "https://mycolor.space/gradient?ori=to+right+top&hex=%23051937&hex2=%23A8EB12&sub=1"


def get_prediction(pickup_datetime, pickup_longitude: float,
                   pickup_latitude: float, dropoff_longitude: float,
                   dropoff_latitude: float, passenger_count: int) -> float:
    url = 'https://le-petite-wagon-f4hdpssb7a-ew.a.run.app/'
    key = ["2009-06-15 17:26:21.0000001"]
    data = {
        "key": key,
        "pickup_datetime": pickup_datetime,
        "pickup_latitude": pickup_latitude,
        "pickup_longitude": pickup_longitude,
        "dropoff_latitude": dropoff_latitude,
        "dropoff_longitude": dropoff_longitude,
        "passenger_count": passenger_count
    }
    try:
        fare_prediction = requests.get(url, params=data)
        if fare_prediction.status_code == 200:
            return fare_prediction.json().get("fare")
    except requests.exceptions.RequestException:
        return "Woops! Server is busy!"


@st.experimental_memo
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


## get images

bg_img = get_img_as_base64("images/image.jpg")
side_img = get_img_as_base64("images/lewagon.png")

st.markdown(f"""<style>
    [data-testid="stHeader"]{{
        background-color: rgba(0,0,0,0);
    }}
    [data-testid="stMarkdownContainer"]{{
        font-size:large;
        font:20px;
        font-family:Comic Sans MS;
        color:white;
        background-position: top center;
        text-align: center;
    }}


    button {{
        background-color:red !important;
        opacity:0.9;
    }}

    #map_div{{
            background-color:red;
    }}
    [data-testid="stSidebar"]{{
        background-image: url("data:image/jpg;base64,{side_img}");
        background-position: center;
        background-repeat: no-repeat;
        background-position: bottom center;
        background-color:black;
        opacity:0.90;
        padding-bottom: 10%;
        background: repeating-linear-gradient();
    }}
    .title {{
        margin-top:-100px;
        margin-bottom:-100px;
        font-size:50px;
        color:white;
    }}
    .info {{
        margin-top:-100px;
    }}
    [data-testid="stForm"]{{
        background-color:black;
        opacity:0.98;
        background:linear-gradient(to right top, #051937, #004d7a, #008793, #00bf72, #a8eb12);
    }}


    [data-testid="stAppViewContainer"]
    {{
        background-image: url("data:image/jpg;base64,{bg_img}");
        background-position: center;
        background-repeat: no-repeat;
        background-size:cover;
        }}
    </style>""",
            unsafe_allow_html=True)

if 'clicks' not in st.session_state:
    st.session_state['clicks'] = 0

if "message" not in st.session_state:
    st.session_state["message"] = "Select Pickup Location"


def location_callback(position):
    if st.session_state["clicks"] == 3:
        st.session_state["clicks"] = 0
        del st.session_state["message"]

    if position:
        st.session_state["clicks"] += 1
        if st.session_state["clicks"] == 1:
            st.session_state["pickup_latitude"] = position.get("lat")
            st.session_state["pickup_longitude"] = position.get("lng")
            st.session_state["message"] = "Select Dropoff Location"
        elif st.session_state["clicks"] == 2:
            st.session_state["dropoff_latitude"] = position.get("lat")
            st.session_state["dropoff_longitude"] = position.get("lng")
            st.session_state["message"] = "Click again to predict!"
    elif st.session_state["clicks"] == 2:
        st.session_state["clicks"] += 1
        st.session_state["message"] = "Refresh!"


def display_map():
    map = folium.Map(location=[40.730610, -73.935242],
                     tiles='OpenStreetMap',
                     scrollWheelZoom=True)
    if st.session_state["clicks"] == 1:
        pickup_latitude = st.session_state["pickup_latitude"]
        pickup_longitude = st.session_state["pickup_longitude"]
        folium.Marker(location=[pickup_latitude, pickup_longitude],
                      popup="pickup coordinates",
                      icon=folium.Icon(color='blue')).add_to(map)
    if st.session_state["clicks"] in [2, 3]:
        pickup_latitude = st.session_state["pickup_latitude"]
        pickup_longitude = st.session_state["pickup_longitude"]
        dropoff_latitude = st.session_state["dropoff_latitude"]
        dropoff_longitude = st.session_state["dropoff_longitude"]

        folium.Marker(location=[pickup_latitude, pickup_longitude],
                      popup="pickup coordinates",
                      icon=folium.Icon(color='blue')).add_to(map)
        folium.Marker(location=[dropoff_latitude, dropoff_longitude],
                      popup="dropoff coordinates",
                      icon=folium.Icon(color='blue')).add_to(map)
        folium.PolyLine([[pickup_latitude, pickup_longitude],
                         [dropoff_latitude, dropoff_longitude]],
                        color="red",
                        weight=10).add_to(map)
    return map


def main():
    st.markdown("<div class='title'> Le Petite Wagon </span>",
                unsafe_allow_html=True)
    st.markdown(
        "Now travel anywhere with Le Petite Wagon Cab and get your fare price NOW!"
    )

    with st.sidebar:
        st.markdown("""Choose your features: """)
        passenger_count = st.selectbox("Passengers", options=range(1, 9))
        pickup_date = st.date_input("Pickup date", datetime(2022, 11, 23))
        pickup_time = st.slider("Pickup Datetime",
                                min_value=time(6, 0),
                                value=time(2, 0),
                                max_value=time(0, 0),
                                format="h:mm:ss a")
        pickup_datetime = datetime.combine(pickup_date,pickup_time)\
                                  .strftime("%Y-%m-%d %H:%M:%S")

    st.markdown("Choose your dropoff and pickup locations: ")
    if st.session_state["clicks"] == 3:
        pickup_latitude = st.session_state["pickup_latitude"]
        pickup_longitude = st.session_state["pickup_longitude"]
        dropoff_latitude = st.session_state["dropoff_latitude"]
        dropoff_longitude = st.session_state["dropoff_longitude"]

        predicted_fare = get_prediction(pickup_latitude=pickup_latitude,
                                        pickup_longitude=pickup_longitude,
                                        dropoff_latitude=dropoff_latitude,
                                        dropoff_longitude=dropoff_longitude,
                                        passenger_count=passenger_count,
                                        pickup_datetime=pickup_datetime)
        if isinstance(predicted_fare, float):
            st.balloons()
            st.success(f"Estimated Fare Amount: {predicted_fare:.2f}€")
        else:
            st.warning("Woooops! Something went wrong...")



    folium_map = display_map()
    with st.container():
        map = st_folium(folium_map, width=1000, height=500)

    position = map.get("last_clicked")
    col , _ , _ , _ = st.columns(4)
    with col:
        location = st.button(st.session_state["message"],
                             on_click=location_callback,
                             args=(position, ))




if __name__ == "__main__":
    main()
