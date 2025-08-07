from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import cv2
import io
from camera import RealSenseCamera
import threading
import requests

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
                color = (0, 255, 0)  # green default
                if pt["color"] == "red":
                    color = (0, 0, 255)
                cv2.circle(color_image, tuple(pt["pixel"]), 6, color, -1)
            _, buffer = cv2.imencode('.jpg', color_image)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/click_point/")
async def click_point(x: int, y: int):
    _, _, depth_frame = camera.get_frame()
    point, depth = camera.pixel_to_point(x, y, depth_frame)

    # Invalid depth (z = 0)
    if depth == 0:
        pt_data = {
            "pixel": [x, y],
            "world": None,
            "color": "red"
        }
        points.append(pt_data)
        return pt_data

    # Valid point
    pt_data = {
        "pixel": [x, y],
        "world": point,     # already in mm
        "color": "green"
    }
    points.append(pt_data)
    return pt_data


@app.get("/get_points/")
def get_points():
    return [pt for pt in points if pt["world"] is not None]

@app.post("/clear/")
def clear_points():
    points.clear()
    return {"status": "cleared"}

@app.post("/send/")
def send_to_server():
    # valid_points = [pt["world"] for pt in points if pt["world"] is not None]
    # if not valid_points:
    #     return {"status": "no valid points to send"}

    # url = "http://YOUR_SERVER_IP:PORT/receive_coords"
    # response = requests.post(url, json={"points": valid_points})
    # return {"status": "sent", "server_response": response.text}
    print("Send Done")
    return {'Message': 'Send Succesfully'}

@app.post("/exit/")
def stop_camera():
    if camera.running:
        camera.stop()
    return {"status": "stopped"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
