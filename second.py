import cv2
import mediapipe as mp
import time
import math
import csv
import os
import seaborn as sns
import plotly.express as px
import pandas as pd
import matplotlib.pyplot as plt
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from matplotlib.colors import ListedColormap

# Initialize MediaPipe Hand Detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Function to map distance to angle (0-180 degrees)
def map_distance_to_angle(distance, min_dist, max_dist, min_angle, max_angle):
    return int((distance - min_dist) * (max_angle - min_angle) / (max_dist - min_dist) + min_angle)

# CSV filenames
csv_filename = "daily_log.csv"
weekly_log_filename = "weekly_log.csv"
monthly_log_filename = "monthly_log.csv"

# Initialize log files if they don't exist
def initialize_log_file(filename, headers):
    if not os.path.exists(filename):
        with open(filename, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

initialize_log_file(csv_filename, ["Timestamp", "Angle"])  # Daily log
initialize_log_file(weekly_log_filename, ["Week", "Average Angle"])  # Weekly log
initialize_log_file(monthly_log_filename, ["Month", "Average Angle"])  # Monthly log

# OpenCV video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

logging = False
print("Press 's' to start recording for 15 seconds...")

# Display an initial frame
timeout = 15  # Logging duration in seconds
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read from camera.")
        break
    
    cv2.putText(frame, "Press 's' to start, 'q' to quit", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Hand Tracking", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        logging = True
        start_time = time.time()
        print("Logging started for 15 seconds...")
        break
    elif key == ord('q'):
        cap.release()
        cv2.destroyAllWindows()
        exit()

# Run loop for 15 seconds
while logging:
    elapsed_time = time.time() - start_time
    if elapsed_time > timeout:
        logging = False
        print("15 seconds completed. Logging stopped.")
        break

    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            h, w, _ = img.shape
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)

            cv2.line(img, (thumb_x, thumb_y), (index_x, index_y), (255, 0, 0), 3)
            cv2.circle(img, (thumb_x, thumb_y), 5, (0, 255, 0), cv2.FILLED)
            cv2.circle(img, (index_x, index_y), 5, (0, 255, 0), cv2.FILLED)

            distance = math.hypot(index_x - thumb_x, index_y - thumb_y)
            angle = map_distance_to_angle(distance, 50, 200, 0, 180)
            angle = max(0, min(180, angle))

            cv2.putText(img, f"Angle: {angle} deg", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            with open(csv_filename, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), angle])

            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        logging = False
        print("Logging stopped manually.")
        break

# Process daily average
df = pd.read_csv(csv_filename)
if not df.empty:
    df["Angle"] = df["Angle"].astype(int)
    average_angle = df["Angle"].mean()
    current_week = time.strftime("%U")
    current_month = time.strftime("%m")
    
    with open(weekly_log_filename, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([current_week, average_angle])

    with open(monthly_log_filename, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([current_month, average_angle])

    print(f"Daily average angle {average_angle} logged to weekly and monthly logs.")

# Generate heatmap with custom color scale (shades of red and orange)
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
df["Hour"] = df["Timestamp"].dt.hour
df["Minute"] = df["Timestamp"].dt.minute
df["Time Slot"] = df["Hour"].astype(str) + ":" + df["Minute"].astype(str)

# Create a custom colormap (red to orange)
custom_cmap = ListedColormap(["red", "orange"])

plt.figure(figsize=(10, 6))
sns.heatmap(df.pivot_table(index="Time Slot", values="Angle", aggfunc='mean').fillna(0), cmap=custom_cmap, annot=True)
plt.title("Angle Distribution Over Time")
plt.xlabel("Angle (in degrees)")
plt.ylabel("Timestamp (24-hour clock)")
plt.xticks(rotation=45)
plt.show()

fig = px.density_heatmap(df, x="Timestamp", y="Angle", title="Daily Log of Angle Distribution", color_continuous_scale="reds")
fig.show()

# --- Interactive Time Series with Annotations (Weekly Log) ---
weekly_df = pd.read_csv(weekly_log_filename)

# Example of annotations
annotations = [
    dict(
        x=5,  # Example week number
        y=80,  # Example average angle
        xref="x", yref="y",
        text="Significant change",  # Your annotation text
        showarrow=True,
        arrowhead=2,
        ax=0, ay=-50
    ),
    dict(
        x=10,
        y=100,
        xref="x", yref="y",
        text="Key moment",  # Another annotation text
        showarrow=True,
        arrowhead=2,
        ax=0, ay=-50
    )
]

# Create the interactive time series plot
fig = px.line(weekly_df, x='Week', y='Average Angle', title='Weekly Angle Trend')

# Add annotations
for annotation in annotations:
    fig.add_annotation(annotation)

# Show the plot
fig.show()

# --- Interactive Dashboard using Monthly Log (Dash by Plotly) ---
# Load your monthly log data
monthly_df = pd.read_csv(monthly_log_filename)

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Line chart for average angle over the months
line_chart = dcc.Graph(
    id='line-chart',
    figure=px.line(monthly_df, x='Month', y='Average Angle', title="Monthly Average Angle")
)

# Scatter plot for angle distribution over months
scatter_plot = dcc.Graph(
    id='scatter-plot',
    figure=px.scatter(monthly_df, x='Month', y='Average Angle', title="Angle Distribution by Month")
)

# Histogram for angle frequency
histogram = dcc.Graph(
    id='histogram',
    figure=px.histogram(monthly_df, x='Average Angle', title="Angle Frequency Distribution")
)

# Dropdown for month selection
month_dropdown = dcc.Dropdown(
    id='month-dropdown',
    options=[{'label': month, 'value': month} for month in monthly_df['Month'].unique()],
    value=monthly_df['Month'].iloc[0],
    multi=False
)

# Layout for the app
app.layout = html.Div([
    dbc.Row([
        dbc.Col(month_dropdown, width=4),
        dbc.Col(line_chart, width=8)
    ]),
    dbc.Row([
        dbc.Col(scatter_plot, width=6),
        dbc.Col(histogram, width=6)
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)

cap.release()
cv2.destroyAllWindows()
print("Program terminated successfully.")