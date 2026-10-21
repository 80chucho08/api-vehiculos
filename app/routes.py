from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app import services

router = APIRouter()


@router.get("/health", tags=["salud"])
def health(request: Request):
    return {"status": "ok", "service": request.app.state.settings.app_name}


@router.get("/health/db", tags=["salud"])
def database_health(request: Request):
    try:
        services.check_database(request.app.state.settings)
        return {"status": "ok", "database": "connected"}
    except services.DatabaseUnavailable as exc:
        return JSONResponse(status_code=503, content={"status": "error", "database": "unavailable", "detail": str(exc)})


@router.get("/api/automoviles", tags=["automóviles"])
def automoviles(request: Request):
    try:
        return services.get_automoviles(request.app.state.settings)
    except services.DatabaseUnavailable as exc:
        return JSONResponse(status_code=503, content={"error": "database_unavailable", "detail": str(exc)})
    except services.ProcedureNotFound as exc:
        return JSONResponse(status_code=502, content={"error": "procedure_not_found", "detail": str(exc)})
    except services.DatabaseQueryError as exc:
        return JSONResponse(status_code=500, content={"error": "database_query_failed", "detail": str(exc)})
