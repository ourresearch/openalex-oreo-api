import os
import aiohttp
import asyncio
import argparse
from typing import List, Set, Optional
from urllib.parse import quote
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

from app import app, db
from models import Sample
from metrics import id_filter_field, extract_id

OPENALEX_API_KEY = os.getenv("OPENALEX_API_KEY")
OPENALEX_BASE = "https://api.openalex.org"
PER_PAGE = 100

headers = {'Authorization': f'Bearer {OPENALEX_API_KEY}'}


async def _fetch_json(session: aiohttp.ClientSession, url: str, params: Optional[dict] = None) -> dict:
    """Minimal GET wrapper with sane timeout and basic error handling."""
    timeout = aiohttp.ClientTimeout(total=30)  # adjust if you like
    async with session.get(url, params=params, timeout=timeout) as resp:
        if resp.status != 200:
            text = await resp.text()
            full_url = url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
            raise RuntimeError(f"OpenAlex request failed: {full_url} ({resp.status}): {text[:300]}")
        return await resp.json()


async def _fetch_random_sample(
    session: aiohttp.ClientSession,
    entity_type: str,
    sample_type: str,
    sample_scope: str,
) -> List[str]:
    """
    Fetch one page of random sample IDs for the given entity_type.
    Applies post-filtering for 'prod-only', 'walden-only', and 'both'.
    """
    # Decide which "side" to sample from
    # - 'prod' and 'prod-only' and 'both' sample from Prod (no data-version)
    # - 'walden' and 'walden-only' sample from Walden (data-version=2)
    url = f"{OPENALEX_BASE}/{entity_type}"
    params = {
        "sample": PER_PAGE,
        "per_page": PER_PAGE,
    }
    if sample_type in {"walden", "walden-only"}:
        params["data-version"] = "2"
    else:
        params["data-version"] = "1"

    if sample_scope == "last-week":
        last_week_str = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        params["filter"] = f"from_created_date:{last_week_str}"

    data = await _fetch_json(session, url, params=params)
    raw_ids = [extract_id(item["id"]) for item in data.get("results", [])]

    # Post-filtering based on presence/absence in the opposite index
    if sample_type == "walden-only":
        # keep IDs that DO NOT exist in Prod
        prod_present = await _ids_present_in(session, entity_type, raw_ids, walden=False)
        return [i for i in raw_ids if i not in prod_present]

    if sample_type == "prod-only":
        # keep IDs that DO NOT exist in Walden
        walden_present = await _ids_present_in(session, entity_type, raw_ids, walden=True)
        return [i for i in raw_ids if i not in walden_present]

    if sample_type == "both":
        # keep IDs that DO exist in Walden
        walden_present = await _ids_present_in(session, entity_type, raw_ids, walden=True)
        return [i for i in raw_ids if i in walden_present]

    # 'prod' or 'walden' -> no post filtering
    return raw_ids


async def _ids_present_in(
    session: aiohttp.ClientSession,
    entity_type: str,
    ids: List[str],
    *,
    walden: bool,
) -> Set[str]:
    """
    Return the subset of `ids` that are present in the target side
    (walden=True -> data-version=2, walden=False -> prod).
    """
    if not ids:
        return set()

    url = f"{OPENALEX_BASE}/{entity_type}"
    short_ids = [id.split("/")[-1] if "/" in id else id for id in ids]
    filter_value = "|".join(short_ids)
    id_field = id_filter_field(entity_type)
    params = {
        "filter": f"{id_field}:{filter_value}",
        "select": "id",
        "per_page": PER_PAGE,
    }
    if walden:
        params["data-version"] = "2"
    else:
        params["data-version"] = "1"

    data = await _fetch_json(session, url, params=params)
    return {extract_id(item["id"]) for item in data.get("results", [])}


async def build_sample(
    entity_type: str,
    sample_size: int,
    sample_type: str,
    sample_scope: str,
) -> List[str]:
    """
    sample_type:
      - 'prod'         : sample from Prod only (no post-filter)
      - 'walden'       : sample from Walden only (no post-filter)
      - 'prod-only'    : sample from Prod, then remove IDs that exist in Walden
      - 'walden-only'  : sample from Walden, then remove IDs that exist in Prod
      - 'both'         : sample from Prod, keep only IDs that also exist in Walden
    """
    if sample_type not in {"prod", "walden", "prod-only", "walden-only", "both"}:
        raise ValueError("sample_type must be one of: 'prod', 'walden', 'prod-only', 'walden-only', 'both'")

    sample_ids: List[str] = []
    seen: Set[str] = set()

    async with aiohttp.ClientSession(headers=headers) as session:
        while len(sample_ids) < sample_size:
            new_ids = await _fetch_random_sample(session, entity_type, sample_type, sample_scope)
            prev_count = len(seen)
            for _id in new_ids:
                if _id not in seen:
                    seen.add(_id)
                    sample_ids.append(_id)
                    if len(sample_ids) >= sample_size:
                        break

            new_count = len(seen)
            print(f"\rBuilding {entity_type} - {sample_type}: {new_count} / {sample_size}", end="", flush=True)

    return sample_ids[:sample_size]


def save_sample(sample_name, entity_type, sample_type, sample_scope, ids):
    with app.app_context():
        try:
            date_obj = datetime.now()
            
            # Create the Sample object
            sample = Sample(
                name=sample_name,
                entity=entity_type,
                type=sample_type,
                scope=sample_scope,
                date=date_obj,
                ids=ids
            )
            
            # Check if a sample with this name already exists
            existing_sample = Sample.query.filter_by(name=sample_name).first()
            
            if existing_sample:
                # Update existing sample
                existing_sample.entity = entity_type
                existing_sample.type = sample_type
                existing_sample.date = date_obj
                existing_sample.ids = ids
                print(f"Updated existing sample: {sample_name}")
            else:
                # Add new sample to session
                db.session.add(sample)
                print(f"Added new sample: {sample_name}")
            
            db.session.commit()
            print(f"\nSuccessfully loaded {sample_name} into the database!")
        except Exception as e:
            print(f"Error committing to database: {e}")
            db.session.rollback()


async def make_sample(sample_name, entity_type, sample_size, sample_type, sample_scope="all", test=False):
    ids = await build_sample(entity_type=entity_type, sample_size=sample_size, sample_type=sample_type, sample_scope=sample_scope)
    print(f"\n{len(ids)} IDs collected: {ids[:10]}")
    if not test:
        save_sample(sample_name, entity_type, sample_type, sample_scope, ids) 


async def main():
    parser = argparse.ArgumentParser(description="Build a sample of OpenAlex entity IDs")
    parser.add_argument("--name", "-n", required=True, 
                       help="Sample name (e.g., AuthorsBoth)")
    parser.add_argument("--entity", "-e", required=True, 
                       help="Entity type (e.g., works, authors, institutions, concepts)")
    parser.add_argument("--size", "-s", type=int, required=True,
                       help="Sample size (number of IDs to collect)")
    parser.add_argument("--type", "-t", required=True,
                       choices=["prod", "walden", "prod-only", "walden-only", "both"],
                       help="Sample type: prod, walden, prod-only, walden-only, or both")
    parser.add_argument("--scope", "-p", default="all",
                       choices=["last-week", "all"],
                       help="Sample scope: last-week, all")
    parser.add_argument("--test", "-x", action="store_true",
                       help="Run in test mode (skip saving to database)")
    
    args = parser.parse_args()
    
    await make_sample(args.name, args.entity, args.size, args.type, args.scope, test=args.test)


if __name__ == "__main__":
    asyncio.run(main())