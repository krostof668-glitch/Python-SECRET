import asyncio
import datetime
import logging
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# 1. CONFIGURE SERVER LOGGING
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s | [%(threadName)s] | %(levelname)s | %(message)s', 
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("server_workers")


# -------------------------------------------------------------
# 2. HEAVY ON-DEMAND BACKGROUND WORKERS (Async Tasks)
# -------------------------------------------------------------
async def process_heavy_user_report(user_id: int, report_type: str):
    """Simulates an on-demand task pulled from an API request."""
    logger.info(f"Worker started: Compiling {report_type} for User ID {user_id}...")
    
    # Simulate high computation or file processing without blocking the server thread
    await asyncio.sleep(3) 
    
    logger.info(f"Worker complete: {report_type} generated and dispatched for User ID {user_id}.")


async def dispatch_system_email(recipient_email: str, subject: str):
    """Simulates sending transactional emails out via SMTP servers."""
    logger.info(f"Email Engine: Enqueuing outbound email to {recipient_email}")
    await asyncio.sleep(1)
    logger.info(f"Email Engine: Message successfully routed to {recipient_email}.")


# -------------------------------------------------------------
# 3. CRON-LIKE RECURRING SYSTEM MAINTENANCE TASKS
# -------------------------------------------------------------
async def scheduled_database_cleanup():
    """System job triggered on a recurring schedule to scrub loose frames."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.warning(f"Maintenance Cron: Starting log purge loop at {timestamp}...")
    await asyncio.sleep(1.5)
    logger.info("Maintenance Cron: Database rows optimized, expired sessions deleted.")


# -------------------------------------------------------------
# 4. MAIN SERVER LIFECYCLE CONTROLLER
# -------------------------------------------------------------
async def main_server_loop():
    logger.info("Server Initialization: Launching network layers...")

    # A. Setup and start the Cron Scheduler
    scheduler = AsyncIOScheduler()
    # Runs the cleanup function automatically every 5 seconds
    scheduler.add_job(scheduled_database_cleanup, 'interval', seconds=5)
    scheduler.start()
    logger.info("Server Scheduler: Cron engine successfully attached.")

    # B. Simulate a live API Server listening for client connections
    try:
        count = 0
        while count < 3:
            count += 1
            logger.info(f"Server Core: Base loops humming normally (Tick #{count}). Listening for user payloads...")
            await asyncio.sleep(2)
            
            # Simulate a user hitting a login/registration API endpoint
            if count == 1:
                logger.info("API Endpoint: User hit registration gateway.")
                # Fire-and-forget: we do NOT 'await' this right here.
                # It spawns instantly as a detached background routine.
                asyncio.create_task(dispatch_system_email("dev@server.com", "Welcome onboard!"))

            # Simulate a user requesting a large export payload
            if count == 2:
                logger.info("API Endpoint: User requested a 12-month transaction payload.")
                # Hand off task dynamically to background thread management
                asyncio.create_task(process_heavy_user_report(user_id=8402, report_type="Financial_Audit_2026"))

        # Allow time for lingering background queues to print output logs cleanly before stopping simulation
        logger.info("Server Core: Shutting down listening loops. Draining workers...")
        await asyncio.sleep(6)
        
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        scheduler.shutdown()
        logger.info("Server Engine: Stopped successfully.")


if __name__ == "__main__":
    # Launch the asynchronous loop runtime context
    asyncio.run(main_server_loop())
