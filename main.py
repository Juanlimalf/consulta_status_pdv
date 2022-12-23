
import uvicorn


if __name__ == "__main__":
    uvicorn.run("routes.routes:app", host="0.0.0.0", port=8005, log_level="info")
