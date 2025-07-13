#!/usr/bin/env python3
"""
TAIFA Source Validation CLI Tool

Command-line interface for managing source validation operations including
source management, performance monitoring, and administrative tasks.

Usage:
    python -m app.services.source_validation.cli [command] [options]
"""

import asyncio
import click
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
from tabulate import tabulate

# Import source validation components
from app.services.source_validation import (
    SourceValidationOrchestrator,
    SourceValidator,
    PerformanceTracker,
    SourceSubmission,
    SourceStatus
)
from app.services.source_validation.config import get_config, reload_config
from app.core.database import get_database


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def cli(verbose):
    """TAIFA Source Validation CLI Tool"""
    if verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)


@cli.group()
def sources():
    """Manage funding sources"""
    pass


@cli.group()
def performance():
    """Monitor source performance"""
    pass


@cli.group()
def config():
    """Manage configuration"""
    pass


@cli.group()
def submissions():
    """Manage source submissions"""
    pass


# Source management commands
@sources.command()
@click.option('--status', help='Filter by status')
@click.option('--limit', default=50, help='Number of sources to show')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']))
def list(status, limit, output_format):
    """List funding sources"""
    async def _list_sources():
        db = await get_database()
        
        where_clause = ""
        params = [limit]
        
        if status:
            where_clause = "WHERE status = $2"
            params.append(status)
        
        query = f"""
            SELECT id, name, url, source_type, status, created_at, 
                   pilot_mode, reliability_score
            FROM data_sources 
            {where_clause}
            ORDER BY created_at DESC 
            LIMIT $1
        """
        
        sources = await db.fetch_all(query, *params)
        
        if output_format == 'json':
            click.echo(json.dumps([dict(row) for row in sources], indent=2, default=str))
        else:
            headers = ['ID', 'Name', 'URL', 'Type', 'Status', 'Created', 'Pilot', 'Reliability']
            rows = []
            for source in sources:
                rows.append([
                    source['id'],
                    source['name'][:30] + ('...' if len(source['name']) > 30 else ''),
                    source['url'][:40] + ('...' if len(source['url']) > 40 else ''),
                    source['source_type'],
                    source['status'],
                    source['created_at'].strftime('%Y-%m-%d'),
                    'Yes' if source['pilot_mode'] else 'No',
                    f"{source['reliability_score']:.2f}" if source['reliability_score'] else 'N/A'
                ])
            
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
    
    asyncio.run(_list_sources())


@sources.command()
@click.argument('source_id', type=int)
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']))
def show(source_id, output_format):
    """Show detailed information about a source"""
    async def _show_source():
        db = await get_database()
        
        source = await db.fetch_one(
            """
            SELECT ds.*, ss.contact_person, ss.contact_email, ss.geographic_focus
            FROM data_sources ds
            LEFT JOIN source_submissions ss ON ds.submission_id = ss.id
            WHERE ds.id = $1
            """,
            source_id
        )
        
        if not source:
            click.echo(f"Source {source_id} not found", err=True)
            return
        
        if output_format == 'json':
            click.echo(json.dumps(dict(source), indent=2, default=str))
        else:
            click.echo(f"\n{'='*60}")
            click.echo(f"Source ID: {source['id']}")
            click.echo(f"Name: {source['name']}")
            click.echo(f"URL: {source['url']}")
            click.echo(f"Type: {source['source_type']}")
            click.echo(f"Status: {source['status']}")
            click.echo(f"Created: {source['created_at']}")
            click.echo(f"Pilot Mode: {'Yes' if source['pilot_mode'] else 'No'}")
            click.echo(f"Reliability: {source['reliability_score']:.2f}" if source['reliability_score'] else "N/A")
            
            if source['contact_person']:
                click.echo(f"Contact: {source['contact_person']} ({source['contact_email']})")
            
            if source['geographic_focus']:
                click.echo(f"Geographic Focus: {', '.join(source['geographic_focus'])}")
            
            click.echo(f"{'='*60}\n")
    
    asyncio.run(_show_source())


@sources.command()
@click.argument('source_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to disable this source?')
def disable(source_id):
    """Disable a funding source"""
    async def _disable_source():
        db = await get_database()
        
        result = await db.execute(
            "UPDATE data_sources SET status = 'disabled', updated_at = CURRENT_TIMESTAMP WHERE id = $1",
            source_id
        )
        
        if result == "UPDATE 1":
            click.echo(f"Source {source_id} disabled successfully")
        else:
            click.echo(f"Source {source_id} not found", err=True)
    
    asyncio.run(_disable_source())


