# src/modules/hero/api.py
from fastapi import APIRouter, Depends, Query, HTTPException
from src.core.dependencies import get_service
from src.modules.hero.schemas import HeroCreate, HeroRead
from src.modules.hero.service import HeroService
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/heroes", tags=["Heroes"])


@router.post("/", response_model=HeroRead)
async def create_hero(
    data: HeroCreate,
    service: HeroService = Depends(get_service),
):
    logger.info("Creating hero", extra={
        "hero_name": data.name,
        "action": "create_hero"
    })

    try:
        hero = await service.create(data)
        logger.info("Hero created successfully", extra={
            "hero_id":   hero.id,
            "hero_name": hero.name,
            "action":    "create_hero_success"
        })
        return hero

    except Exception as e:
        logger.error("Failed to create hero", extra={
            "hero_name": data.name,
            "error":     str(e),
            "action":    "create_hero_failed"
        })
        raise


@router.get("/", response_model=list[HeroRead])
async def list_heroes(
    service: HeroService = Depends(get_service),
    offset: int = 0,
    limit: int = Query(default=100, le=100),
):
    logger.info("Listing heroes", extra={
        "offset": offset,
        "limit":  limit,
        "action": "list_heroes"
    })

    try:
        heroes = await service.list(offset, limit)
        logger.info("Heroes listed successfully", extra={
            "count":  len(heroes),
            "offset": offset,
            "limit":  limit,
            "action": "list_heroes_success"
        })
        return heroes

    except Exception as e:
        logger.error("Failed to list heroes", extra={
            "error":  str(e),
            "action": "list_heroes_failed"
        })
        raise


@router.get("/{hero_id}", response_model=HeroRead)
async def get_hero(
    hero_id: int,
    service: HeroService = Depends(get_service)
):
    logger.info("Getting hero", extra={
        "hero_id": hero_id,
        "action":  "get_hero"
    })

    try:
        hero = await service.get(hero_id)

        if not hero:
            logger.warning("Hero not found", extra={
                "hero_id": hero_id,
                "action":  "get_hero_not_found"
            })
            raise HTTPException(status_code=404, detail="Hero not found")

        logger.info("Hero found", extra={
            "hero_id":   hero.id,
            "hero_name": hero.name,
            "action":    "get_hero_success"
        })
        return hero

    except HTTPException:
        raise

    except Exception as e:
        logger.error("Failed to get hero", extra={
            "hero_id": hero_id,
            "error":   str(e),
            "action":  "get_hero_failed"
        })
        raise


@router.delete("/{hero_id}")
async def delete_hero(
    hero_id: int,
    service: HeroService = Depends(get_service)
):
    logger.info("Deleting hero", extra={
        "hero_id": hero_id,
        "action":  "delete_hero"
    })

    try:
        result = await service.delete(hero_id)
        logger.info("Hero deleted successfully", extra={
            "hero_id": hero_id,
            "action":  "delete_hero_success"
        })
        return result

    except Exception as e:
        logger.error("Failed to delete hero", extra={
            "hero_id": hero_id,
            "error":   str(e),
            "action":  "delete_hero_failed"
        })
        raise
