#!/usr/bin/env python3
"""
Script to clean up orphaned resources.

This script identifies and removes resources that may have been left behind
due to failed operations or incomplete cleanup procedures.

Usage:
    python scripts/cleanup_orphaned_resources.py --confirm
    python scripts/cleanup_orphaned_resources.py --help
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.aws_config import AWSConfig
from src.cleanup_manager import ResourceCleanupManager
from src.knowledge_base_manager import BedrockKnowledgeBase
from src.s3_manager import S3Manager
from src.iam_manager import IAMManager
from src.vector_store import VectorIndexManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for orphaned resource cleanup script."""
    parser = argparse.ArgumentParser(
        description="Clean up orphaned resources left behind by failed operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan for and clean up orphaned resources
  python scripts/cleanup_orphaned_resources.py --confirm

  # Dry run (list orphaned resources without deleting)
  python scripts/cleanup_orphaned_resources.py --dry-run

  # Clean up with verbose logging
  python scripts/cleanup_orphaned_resources.py --confirm --verbose

  # Use specific AWS profile
  python scripts/cleanup_orphaned_resources.py --confirm --profile my-profile
        """
    )

    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm deletion of orphaned resources (required for actual deletion)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List orphaned resources without actually deleting them"
    )

    parser.add_argument(
        "--region",
        help="AWS region (defaults to configured region)"
    )

    parser.add_argument(
        "--profile",
        help="AWS profile to use"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Initialize AWS config
        logger.info("Initializing AWS configuration...")
        aws_config = AWSConfig(region=args.region, profile=args.profile)

        # Initialize managers
        logger.info("Initializing resource managers...")
        kb_manager = BedrockKnowledgeBase(aws_config)
        s3_manager = S3Manager(aws_config)
        iam_manager = IAMManager(aws_config)
        vector_store_manager = VectorIndexManager(aws_config)
        cleanup_manager = ResourceCleanupManager(aws_config)

        # Perform cleanup
        if args.dry_run:
            logger.info("DRY RUN: Scanning for orphaned resources")
            logger.info("No resources will be deleted in dry-run mode")

            # Scan for failed knowledge bases
            try:
                kbs = kb_manager.list_knowledge_bases()
                failed_kbs = []
                for kb in kbs:
                    try:
                        kb_info = kb_manager.get_knowledge_base(kb.get("kb_id"))
                        if kb_info.get("status") == "FAILED":
                            failed_kbs.append(kb)
                    except Exception as e:
                        logger.debug(f"Could not check KB {kb.get('kb_id')}: {str(e)}")

                if failed_kbs:
                    logger.info(f"Found {len(failed_kbs)} failed knowledge bases:")
                    for kb in failed_kbs:
                        logger.info(f"  - {kb.get('kb_name')} (ID: {kb.get('kb_id')}, Status: FAILED)")
                else:
                    logger.info("No failed knowledge bases found")
            except Exception as e:
                logger.error(f"Failed to scan for orphaned KBs: {str(e)}")

        else:
            if not args.confirm:
                logger.error("ERROR: --confirm flag is required to delete resources")
                logger.error("Use --dry-run to preview orphaned resources")
                sys.exit(1)

            logger.warning("=" * 60)
            logger.warning("CLEANING UP ORPHANED RESOURCES")
            logger.warning("=" * 60)

            # Perform cleanup
            cleanup_results = cleanup_manager.cleanup_orphaned_resources(
                kb_manager=kb_manager,
                s3_manager=s3_manager,
                iam_manager=iam_manager,
                vector_store_manager=vector_store_manager,
                confirm=True
            )

            # Print report
            report = cleanup_manager.generate_cleanup_report(cleanup_results)
            logger.info(report)

            # Exit with error if there were errors
            if cleanup_results.get("errors"):
                logger.error(f"Cleanup completed with {len(cleanup_results['errors'])} errors")
                sys.exit(1)
            else:
                logger.info("Cleanup completed successfully")
                sys.exit(0)

    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