@sources.command()
@click.argument('source_id', type=int)
def enable(source_id):
    """Enable a disabled funding source"""
    async def _enable_source():
        db = await get_database()
        
        result = await db.execute(
            "UPDATE data_sources SET status = 'active', updated_at = CURRENT_TIMESTAMP WHERE id = $1",
            source_id
        )
        
        if result == "UPDATE 1":
            click.echo(f"Source {source_id} enabled successfully")
        else:
            click.echo(f"Source {source_id} not found", err=True)
    
    asyncio.run(_enable_source())


# Performance monitoring commands
@performance.command()
@click.argument('source_id', type=int)
@click.option('--days', default=30, help='Evaluation period in days')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']))
def evaluate(source_id, days, output_format):
    """Evaluate source performance"""
    async def _evaluate_performance():
        tracker = PerformanceTracker()
        
        try:
            metrics = await tracker.evaluate_source_performance(source_id, days)
            
            if output_format == 'json':
                click.echo(json.dumps(metrics.__dict__, indent=2, default=str))
            else:
                click.echo(f"\n{'='*60}")
                click.echo(f"Performance Report for Source {source_id}")
                click.echo(f"Source: {metrics.source_name}")
                click.echo(f"Evaluation Period: {days} days")
                click.echo(f"{'='*60}")
                
                click.echo(f"\nOverall Performance:")
                click.echo(f"  Score: {metrics.overall_score:.3f}")
                click.echo(f"  Status: {metrics.performance_status.value}")
                
                click.echo(f"\nVolume Metrics:")
                click.echo(f"  Opportunities Discovered: {metrics.opportunities_discovered}")
                click.echo(f"  AI Relevant: {metrics.ai_relevant_count}")
                click.echo(f"  Africa Relevant: {metrics.africa_relevant_count}")
                
                click.echo(f"\nQuality Metrics:")
                click.echo(f"  Community Approval Rate: {metrics.community_approval_rate:.1%}")
                click.echo(f"  Duplicate Rate: {metrics.duplicate_rate:.1%}")
                click.echo(f"  Data Completeness: {metrics.data_completeness_score:.1%}")
                
                click.echo(f"\nTechnical Metrics:")
                click.echo(f"  Monitoring Reliability: {metrics.monitoring_reliability:.1%}")
                click.echo(f"  Processing Error Rate: {metrics.processing_error_rate:.1%}")
                click.echo(f"  Average Response Time: {metrics.average_response_time:.0f}ms")
                
                click.echo(f"\nValue Metrics:")
                click.echo(f"  Unique Opportunities Added: {metrics.unique_opportunities_added}")
                click.echo(f"  High-Value Opportunities: {metrics.high_value_opportunities}")
                click.echo(f"  Successful Applications: {metrics.successful_applications}")
                
                click.echo(f"\nCalculated: {metrics.calculated_at}")
                click.echo(f"{'='*60}\n")
        
        except Exception as e:
            click.echo(f"Error evaluating source performance: {e}", err=True)
    
    asyncio.run(_evaluate_performance())


@performance.command()
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']))
def summary():
    """Show performance summary for all sources"""
    async def _performance_summary():
        tracker = PerformanceTracker()
        
        try:
            summary = await tracker.get_all_sources_performance_summary()
            
            if output_format == 'json':
                click.echo(json.dumps(summary, indent=2, default=str))
            else:
                click.echo(f"\n{'='*60}")
                click.echo("Source Performance Summary")
                click.echo(f"{'='*60}")
                
                click.echo(f"Total Sources: {summary['total_sources']}")
                click.echo(f"Average Score: {summary['average_score']:.3f}")
                click.echo(f"Sources Needing Evaluation: {summary['sources_needing_evaluation']}")
                
                click.echo(f"\nStatus Breakdown:")
                for status, count in summary['status_breakdown'].items():
                    click.echo(f"  {status.title()}: {count}")
                
                if summary['top_performing_sources']:
                    click.echo(f"\nTop Performing Sources:")
                    for source in summary['top_performing_sources']:
                        click.echo(f"  {source['name']}: {source['score']:.3f} ({source['status']})")
                
                click.echo(f"{'='*60}\n")
        
        except Exception as e:
            click.echo(f"Error getting performance summary: {e}", err=True)
    
    asyncio.run(_performance_summary())


