#!/usr/bin/env python3
"""
InfoSentry-CLI: Command Line Interface
"""

import sys
import argparse
import json
from pathlib import Path
from typing import Optional

from .core.engine import InfoEngine
from .core.config import Config
from .ui.formatter import OutputFormatter
from .ui.dashboard import Dashboard


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog='infosentry',
        description='🛡️ InfoSentry-CLI: Lightweight Open Source Intelligence Aggregation & Analysis Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  infosentry fetch                    # Fetch all intelligence data
  infosentry fetch --source earthquake # Fetch only earthquake data
  infosentry dashboard                # Launch real-time dashboard
  infosentry analyze                  # Fetch and analyze data
  infosentry export --format json     # Export data as JSON
  infosentry export --format csv      # Export data as CSV
  infosentry export --format markdown # Export as Markdown report
        '''
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch intelligence data')
    fetch_parser.add_argument(
        '--source',
        type=str,
        choices=['earthquake', 'aviation', 'weather', 'spacex', 'cve'],
        help='Fetch from specific source only'
    )
    fetch_parser.add_argument(
        '--severity',
        type=str,
        choices=['critical', 'high', 'medium', 'low', 'info'],
        help='Filter by severity level'
    )
    fetch_parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum number of items to display (default: 50)'
    )
    fetch_parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Bypass cache and fetch fresh data'
    )
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Launch real-time dashboard')
    dashboard_parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Refresh interval in seconds (default: 60)'
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Fetch and analyze data for patterns')
    analyze_parser.add_argument(
        '--correlations',
        action='store_true',
        help='Show correlations between events'
    )
    analyze_parser.add_argument(
        '--patterns',
        action='store_true',
        help='Show pattern analysis'
    )
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data to file')
    export_parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'csv', 'markdown'],
        default='json',
        help='Export format (default: json)'
    )
    export_parser.add_argument(
        '--output',
        type=str,
        help='Output file path'
    )
    
    # Sources command
    sources_parser = subparsers.add_parser('sources', help='List available data sources')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_parser.add_argument(
        '--set',
        nargs=2,
        metavar=('KEY', 'VALUE'),
        help='Set configuration value'
    )
    config_parser.add_argument(
        '--get',
        type=str,
        metavar='KEY',
        help='Get configuration value'
    )
    config_parser.add_argument(
        '--list',
        action='store_true',
        help='List all configuration'
    )
    
    # Cache command
    cache_parser = subparsers.add_parser('cache', help='Manage cache')
    cache_parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear all cached data'
    )
    
    return parser


def cmd_fetch(args, engine: InfoEngine, formatter: OutputFormatter):
    """Handle fetch command"""
    use_cache = not args.no_cache
    
    if args.source:
        items = engine.fetch_source(args.source)
    else:
        items = engine.fetch_all(use_cache=use_cache)
    
    # Apply filters
    if args.severity:
        items = [i for i in items if i.get('severity') == args.severity]
    
    # Apply limit
    items = items[:args.limit]
    
    # Display
    if items:
        print(formatter.format_list(items, compact=False))
        print()
        stats = engine.get_stats(items)
        print(formatter.colorize(f"📊 Fetched {stats['total']} items from {len(stats['by_source'])} sources", 'dim'))
    else:
        print(formatter.colorize("No data available.", 'dim'))


def cmd_dashboard(args, engine: InfoEngine, formatter: OutputFormatter):
    """Handle dashboard command"""
    def fetch_callback():
        items = engine.fetch_all(use_cache=True)
        analysis = engine.analyze(items)
        return items, analysis['correlations'], analysis['patterns']
    
    dashboard = Dashboard(refresh_interval=args.interval)
    dashboard.run(fetch_callback)


def cmd_analyze(args, engine: InfoEngine, formatter: OutputFormatter):
    """Handle analyze command"""
    items = engine.fetch_all()
    analysis = engine.analyze(items)
    
    # Display summary
    print(formatter.format_summary(items, analysis['correlations'], analysis['patterns']))
    
    # Display correlations if requested
    if args.correlations and analysis['correlations']:
        print()
        print(formatter.colorize("🔗 DETAILED CORRELATIONS", 'bold'))
        for corr in analysis['correlations']:
            print(f"  Type: {corr.get('type')}")
            print(f"  Description: {corr.get('description')}")
            print(f"  Confidence: {corr.get('confidence', 0) * 100:.1f}%")
            print()
    
    # Display patterns if requested
    if args.patterns and analysis['patterns']:
        print()
        print(formatter.colorize("🔍 DETAILED PATTERNS", 'bold'))
        for pattern in analysis['patterns']:
            print(f"  Type: {pattern.get('type')}")
            print(f"  Description: {pattern.get('description')}")
            if 'data' in pattern:
                print(f"  Data: {json.dumps(pattern['data'], indent=4)[:200]}...")
            print()


def cmd_export(args, engine: InfoEngine, formatter: OutputFormatter):
    """Handle export command"""
    items = engine.fetch_all()
    
    if args.format == 'json':
        output = formatter.format_json(items)
        default_ext = 'json'
    elif args.format == 'csv':
        output = formatter.format_csv(items)
        default_ext = 'csv'
    elif args.format == 'markdown':
        output = formatter.format_markdown(items)
        default_ext = 'md'
    else:
        print(formatter.colorize(f"Unknown format: {args.format}", 'red'))
        return
    
    if args.output:
        output_path = Path(args.output)
    else:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = Path(f'infosentry_export_{timestamp}.{default_ext}')
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
        print(formatter.colorize(f"✅ Exported {len(items)} items to {output_path}", 'green'))
    except IOError as e:
        print(formatter.colorize(f"❌ Export failed: {e}", 'red'))


def cmd_sources(args, engine: InfoEngine, formatter: OutputFormatter):
    """Handle sources command"""
    sources = engine.get_source_info()
    
    print(formatter.colorize("📡 AVAILABLE DATA SOURCES", 'bold'))
    print(formatter.colorize("═" * 60, 'dim'))
    print()
    
    for source in sources:
        status = "✅" if source.get('enabled') else "❌"
        name = source.get('name', 'unknown')
        description = source.get('description', '')
        url = source.get('url', '')
        
        print(f"{status} {formatter.colorize(name.upper(), 'cyan')}")
        print(f"   {description}")
        print(f"   URL: {formatter.colorize(url, 'dim')}")
        print()


def cmd_config(args, config: Config, formatter: OutputFormatter):
    """Handle config command"""
    if args.set:
        key, value = args.set
        config.set(key, value)
        config.save()
        print(formatter.colorize(f"✅ Set {key} = {value}", 'green'))
    
    elif args.get:
        value = config.get(args.get)
        if value is not None:
            print(f"{args.get} = {value}")
        else:
            print(formatter.colorize(f"Key '{args.get}' not found", 'red'))
    
    elif args.list:
        import json
        print(json.dumps(config._config, indent=2))
    
    else:
        print(formatter.colorize("Use --set, --get, or --list", 'dim'))


def cmd_cache(args, engine: InfoEngine, formatter: OutputFormatter):
    """Handle cache command"""
    if args.clear:
        engine.clear_cache()
        print(formatter.colorize("✅ Cache cleared", 'green'))
    else:
        print(formatter.colorize("Use --clear to clear cache", 'dim'))


def main() -> int:
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Initialize components
    config = Config()
    engine = InfoEngine(config)
    formatter = OutputFormatter(use_colors=not args.no_color)
    
    # Route commands
    try:
        if args.command == 'fetch':
            cmd_fetch(args, engine, formatter)
        elif args.command == 'dashboard':
            cmd_dashboard(args, engine, formatter)
        elif args.command == 'analyze':
            cmd_analyze(args, engine, formatter)
        elif args.command == 'export':
            cmd_export(args, engine, formatter)
        elif args.command == 'sources':
            cmd_sources(args, engine, formatter)
        elif args.command == 'config':
            cmd_config(args, config, formatter)
        elif args.command == 'cache':
            cmd_cache(args, engine, formatter)
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print()
        print(formatter.colorize("\n👋 Interrupted by user", 'dim'))
        return 130
    except Exception as e:
        print(formatter.colorize(f"\n❌ Error: {e}", 'red'))
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
