from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import cv2
import io
from camera import RealSenseCamera
import threading

app = FastAPI()
camera = RealSenseCamera()
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

points = []

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/video_feed")
def video_feed():
    def generate():
        camera.start()
        while camera.running:
            color_image, depth_image, _ = camera.get_frame()
            if color_image is None:
                continue
            for pt in points:
                cv2.circle(color_image, (pt["pixel"][0], pt["pixel"][1]), 5, (0, 0, 255), -1)
            _, buffer = cv2.imencode('.jpg', color_image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/click_point/")
async def click_point(x: int, y: int):
    _, _, depth_frame = camera.get_frame()
    point = camera.pixel_to_point(x, y, depth_frame)
    pt_data = {
        "pixel": [x, y],
        "world": [round(p, 3) for p in point]
    }
    points.append(pt_data)
    return pt_data

@app.get("/get_points/")
def get_points():
    return points

@app.post("/clear/")
def clear_points():
    points.clear()
    return {"status": "cleared"}

@app.post("/send/")
def send_to_server():
    # import requests
    # url = "http://YOUR_SERVER_IP:PORT/receive_coords"
    # response = requests.post(url, json={"points": points})
    # return {"status": "sent", "server_response": response.text}
    print("Send to the server")

@app.post("/exit/")
def stop_camera():
    camera.stop()
    return {"status": "stopped"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
