# main entrypoint
from fastapi import FastAPI
from app.adapters import awx, ev, sn, audit, context, ev, sn, audit, context, auth, llm

app = FastAPI(title="AWX Advanced Tools", description="Orchestration gateway", version="1.0.0")

# Add routers
app.include_router(awx.router)
app.include_router(ev.router)
app.include_router(sn.router)
app.include_router(audit.router)
app.include_router(context.router)
app.include_router(auth.router)
app.include_router(llm.router)

# Root health check
@app.get("/")
async def health():
    return {"status": "running"}
