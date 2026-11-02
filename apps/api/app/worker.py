"""Evaluación periódica opcional. Solo propone; nunca aprueba ni aplica."""

import argparse
import logging
import time
from sqlalchemy import select
from .db import SessionLocal
from .models import Member

logger = logging.getLogger(__name__)


def tick():
    # Importación diferida: reutiliza la misma operación de negocio que la API.
    from .main import run_evaluation

    with SessionLocal() as db:
        members = list(db.scalars(select(Member).where(Member.role == "owner")))
        count = 0
        for member in members:
            try:
                run_evaluation(member, db)
                count += 1
            except Exception:
                db.rollback()
                logger.exception("No se pudo evaluar un espacio de demo")
        return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--interval", type=int, default=900)
    args = parser.parse_args()
    if args.interval < 60:
        parser.error("El intervalo mínimo es 60 segundos")
    logging.basicConfig(level=logging.INFO)
    while True:
        logger.info("Espacios evaluados: %s. Ningún cambio aplicado.", tick())
        if args.once:
            break
        time.sleep(args.interval)
