import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/v2/job_templates/{template_id}/launch/")
async def launch_job_template(template_id: int, request: Request):
    await asyncio.sleep(1)  # Simulate job creation delay
    return JSONResponse(
        status_code=201,
        content={"id": 123, "status": "pending", "template_id": template_id},
    )

@app.post("/api/v2/inventories/")
async def create_inventory(request: Request):
    data = await request.json()
    return JSONResponse(
        status_code=201,
        content={"id": 456, "name": data.get("name"), "organization": 1},
    )

@app.get("/api/v2/jobs/{job_id}/")
async def get_job(job_id: int):
    return JSONResponse(
        status_code=200,
        content={"id": job_id, "status": "successful", "finished": "2025-10-23T12:00:00Z"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8055)