@performance.command()
def review_needed():
    """List sources that need performance review"""
    async def _review_needed():
        tracker = PerformanceTracker()
        
        try:
            sources = await tracker.identify_sources_for_review()
            
            if not sources:
                click.echo("No sources need performance review")
                return
            
            headers = ['Source ID', 'Name', 'Last Evaluation', 'Days Since', 'Status', 'Priority', 'Reason']
            rows = []
            
            for source in sources:
                last_eval = source['last_evaluation']
                last_eval_str = last_eval.strftime('%Y-%m-%d') if last_eval else 'Never'
                days_since = source['days_since_evaluation'] if source['days_since_evaluation'] else 'N/A'
                
                rows.append([
                    source['source_id'],
                    source['source_name'][:25] + ('...' if len(source['source_name']) > 25 else ''),
                    last_eval_str,
                    days_since,
                    source['current_status'] or 'Unknown',
                    source['review_priority'],
                    source['reason']
                ])
            
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
        
        except Exception as e:
            click.echo(f"Error identifying sources for review: {e}", err=True)
    
    asyncio.run(_review_needed())


# Configuration commands
@config.command()
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']))
def show(output_format):
    """Show current configuration"""
    async def _show_config():
        config = get_config()
        await config.load_from_database()
        
        config_dict = config.to_dict()
        
        if output_format == 'json':
            click.echo(json.dumps(config_dict, indent=2, default=str))
        else:
            click.echo(f"\n{'='*60}")
            click.echo("Source Validation Configuration")
            click.echo(f"{'='*60}")
            
            for section_name, section_data in config_dict.items():
                click.echo(f"\n{section_name.replace('_', ' ').title()}:")
                for key, value in section_data.items():
                    if isinstance(value, float):
                        click.echo(f"  {key}: {value:.3f}")
                    else:
                        click.echo(f"  {key}: {value}")
            
            click.echo(f"{'='*60}\n")
    
    asyncio.run(_show_config())


