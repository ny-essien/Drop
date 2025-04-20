import asyncio
import schedule
import time
from datetime import datetime
from app.db import get_database
from app.monitoring import BackupManager, logger

async def backup_collection(collection_name: str, backup_manager: BackupManager):
    """Backup a single collection"""
    try:
        db = get_database()
        collection = db[collection_name]
        data = await collection.find({}).to_list(length=None)
        
        success = await backup_manager.create_backup(collection_name, data)
        if success:
            logger.info(f"Successfully backed up collection: {collection_name}")
        else:
            logger.error(f"Failed to backup collection: {collection_name}")
    except Exception as e:
        logger.error(f"Error backing up collection {collection_name}: {str(e)}")

async def backup_all_collections():
    """Backup all collections"""
    collections = [
        "users",
        "products",
        "orders",
        "carts",
        "shipping_labels",
        "ml_models"
    ]
    
    backup_manager = BackupManager()
    
    for collection in collections:
        await backup_collection(collection, backup_manager)
    
    logger.info("Completed backup of all collections")

def schedule_backups():
    """Schedule regular backups"""
    # Run full backup daily at midnight
    schedule.every().day.at("00:00").do(
        lambda: asyncio.run(backup_all_collections())
    )
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    logger.info("Starting backup scheduler")
    try:
        schedule_backups()
    except KeyboardInterrupt:
        logger.info("Backup scheduler stopped")
    except Exception as e:
        logger.error(f"Error in backup scheduler: {str(e)}")
        raise 