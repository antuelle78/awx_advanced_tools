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

@app.get("/api/v2/job_templates/{template_id}/schedules/")
async def list_schedules(template_id: int):
    return JSONResponse(
        status_code=200,
        content={
            "count": 1,
            "results": [
                {"id": 30, "name": "Test Schedule", "enabled": True, "rrule": "DTSTART:20251024T120000Z RRULE:FREQ=DAILY;INTERVAL=1"}
            ]
        }
    )

@app.patch("/api/v2/schedules/{schedule_id}/")
async def toggle_schedule(schedule_id: int, request: Request):
    data = await request.json()
    return JSONResponse(
        status_code=200,
        content={"id": schedule_id, "name": "Test Schedule", "enabled": data.get("enabled")}
    )

@app.delete("/api/v2/schedules/{schedule_id}/")
async def delete_schedule(schedule_id: int):
    return JSONResponse(status_code=204)

@app.post("/api/v2/schedules/")
async def create_schedule(request: Request):
    data = await request.json()
    return JSONResponse(
        status_code=201,
        content={
            "id": 77,
            "name": data.get("name"),
            "rrule": data.get("rrule"),
            "summary_fields": {
                "unified_job_template": {
                    "id": data.get("unified_job_template"),
                    "name": "Mock Job Template"
                }
            }
        }
    )

@app.get("/api/v2/job_templates/")
async def list_templates():
    return JSONResponse(status_code=200, content={"count": 1, "results": [{"id": 1, "name": "Mock Template"}]})

@app.get("/api/v2/jobs/")
async def list_jobs(request: Request):
    return JSONResponse(status_code=200, content={"count": 1, "results": [{"id": 123, "status": "successful"}]})

@app.get("/api/v2/schedules/{schedule_id}/")
async def get_schedule(schedule_id: int):
    return JSONResponse(status_code=200, content={"id": schedule_id, "name": "Test Schedule", "enabled": True})

@app.get("/api/v2/inventories/")
async def list_inventories():
    return JSONResponse(status_code=200, content={"count": 1, "results": [{"id": 456, "name": "Test Inventory"}]})

@app.get("/api/v2/inventories/{inventory_id}/")
async def get_inventory(inventory_id: int):
    return JSONResponse(status_code=200, content={"id": inventory_id, "name": "Test Inventory"})

@app.delete("/api/v2/inventories/{inventory_id}/")
async def delete_inventory(inventory_id: int):
    return JSONResponse(status_code=204)

@app.post("/api/v2/inventories/{inventory_id}/sync/")
async def sync_inventory(inventory_id: int):
    return JSONResponse(status_code=202, content={"status": "syncing"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8055)
