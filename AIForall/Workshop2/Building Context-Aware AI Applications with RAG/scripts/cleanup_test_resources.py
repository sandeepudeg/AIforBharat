#!/usr/bin/env python3
"""
Script to clean up test resources created during testing.

This script identifies and removes resources created for testing purposes,
including test knowledge bases, S3 buckets, and IAM roles.

Usage:
    python scripts/cleanup_test_resources.py --prefix test- --confirm
    python scripts/cleanup_test_resources.py --help
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
    """Main entry point for cleanup script."""
    parser = argparse.ArgumentParser(
        description="Clean up test resources created during testing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Clean up test resources with default prefix
  python scripts/cleanup_test_resources.py --confirm

  # Clean up resources with custom prefix
  python scripts/cleanup_test_resources.py --prefix my-test- --confirm

  # Dry run (list resources without deleting)
  python scripts/cleanup_test_resources.py --prefix test- --dry-run

  # Clean up and delete S3 buckets
  python scripts/cleanup_test_resources.py --confirm --delete-s3

  # Clean up and delete IAM roles
  python scripts/cleanup_test_resources.py --confirm --delete-iam
        """
    )

    parser.add_argument(
        "--prefix",
        default="test-",
        help="Prefix used to identify test resources (default: test-)"
    )

    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Confirm deletion of resources (required for actual deletion)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List resources that would be deleted without actually deleting them"
    )

    parser.add_argument(
        "--delete-s3",
        action="store_true",
        help="Also delete S3 buckets (use with caution)"
    )

    parser.add_argument(
        "--delete-iam",
        action="store_true",
        help="Also delete IAM roles and policies (use with caution)"
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
            logger.info(f"DRY RUN: Listing test resources with prefix '{args.prefix}'")
            logger.info("No resources will be deleted in dry-run mode")

            # List test knowledge bases
            try:
                kbs = kb_manager.list_knowledge_bases()
                test_kbs = [kb for kb in kbs if kb.get("kb_name", "").startswith(args.prefix)]
                if test_kbs:
                    logger.info(f"Found {len(test_kbs)} test knowledge bases:")
                    for kb in test_kbs:
                        logger.info(f"  - {kb.get('kb_name')} (ID: {kb.get('kb_id')})")
                else:
                    logger.info("No test knowledge bases found")
            except Exception as e:
                logger.error(f"Failed to list knowledge bases: {str(e)}")

        else:
            if not args.confirm:
                logger.error("ERROR: --confirm flag is required to delete resources")
                logger.error("Use --dry-run to preview resources that would be deleted")
                sys.exit(1)

            logger.warning("=" * 60)
            logger.warning("DELETING TEST RESOURCES")
            logger.warning("=" * 60)

            # Perform cleanup
            cleanup_results = cleanup_manager.cleanup_test_resources(
                test_prefix=args.prefix,
                kb_manager=kb_manager,
                s3_manager=s3_manager if args.delete_s3 else None,
                iam_manager=iam_manager if args.delete_iam else None,
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