@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set configuration value"""
    async def _set_config():
        config = get_config()
        
        # Try to parse value as appropriate type
        try:
            if value.lower() in ('true', 'false'):
                parsed_value = value.lower() == 'true'
            elif '.' in value:
                parsed_value = float(value)
            else:
                parsed_value = int(value)
        except ValueError:
            parsed_value = value
        
        success = await config.update_config(key, parsed_value)
        
        if success:
            click.echo(f"Configuration updated: {key} = {parsed_value}")
        else:
            click.echo(f"Failed to update configuration: {key}", err=True)
    
    asyncio.run(_set_config())


@config.command()
def reload():
    """Reload configuration from database"""
    async def _reload_config():
        await reload_config()
        click.echo("Configuration reloaded from database")
    
    asyncio.run(_reload_config())


# Submission management commands
@submissions.command()
@click.option('--status', help='Filter by status')
@click.option('--limit', default=20, help='Number of submissions to show')
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']))
def list(status, limit, output_format):
    """List source submissions"""
    async def _list_submissions():
        db = await get_database()
        
        where_clause = ""
        params = [limit]
        
        if status:
            where_clause = "WHERE status = $2"
            params.append(status)
        
        query = f"""
            SELECT id, name, url, status, submitted_at, validation_score,
                   contact_person, pilot_id
            FROM source_submissions 
            {where_clause}
            ORDER BY submitted_at DESC 
            LIMIT $1
        """
        
        submissions = await db.fetch_all(query, *params)
        
        if output_format == 'json':
            click.echo(json.dumps([dict(row) for row in submissions], indent=2, default=str))
        else:
            headers = ['ID', 'Name', 'Contact', 'Status', 'Validation Score', 'Submitted', 'Pilot ID']
            rows = []
            
            for sub in submissions:
                rows.append([
                    sub['id'],
                    sub['name'][:25] + ('...' if len(sub['name']) > 25 else ''),
                    sub['contact_person'][:20] + ('...' if len(sub['contact_person']) > 20 else ''),
                    sub['status'],
                    f"{sub['validation_score']:.2f}" if sub['validation_score'] else 'N/A',
                    sub['submitted_at'].strftime('%Y-%m-%d'),
                    sub['pilot_id'] or 'N/A'
                ])
            
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
    
    asyncio.run(_list_submissions())


@submissions.command()
@click.argument('submission_id', type=int)
@click.option('--format', 'output_format', default='table', type=click.Choice(['table', 'json']))
def show(submission_id, output_format):
    """Show detailed submission information"""
    async def _show_submission():
        async with SourceValidationOrchestrator() as orchestrator:
            status = await orchestrator.get_submission_status(submission_id)
            
            if "error" in status:
                click.echo(f"Submission {submission_id} not found", err=True)
                return
            
            if output_format == 'json':
                click.echo(json.dumps(status, indent=2, default=str))
            else:
                click.echo(f"\n{'='*60}")
                click.echo(f"Submission {submission_id} Details")
                click.echo(f"{'='*60}")
                
                for key, value in status.items():
                    if key == 'validation_score' and value:
                        click.echo(f"{key}: {value:.3f}")
                    else:
                        click.echo(f"{key}: {value}")
                
                click.echo(f"{'='*60}\n")
    
    asyncio.run(_show_submission())


@submissions.command()
def review_queue():
    """Show manual review queue"""
    async def _review_queue():
        async with SourceValidationOrchestrator() as orchestrator:
            queue = await orchestrator.get_manual_review_queue()
            
            if not queue:
                click.echo("Manual review queue is empty")
                return
            
            headers = ['Review ID', 'Submission ID', 'Source Name', 'Contact', 'Priority', 'Queued']
            rows = []
            
            for item in queue:
                rows.append([
                    item['id'],
                    item['submission_id'],
                    item['name'][:25] + ('...' if len(item['name']) > 25 else ''),
                    item['contact_person'][:20] + ('...' if len(item['contact_person']) > 20 else ''),
                    item['priority'],
                    item['queued_at'].strftime('%Y-%m-%d %H:%M')
                ])
            
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))
    
    asyncio.run(_review_queue())


# Utility commands
@cli.command()
def health():
    """Check source validation module health"""
    async def _health_check():
        try:
            # Test database connectivity
            db = await get_database()
            submission_count = await db.fetch_val("SELECT COUNT(*) FROM source_submissions")
            source_count = await db.fetch_val("SELECT COUNT(*) FROM data_sources WHERE status = 'active'")
            
            click.echo("✅ Source Validation Module Health Check")
            click.echo(f"Database Connection: OK")
            click.echo(f"Total Submissions: {submission_count}")
            click.echo(f"Active Sources: {source_count}")
            
            # Test configuration
            config = get_config()
            await config.load_from_database()
            click.echo(f"Configuration: OK")
            
        except Exception as e:
            click.echo(f"❌ Health check failed: {e}", err=True)
            sys.exit(1)
    
    asyncio.run(_health_check())


@cli.command()
@click.option('--days', default=7, help='Number of days to analyze')
def stats(days):
    """Show source validation statistics"""
    async def _show_stats():
        async with SourceValidationOrchestrator() as orchestrator:
            analytics = await orchestrator.get_source_validation_analytics(days)
            
            click.echo(f"\n{'='*60}")
            click.echo(f"Source Validation Statistics (Last {days} days)")
            click.echo(f"{'='*60}")
            
            if 'submission_statistics' in analytics:
                stats = analytics['submission_statistics']
                click.echo(f"\nSubmissions:")
                click.echo(f"  Total: {stats.get('total_submissions', 0)}")
                click.echo(f"  Approved: {stats.get('approved', 0)}")
                click.echo(f"  Rejected: {stats.get('rejected', 0)}")
                click.echo(f"  In Pilot: {stats.get('in_pilot', 0)}")
                click.echo(f"  Average Validation Score: {stats.get('avg_validation_score', 0):.3f}")
            
            if 'deduplication_statistics' in analytics:
                dedup_stats = analytics['deduplication_statistics']
                click.echo(f"\nDeduplication:")
                click.echo(f"  Total Checks: {dedup_stats.get('total_checks', 0)}")
                click.echo(f"  Duplicates Found: {dedup_stats.get('duplicates_found', 0)}")
                click.echo(f"  Duplicate Rate: {dedup_stats.get('duplicate_rate', 0):.1%}")
            
            click.echo(f"{'='*60}\n")
    
    asyncio.run(_show_stats())


if __name__ == '__main__':
    cli()
